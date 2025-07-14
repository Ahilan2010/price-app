# backend/tracker.py - UPDATED WITH USER SUPPORT AND NO FLIGHTS
import asyncio
import json
import smtplib
import sqlite3
import time
import random
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlparse

from multi_platform_scraper import MultiPlatformScraper


class StorenvyPriceTracker:
    """Multi-platform price tracker for e-commerce and Roblox items"""
    
    def __init__(self, db_path: str = "storenvy_tracker.db"):
        self.db_path = db_path
        self.scraper = MultiPlatformScraper()
        self.init_database()
        
    def init_database(self) -> None:
        """Initialize SQLite database for storing tracked products"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create main products table with user_id
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tracked_products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    url TEXT NOT NULL,
                    platform TEXT,
                    title TEXT,
                    target_price REAL NOT NULL,
                    last_price REAL,
                    last_checked TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id, url)
                )
            ''')
            
            # Check if user_id column exists
            cursor.execute("PRAGMA table_info(tracked_products)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'user_id' not in columns:
                # Migrate existing data
                cursor.execute('ALTER TABLE tracked_products ADD COLUMN user_id INTEGER DEFAULT 1')
                print("Added user_id column to existing database")
            
            # Create price history table
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
            print("Database initialized successfully")
            
        except Exception as e:
            print(f"Error initializing database: {e}")
            raise
    
    def add_product(self, url: str, target_price: float, user_id: int) -> None:
        """Add a product to track for a specific user"""
        try:
            # Detect platform
            platform = self.scraper.detect_platform(url)
            if not platform or platform == 'flights':  # Exclude flights
                raise ValueError("Unsupported e-commerce platform")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                # Try to insert new product
                cursor.execute('''
                    INSERT INTO tracked_products (user_id, url, platform, target_price)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, url, platform, target_price))
                conn.commit()
                print(f"Added new product from {platform}: {url[:50]}...")
                
            except sqlite3.IntegrityError:
                # Update existing product
                cursor.execute('''
                    UPDATE tracked_products
                    SET target_price = ?, platform = ?
                    WHERE user_id = ? AND url = ?
                ''', (target_price, platform, user_id, url))
                conn.commit()
                print(f"Updated existing product from {platform}: {url[:50]}...")
            
            conn.close()
            
        except Exception as e:
            print(f"Error adding product: {e}")
            raise
    
    def delete_product(self, product_id: int, user_id: int) -> None:
        """Delete a tracked product for a specific user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete price history first
            cursor.execute('''
                DELETE FROM price_history 
                WHERE product_id IN (
                    SELECT id FROM tracked_products 
                    WHERE id = ? AND user_id = ?
                )
            ''', (product_id, user_id))
            
            # Delete product
            cursor.execute('DELETE FROM tracked_products WHERE id = ? AND user_id = ?', (product_id, user_id))
            
            conn.commit()
            conn.close()
            print(f"Deleted product {product_id} for user {user_id}")
            
        except Exception as e:
            print(f"Error deleting product {product_id}: {e}")
            raise
    
    def get_tracked_products(self, user_id: int = None) -> List[Dict[str, Any]]:
        """Get all tracked products, optionally filtered by user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute('''
                    SELECT id, url, platform, title, target_price, last_price, last_checked
                    FROM tracked_products
                    WHERE user_id = ? AND platform != 'flights'
                    ORDER BY created_at DESC
                ''', (user_id,))
            else:
                cursor.execute('''
                    SELECT id, url, platform, title, target_price, last_price, last_checked
                    FROM tracked_products
                    WHERE platform != 'flights'
                    ORDER BY created_at DESC
                ''')
            
            products = []
            platform_info = MultiPlatformScraper.get_platform_info()
            
            for row in cursor.fetchall():
                try:
                    platform = row[2] or 'storenvy'
                    if platform == 'flights':  # Skip flights
                        continue
                        
                    platform_details = platform_info.get(platform, {
                        'name': 'Unknown', 
                        'icon': '🛒'
                    })
                    
                    # Determine status
                    status = 'waiting'
                    if row[5] is not None and row[4] is not None:
                        if row[5] <= row[4]:
                            status = 'below_target'
                    
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
                        'status': status
                    })
                    
                except Exception as e:
                    print(f"Error processing product row: {e}")
                    continue
            
            conn.close()
            return products
            
        except Exception as e:
            print(f"Error getting tracked products: {e}")
            return []

    def get_all_products_for_checking(self) -> List[Dict[str, Any]]:
        """Get all products from all users for checking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT p.id, p.user_id, p.url, p.platform, p.title, p.target_price, 
                       p.last_price, p.last_checked, u.email, u.smtp_password, u.first_name
                FROM tracked_products p
                JOIN users u ON p.user_id = u.id
                WHERE p.platform != 'flights'
                ORDER BY p.created_at DESC
            ''')
            
            products = []
            platform_info = MultiPlatformScraper.get_platform_info()
            
            for row in cursor.fetchall():
                try:
                    platform = row[3] or 'storenvy'
                    if platform == 'flights':  # Skip flights
                        continue
                        
                    platform_details = platform_info.get(platform, {
                        'name': 'Unknown', 
                        'icon': '🛒'
                    })
                    
                    products.append({
                        'id': row[0],
                        'user_id': row[1],
                        'url': row[2],
                        'platform': platform,
                        'platform_name': platform_details['name'],
                        'platform_icon': platform_details['icon'],
                        'title': row[4],
                        'target_price': row[5],
                        'last_price': row[6],
                        'last_checked': row[7],
                        'user_email': row[8],
                        'smtp_password': row[9],
                        'user_name': row[10]
                    })
                    
                except Exception as e:
                    print(f"Error processing product row: {e}")
                    continue
            
            conn.close()
            return products
            
        except Exception as e:
            print(f"Error getting all products: {e}")
            return []
    
    def update_product_info(self, product_id: int, title: str, price: float) -> None:
        """Update product information after scraping"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Update product
            cursor.execute('''
                UPDATE tracked_products
                SET title = ?, last_price = ?, last_checked = ?
                WHERE id = ?
            ''', (title, price, datetime.now().isoformat(), product_id))
            
            # Add to price history
            cursor.execute('''
                INSERT INTO price_history (product_id, price)
                VALUES (?, ?)
            ''', (product_id, price))
            
            conn.commit()
            conn.close()
            print(f"Updated product {product_id}: {title[:30]}... - ${price:.2f}")
            
        except Exception as e:
            print(f"Error updating product {product_id}: {e}")
    
    async def scrape_product(self, url: str) -> Optional[Tuple[str, float]]:
        """Scrape product using the multi-platform scraper"""
        try:
            return await self.scraper.scrape_product(url)
        except Exception as e:
            print(f"Error scraping product {url}: {e}")
            return None
    
    def send_email_alert(self, product: Dict[str, Any], user_email: str, smtp_password: str, user_name: str) -> None:
        """Send email alert for price drop"""
        if not smtp_password:
            return
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = user_email
            msg['To'] = user_email
            
            platform = product.get('platform', 'storenvy')
            platform_name = product.get('platform_name', 'Unknown Platform')
            
            # Enhanced subject line based on platform
            if platform == 'roblox':
                msg['Subject'] = f"🎮 Roblox Deal Alert: {product['title'][:40]}..."
            else:
                msg['Subject'] = f"🛍️ Price Drop Alert: {product['title'][:40]}..."
            
            # Determine currency and format prices based on platform
            is_robux = platform == 'roblox'
            
            if is_robux:
                current_price_str = f"{int(product['last_price'])} Robux"
                target_price_str = f"{int(product['target_price'])} Robux"
                savings_str = f"{int(product['target_price'] - product['last_price'])} Robux"
                currency_emoji = "🎮"
            else:
                current_price_str = f"${product['last_price']:.2f}"
                target_price_str = f"${product['target_price']:.2f}"
                savings_str = f"${product['target_price'] - product['last_price']:.2f}"
                currency_emoji = "💰"
            
            # Personalized email body
            if platform == 'roblox':
                body = f"""
Hello {user_name}! 🎮

Great news! A Roblox item you're tracking has dropped to or below your target price!

🎯 Item Details:
{product['title']}

💎 Price Information:
Current Price: {current_price_str}
Target Price: {target_price_str}
You Save: {savings_str}

🔗 Get This Item:
{product['url']}

📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Happy gaming! 🎮

Best regards,
PriceTracker
                """
            else:
                body = f"""
Hello {user_name}! 🛍️

Great news! A product you're tracking has dropped to or below your target price!

🏪 Platform: {product['platform_icon']} {platform_name}
📦 Product: {product['title']}

{currency_emoji} Price Information:
Current Price: {current_price_str}
Target Price: {target_price_str}
You Save: {savings_str}

🔗 Buy This Product:
{product['url']}

📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Happy shopping! 🎉

Best regards,
PriceTracker
                """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email using Gmail SMTP
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(user_email, smtp_password)
            server.send_message(msg)
            server.quit()
            
            print(f"📧 Email alert sent to {user_name} for {platform_name}: {product['title'][:30]}...")
            
        except Exception as e:
            print(f"Failed to send email alert: {str(e)}")
    
    async def check_all_products(self) -> None:
        """Check all tracked products for all users"""
        try:
            products = self.get_all_products_for_checking()
            
            if not products:
                print("No products to check")
                return
            
            print(f"🔄 Checking {len(products)} products for all users")
            
            for product in products:
                try:
                    platform_name = product.get('platform_name', 'Unknown')
                    platform = product.get('platform', 'unknown')
                    print(f"📦 Checking {platform_name} product: {product['url'][:50]}...")
                    
                    # Scrape product
                    result = await self.scrape_product(product['url'])
                    
                    if result:
                        title, current_price = result
                        
                        # Update database
                        self.update_product_info(product['id'], title, current_price)
                        
                        # Enhanced logging based on platform
                        if platform == 'roblox':
                            print(f"✅ Updated {platform_name}: {title[:30]}... - Price: {int(current_price)} Robux")
                        else:
                            print(f"✅ Updated {platform_name}: {title[:30]}... - Price: ${current_price:.2f}")
                        
                        # Check if price dropped below target
                        if current_price <= product['target_price']:
                            if platform == 'roblox':
                                print(f"🎮 ROBLOX DEAL! {title[:30]}... is now at/below target price!")
                            else:
                                print(f"🎉 TARGET HIT! {title[:30]}... is now at/below target price!")
                            
                            # Update product info for email
                            product['title'] = title
                            product['last_price'] = current_price
                            
                            # Send email alert if user has SMTP configured
                            if product.get('smtp_password'):
                                self.send_email_alert(
                                    product, 
                                    product['user_email'],
                                    product['smtp_password'],
                                    product['user_name']
                                )
                    else:
                        print(f"❌ Failed to scrape {platform_name} product")
                
                except Exception as e:
                    print(f"Error checking product {product.get('id', 'unknown')}: {str(e)}")
                    continue
                
                # Rate limiting - be respectful to servers
                delay = 3 + (2 * random.random())
                print(f"⏳ Waiting {delay:.1f}s before next check...")
                await asyncio.sleep(delay)
            
            print(f"✅ Finished checking all products")
            
        except Exception as e:
            print(f"Error in check_all_products: {e}")
    
    def get_supported_platforms(self) -> Dict[str, Dict[str, str]]:
        """Get information about supported platforms (excluding flights)"""
        try:
            platforms = MultiPlatformScraper.get_platform_info()
            # Remove flights from supported platforms
            if 'flights' in platforms:
                del platforms['flights']
            return platforms
        except Exception as e:
            print(f"Error getting supported platforms: {e}")
            return {}


# Test function
async def test_tracker():
    """Test the tracker functionality"""
    try:
        tracker = StorenvyPriceTracker()
        
        print("Testing Multi-Platform Price Tracker")
        print("=" * 50)
        
        # Test platform detection
        test_urls = [
            ("https://www.amazon.com/dp/B08N5WRWNW", 100.00),
            ("https://www.roblox.com/catalog/123456789/test", 500),
        ]
        
        for url, target_price in test_urls:
            try:
                platform = tracker.scraper.detect_platform(url)
                print(f"\n🎯 Testing {platform} URL: {url}")
                
                # Add product for test user
                tracker.add_product(url, target_price, 1)
                
                if platform == 'roblox':
                    print(f"✅ Added {platform} item with target price {target_price} Robux")
                else:
                    print(f"✅ Added {platform} product with target price ${target_price}")
                
            except Exception as e:
                print(f"❌ Failed to add {url}: {e}")
        
        # Test getting tracked products
        products = tracker.get_tracked_products(1)
        print(f"\n📋 Currently tracking {len(products)} products:")
        for product in products:
            platform_name = product.get('platform_name', 'Unknown')
            print(f"  - {platform_name}: {product['url'][:50]}...")
            
        print("\n✅ Tracker test completed successfully")
        
    except Exception as e:
        print(f"❌ Error in test_tracker: {e}")


if __name__ == "__main__":
    asyncio.run(test_tracker())