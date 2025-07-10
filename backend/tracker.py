# backend/tracker.py - Updated with multi-platform support and fixed imports
import asyncio
import json
import re
import smtplib
import sqlite3
import time
import random
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
            
            # Determine currency symbol based on platform
            platform = product.get('platform', 'storenvy')
            platform_info = MultiPlatformScraper.get_platform_info().get(platform, {})
            is_robux = platform == 'roblox'
            
            # Format prices based on currency
            if is_robux:
                current_price_str = f"{int(product['last_price'])} Robux"
                target_price_str = f"{int(product['target_price'])} Robux"
                savings_str = f"{int(product['target_price'] - product['last_price'])} Robux"
            else:
                current_price_str = f"${product['last_price']:.2f}"
                target_price_str = f"${product['target_price']:.2f}"
                savings_str = f"${product['target_price'] - product['last_price']:.2f}"
            
            body = f"""
            Great news! A product you're tracking has dropped to or below your target price!
            
            Platform: {product['platform_icon']} {product['platform_name']}
            Product: {product['title']}
            Current Price: {current_price_str}
            Target Price: {target_price_str}
            Savings: {savings_str}
            
            View Product: {product['url']}
            
            Happy shopping!
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(smtp_config['smtp_server'], smtp_config['smtp_port'])
            server.starttls()
            server.login(smtp_config['from_email'], smtp_config['password'])
            server.send_message(msg)
            server.quit()
            
            print(f"📧 Email alert sent for {product['title']}")
            
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
    
    async def check_all_products(self, smtp_config: Optional[Dict[str, any]] = None) -> None:
        """Check all tracked products for price drops."""
        products = self.get_tracked_products()
        
        if not products:
            print("No products to check")
            return
        
        print(f"🔄 Checking {len(products)} products across multiple platforms...")
        
        for product in products:
            try:
                platform_name = product.get('platform_name', 'Unknown')
                print(f"📦 Checking {platform_name} product: {product['url'][:50]}...")
                
                result = await self.scrape_product(product['url'])
                
                if result:
                    title, current_price = result
                    self.update_product_info(product['id'], title, current_price)
                    
                    print(f"✅ Updated {platform_name} product: {title[:30]}... - Price: {current_price}")
                    
                    # Check if price dropped below target
                    if current_price <= product['target_price']:
                        print(f"🎉 TARGET HIT! {title[:30]}... is now at/below target price!")
                        
                        # Update product info for email
                        product['title'] = title
                        product['last_price'] = current_price
                        
                        if smtp_config:
                            self.send_email_alert(product, smtp_config)
                else:
                    print(f"❌ Failed to scrape {platform_name} product")
            
            except Exception as e:
                print(f"Error checking product {product['id']}: {str(e)}")
            
            # Be respectful to servers with random delays
            delay = 3 + (2 * random.random())
            print(f"⏳ Waiting {delay:.1f}s before next check...")
            await asyncio.sleep(delay)
        
        print("✅ Finished checking all products")
    
    def get_supported_platforms(self) -> Dict[str, Dict[str, str]]:
        """Get information about supported platforms"""
        return MultiPlatformScraper.get_platform_info()


# Test function for development
async def test_tracker():
    """Test function to verify the tracker works with multiple platforms"""
    tracker = StorenvyPriceTracker()
    
    print("Testing Multi-Platform Price Tracker")
    print("=" * 50)
    
    # Test adding products from different platforms
    test_products = [
        ("https://www.amazon.com/dp/B08N5WRWNW", 100.00),  # Amazon
        ("https://www.etsy.com/listing/123456789/test", 25.00),  # Etsy
    ]
    
    for url, target_price in test_products:
        try:
            platform = tracker.scraper.detect_platform(url)
            print(f"\n🎯 Testing {platform} URL: {url}")
            
            # Add product
            tracker.add_product(url, target_price)
            print(f"✅ Added {platform} product with target price ${target_price}")
            
        except Exception as e:
            print(f"❌ Failed to add {url}: {e}")
    
    # Test getting tracked products
    products = tracker.get_tracked_products()
    print(f"\n📋 Currently tracking {len(products)} products:")
    for product in products:
        print(f"  - {product['platform_name']}: {product['url'][:50]}...")

if __name__ == "__main__":
    asyncio.run(test_tracker())