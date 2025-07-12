# backend/tracker.py - UPDATED WITH PLATFORM-SPECIFIC CHECK METHODS
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
    """Multi-platform price tracker with enhanced flight support and platform-specific checking"""
    
    def __init__(self, db_path: str = "storenvy_tracker.db"):
        self.db_path = db_path
        self.scraper = MultiPlatformScraper()
        self.init_database()
        
    def init_database(self) -> None:
        """Initialize SQLite database for storing tracked products"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create main products table
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
            
            # Check if platform column exists
            cursor.execute("PRAGMA table_info(tracked_products)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'platform' not in columns:
                cursor.execute('ALTER TABLE tracked_products ADD COLUMN platform TEXT')
                print("Added platform column to existing database")
            
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
    
    def add_product(self, url: str, target_price: float) -> None:
        """Add a product to track"""
        try:
            # Detect platform
            platform = self.scraper.detect_platform(url)
            if not platform:
                raise ValueError("Unsupported e-commerce platform")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                # Try to insert new product
                cursor.execute('''
                    INSERT INTO tracked_products (url, platform, target_price)
                    VALUES (?, ?, ?)
                ''', (url, platform, target_price))
                conn.commit()
                print(f"Added new product from {platform}: {url[:50]}...")
                
            except sqlite3.IntegrityError:
                # Update existing product
                cursor.execute('''
                    UPDATE tracked_products
                    SET target_price = ?, platform = ?
                    WHERE url = ?
                ''', (target_price, platform, url))
                conn.commit()
                print(f"Updated existing product from {platform}: {url[:50]}...")
            
            conn.close()
            
        except Exception as e:
            print(f"Error adding product: {e}")
            raise
    
    def delete_product(self, product_id: int) -> None:
        """Delete a tracked product"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Delete price history first
            cursor.execute('DELETE FROM price_history WHERE product_id = ?', (product_id,))
            
            # Delete product
            cursor.execute('DELETE FROM tracked_products WHERE id = ?', (product_id,))
            
            conn.commit()
            conn.close()
            print(f"Deleted product {product_id}")
            
        except Exception as e:
            print(f"Error deleting product {product_id}: {e}")
            raise
    
    def get_tracked_products(self) -> List[Dict[str, Any]]:
        """Get all tracked products from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, url, platform, title, target_price, last_price, last_checked
                FROM tracked_products
                ORDER BY created_at DESC
            ''')
            
            products = []
            platform_info = MultiPlatformScraper.get_platform_info()
            
            for row in cursor.fetchall():
                try:
                    platform = row[2] or 'storenvy'  # Default fallback
                    platform_details = platform_info.get(platform, {
                        'name': 'Unknown', 
                        'icon': '🛒'
                    })
                    
                    # Determine status
                    status = 'waiting'
                    if row[5] is not None and row[4] is not None:  # last_price and target_price
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

    def get_products_by_platform(self, platforms: List[str]) -> List[Dict[str, Any]]:
        """Get products filtered by specific platforms"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            platform_placeholders = ','.join(['?' for _ in platforms])
            query = f'''
                SELECT id, url, platform, title, target_price, last_price, last_checked
                FROM tracked_products
                WHERE platform IN ({platform_placeholders})
                ORDER BY created_at DESC
            '''
            
            cursor.execute(query, platforms)
            
            products = []
            platform_info = MultiPlatformScraper.get_platform_info()
            
            for row in cursor.fetchall():
                try:
                    platform = row[2] or 'storenvy'
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
            print(f"Error getting products by platform: {e}")
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
    
    def generate_clickable_link(self, product: Dict[str, Any]) -> str:
        """Generate a more user-friendly clickable link based on platform"""
        try:
            platform = product.get('platform', 'unknown')
            original_url = product['url']
            
            # For flights, try to create a more direct search link
            if platform == 'flights':
                parsed_url = urlparse(original_url)
                domain = parsed_url.netloc.lower()
                
                if 'kayak.com' in domain:
                    return original_url
                elif 'booking.com' in domain:
                    return original_url
                elif 'priceline.com' in domain:
                    return original_url
                elif 'momondo.com' in domain:
                    return original_url
                elif 'expedia.com' in domain:
                    return original_url
                else:
                    return original_url
            
            # For other platforms, return the original URL
            return original_url
            
        except Exception as e:
            print(f"Error generating clickable link: {e}")
            return product['url']
    
    def send_email_alert(self, product: Dict[str, Any], smtp_config: Dict[str, Any]) -> None:
        """Send email alert for price drop with enhanced flight support"""
        if not smtp_config.get('enabled'):
            return
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = smtp_config['from_email']
            msg['To'] = smtp_config['to_email']
            
            platform = product.get('platform', 'storenvy')
            platform_name = product.get('platform_name', 'Unknown Platform')
            
            # Enhanced subject line based on platform
            if platform == 'flights':
                msg['Subject'] = f"✈️ Flight Deal Alert: {product['title'][:40]}..."
            elif platform == 'roblox':
                msg['Subject'] = f"🎮 Roblox Deal Alert: {product['title'][:40]}..."
            else:
                msg['Subject'] = f"🛍️ Price Drop Alert: {product['title'][:40]}..."
            
            # Generate clickable link
            clickable_link = self.generate_clickable_link(product)
            
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
            
            # Enhanced email body with platform-specific content
            if platform == 'flights':
                body = f"""
✈️ FLIGHT DEAL ALERT! ✈️

Great news! A flight you're tracking has dropped to or below your target price!

🛫 Flight Details:
{product['title']}

💰 Price Information:
Current Price: {current_price_str}
Target Price: {target_price_str}
You Save: {savings_str}

🔗 Book This Flight:
{clickable_link}

📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Don't wait - flight prices change frequently! ✈️

Happy travels! 🌍
                """
            elif platform == 'roblox':
                body = f"""
🎮 ROBLOX UGC DEAL ALERT! 🎮

Great news! A Roblox item you're tracking has dropped to or below your target price!

🎯 Item Details:
{product['title']}

💎 Price Information:
Current Price: {current_price_str}
Target Price: {target_price_str}
You Save: {savings_str}

🔗 Get This Item:
{clickable_link}

📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Happy gaming! 🎮
                """
            else:
                body = f"""
🛍️ PRICE DROP ALERT! 🛍️

Great news! A product you're tracking has dropped to or below your target price!

🏪 Platform: {product['platform_icon']} {platform_name}
📦 Product: {product['title']}

{currency_emoji} Price Information:
Current Price: {current_price_str}
Target Price: {target_price_str}
You Save: {savings_str}

🔗 Buy This Product:
{clickable_link}

📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Happy shopping! 🎉
                """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            server = smtplib.SMTP(smtp_config['smtp_server'], smtp_config['smtp_port'])
            server.starttls()
            server.login(smtp_config['from_email'], smtp_config['password'])
            server.send_message(msg)
            server.quit()
            
            print(f"📧 Email alert sent for {platform_name}: {product['title'][:30]}...")
            
        except Exception as e:
            print(f"Failed to send email alert: {str(e)}")
    
    async def check_all_products(self, smtp_config: Optional[Dict[str, Any]] = None) -> None:
        """Check all tracked products for price drops - LEGACY METHOD"""
        await self.check_products_by_platform(['amazon', 'ebay', 'etsy', 'walmart', 'storenvy', 'roblox', 'flights'], smtp_config)
    
    async def check_ecommerce_products_only(self, smtp_config: Optional[Dict[str, Any]] = None) -> None:
        """Check only e-commerce products (excludes flights) for price drops"""
        await self.check_products_by_platform(['amazon', 'ebay', 'etsy', 'walmart', 'storenvy', 'roblox'], smtp_config)
    
    async def check_flight_products_only(self, smtp_config: Optional[Dict[str, Any]] = None) -> None:
        """Check only flight products for price drops"""
        await self.check_products_by_platform(['flights'], smtp_config)

    async def check_products_by_platform(self, platforms: List[str], smtp_config: Optional[Dict[str, Any]] = None) -> None:
        """Check products for specific platforms with enhanced flight support"""
        try:
            products = self.get_products_by_platform(platforms)
            
            if not products:
                platform_names = ', '.join(platforms)
                print(f"No {platform_names} products to check")
                return
            
            platform_names = ', '.join(platforms)
            print(f"🔄 Checking {len(products)} products from platforms: {platform_names}")
            
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
                            if platform == 'flights':
                                print(f"✈️ FLIGHT DEAL! {title[:30]}... is now at/below target price!")
                            elif platform == 'roblox':
                                print(f"🎮 ROBLOX DEAL! {title[:30]}... is now at/below target price!")
                            else:
                                print(f"🎉 TARGET HIT! {title[:30]}... is now at/below target price!")
                            
                            # Update product info for email
                            product['title'] = title
                            product['last_price'] = current_price
                            
                            # Send email alert if configured
                            if smtp_config and smtp_config.get('enabled'):
                                self.send_email_alert(product, smtp_config)
                    else:
                        print(f"❌ Failed to scrape {platform_name} product")
                
                except Exception as e:
                    print(f"Error checking product {product.get('id', 'unknown')}: {str(e)}")
                    continue
                
                # Rate limiting - be respectful to servers, longer delay for flight sites
                try:
                    platform = product.get('platform', 'unknown')
                    if platform == 'flights':
                        delay = 5 + (3 * random.random())  # Longer delay for flight sites
                    else:
                        delay = 3 + (2 * random.random())
                    
                    print(f"⏳ Waiting {delay:.1f}s before next check...")
                    await asyncio.sleep(delay)
                except Exception as e:
                    print(f"Error during delay: {e}")
            
            print(f"✅ Finished checking {platform_names} products")
            
        except Exception as e:
            print(f"Error in check_products_by_platform: {e}")
    
    def get_supported_platforms(self) -> Dict[str, Dict[str, str]]:
        """Get information about supported platforms"""
        try:
            return MultiPlatformScraper.get_platform_info()
        except Exception as e:
            print(f"Error getting supported platforms: {e}")
            return {}


# Test function
async def test_tracker():
    """Test the tracker functionality with flight support"""
    try:
        tracker = StorenvyPriceTracker()
        
        print("Testing Enhanced Multi-Platform Price Tracker")
        print("=" * 50)
        
        # Test platform detection
        test_urls = [
            ("https://www.amazon.com/dp/B08N5WRWNW", 100.00),
            ("https://www.kayak.com/flights/LAX-NYC/2024-03-15/2024-03-22", 350.00),
            ("https://www.roblox.com/catalog/123456789/test", 500),
        ]
        
        for url, target_price in test_urls:
            try:
                platform = tracker.scraper.detect_platform(url)
                print(f"\n🎯 Testing {platform} URL: {url}")
                
                # Add product
                tracker.add_product(url, target_price)
                
                if platform == 'flights':
                    print(f"✅ Added {platform} with target price ${target_price}")
                elif platform == 'roblox':
                    print(f"✅ Added {platform} item with target price {target_price} Robux")
                else:
                    print(f"✅ Added {platform} product with target price ${target_price}")
                
            except Exception as e:
                print(f"❌ Failed to add {url}: {e}")
        
        # Test getting tracked products
        products = tracker.get_tracked_products()
        print(f"\n📋 Currently tracking {len(products)} products:")
        for product in products:
            platform_name = product.get('platform_name', 'Unknown')
            print(f"  - {platform_name}: {product['url'][:50]}...")
            
        print("\n✅ Enhanced tracker test completed successfully")
        
    except Exception as e:
        print(f"❌ Error in test_tracker: {e}")


if __name__ == "__main__":
    asyncio.run(test_tracker())