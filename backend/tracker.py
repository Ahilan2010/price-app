# backend/tracker.py - Updated with multi-platform support
import asyncio
import json
import re
import smtplib
import sqlite3
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from multi_platform_scraper import MultiPlatformScraper


class StorenvyPriceTracker:
    def __init__(self, db_path: str = "storenvy_tracker.db"):
        self.db_path = db_path
        self.scraper = MultiPlatformScraper()
        self.init_database()
        
    def init_database(self) -> None:
        """Initialize SQLite database for storing tracked products."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update the table to include platform information
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tracked_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                platform TEXT,
                title TEXT,
                target_price REAL NOT NULL,
                last_price REAL,
                last_checked TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Check if platform column exists, if not add it
        cursor.execute("PRAGMA table_info(tracked_products)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'platform' not in columns:
            cursor.execute('ALTER TABLE tracked_products ADD COLUMN platform TEXT')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                price REAL,
                checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES tracked_products (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_product(self, url: str, target_price: float) -> None:
        """Add a product to track."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Detect platform
        platform = self.scraper.detect_platform(url)
        if not platform:
            raise ValueError("Unsupported e-commerce platform")
        
        try:
            cursor.execute('''
                INSERT INTO tracked_products (url, platform, target_price)
                VALUES (?, ?, ?)
            ''', (url, platform, target_price))
            conn.commit()
        except sqlite3.IntegrityError:
            cursor.execute('''
                UPDATE tracked_products
                SET target_price = ?, platform = ?
                WHERE url = ?
            ''', (target_price, platform, url))
            conn.commit()
        
        conn.close()
    
    def delete_product(self, product_id: int) -> None:
        """Delete a tracked product."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete price history first
        cursor.execute('DELETE FROM price_history WHERE product_id = ?', (product_id,))
        # Delete product
        cursor.execute('DELETE FROM tracked_products WHERE id = ?', (product_id,))
        
        conn.commit()
        conn.close()
    
    def get_tracked_products(self) -> List[Dict[str, any]]:
        """Get all tracked products from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, url, platform, title, target_price, last_price, last_checked
            FROM tracked_products
            ORDER BY created_at DESC
        ''')
        
        products: List[Dict[str, any]] = []
        platform_info = MultiPlatformScraper.get_platform_info()
        
        for row in cursor.fetchall():
            platform = row[2] or 'storenvy'  # Default to storenvy for backward compatibility
            platform_details = platform_info.get(platform, {'name': 'Unknown', 'icon': '🛒'})
            
            products.append({
                'id': row[0],
                'url': row[1],
                'platform': platform,
                'platform_name': platform_details['name'],
                'platform_icon': platform_details['icon'],
                'title': row[3],
                'target_price': row[4],
                'last_price': row[5],
                'last_checked': row[6],
                'status': 'below_target' if row[5] and row[5] <= row[4] else 'waiting'
            })
        
        conn.close()
        return products
    
    def update_product_info(self, product_id: int, title: str, price: float) -> None:
        """Update product information after scraping."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE tracked_products
            SET title = ?, last_price = ?, last_checked = ?
            WHERE id = ?
        ''', (title, price, datetime.now(), product_id))
        
        cursor.execute('''
            INSERT INTO price_history (product_id, price)
            VALUES (?, ?)
        ''', (product_id, price))
        
        conn.commit()
        conn.close()
    
    async def scrape_product(self, url: str) -> Optional[Tuple[str, float]]:
        """Scrape product using the multi-platform scraper"""
        return await self.scraper.scrape_product(url)
    
    def send_email_alert(self, product: Dict[str, any], smtp_config: Dict[str, any]) -> None:
        """Send email alert for price drop."""
        if not smtp_config.get('enabled'):
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_config['from_email']
            msg['To'] = smtp_config['to_email']
            msg['Subject'] = f"Price Drop Alert: {product['title'][:50]}..."
            
            body = f"""
            Great news! A product you're tracking has dropped to or below your target price!
            
            Platform: {product['platform_icon']} {product['platform_name']}
            Product: {product['title']}
            Current Price: ${product['last_price']:.2f}
            Target Price: ${product['target_price']:.2f}
            Savings: ${product['target_price'] - product['last_price']:.2f}
            
            View Product: {product['url']}
            
            Happy shopping!
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(smtp_config['smtp_server'], smtp_config['smtp_port'])
            server.starttls()
            server.login(smtp_config['from_email'], smtp_config['password'])
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
    
    async def check_all_products(self, smtp_config: Optional[Dict[str, any]] = None) -> None:
        """Check all tracked products for price drops."""
        products = self.get_tracked_products()
        
        if not products:
            return
        
        print(f"Checking {len(products)} products across multiple platforms...")
        
        for product in products:
            try:
                print(f"Checking {product['platform_name']} product: {product['url'][:50]}...")
                result = await self.scrape_product(product['url'])
                
                if result:
                    title, current_price = result
                    self.update_product_info(product['id'], title, current_price)
                    
                    if current_price <= product['target_price']:
                        product['title'] = title
                        product['last_price'] = current_price
                        
                        if smtp_config:
                            self.send_email_alert(product, smtp_config)
                else:
                    print(f"Failed to scrape {product['platform_name']} product")
            
            except Exception as e:
                print(f"Error checking product {product['id']}: {str(e)}")
            
            # Be respectful to servers with random delays
            await asyncio.sleep(3 + (2 * random.random()))
    
    def get_supported_platforms(self) -> Dict[str, Dict[str, str]]:
        """Get information about supported platforms"""
        return MultiPlatformScraper.get_platform_info()


# For backward compatibility, also import random
import random