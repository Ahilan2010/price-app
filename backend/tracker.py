# backend/tracker.py
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

from playwright.async_api import async_playwright


class StorenvyPriceTracker:
    def __init__(self, db_path: str = "storenvy_tracker.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self) -> None:
        """Initialize SQLite database for storing tracked products."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tracked_products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                title TEXT,
                target_price REAL NOT NULL,
                last_price REAL,
                last_checked TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
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
        
        try:
            cursor.execute('''
                INSERT INTO tracked_products (url, target_price)
                VALUES (?, ?)
            ''', (url, target_price))
            conn.commit()
        except sqlite3.IntegrityError:
            cursor.execute('''
                UPDATE tracked_products
                SET target_price = ?
                WHERE url = ?
            ''', (target_price, url))
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
            SELECT id, url, title, target_price, last_price, last_checked
            FROM tracked_products
            ORDER BY created_at DESC
        ''')
        
        products: List[Dict[str, any]] = []
        for row in cursor.fetchall():
            products.append({
                'id': row[0],
                'url': row[1],
                'title': row[2],
                'target_price': row[3],
                'last_price': row[4],
                'last_checked': row[5],
                'status': 'below_target' if row[4] and row[4] <= row[3] else 'waiting'
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
    
    async def scrape_storenvy_product(self, url: str) -> Optional[Tuple[str, float]]:
        """Scrape product title and price from a Storenvy product URL."""
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--disable-blink-features=AutomationControlled']
            )

            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                timezone_id='America/New_York'
            )

            page = await context.new_page()

            try:
                await asyncio.sleep(2)
                await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                await page.wait_for_timeout(3000)

                # Extract title
                title = "Unknown Product"
                title_selectors = [
                    'h1.product-name',
                    'h1.product_name',
                    'h1[itemprop="name"]',
                    '.product-header h1',
                    '.product_name',
                    'h1'
                ]
                
                for selector in title_selectors:
                    try:
                        element = await page.wait_for_selector(selector, timeout=2000)
                        if element:
                            title_text = await element.text_content()
                            if title_text:
                                title = title_text.strip()
                                break
                    except Exception:
                        continue

                # Extract price
                price = None
                price_selectors = [
                    'div.price.vprice[itemprop="price"]',
                    'div.price.vprice',
                    'div[itemprop="price"]',
                    '.price.vprice',
                    'span.product-price',
                    '.product-price',
                    'span.price:not(.sale-price):not(.discount-price)'
                ]

                for selector in price_selectors:
                    try:
                        element = await page.wait_for_selector(selector, timeout=2000)
                        if element:
                            price_text = await element.text_content()
                            if price_text and ('$' in price_text or re.search(r'\d+\.?\d*', price_text)):
                                price_text = price_text.strip().replace('$', '').replace(',', '')
                                price_match = re.search(r'(\d+(?:\.\d{1,2})?)', price_text)
                                if price_match:
                                    price = float(price_match.group(1))
                                    if price > 0:
                                        break
                    except Exception:
                        continue

                if price is None:
                    return None

                return title, price

            except Exception as e:
                print(f"Error scraping {url}: {str(e)}")
                return None

            finally:
                await browser.close()

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
        
        for product in products:
            result = await self.scrape_storenvy_product(product['url'])
            
            if result:
                title, current_price = result
                self.update_product_info(product['id'], title, current_price)
                
                if current_price <= product['target_price']:
                    product['title'] = title
                    product['last_price'] = current_price
                    
                    if smtp_config:
                        self.send_email_alert(product, smtp_config)
            
            await asyncio.sleep(3)