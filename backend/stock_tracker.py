# backend/stock_tracker.py - FIXED VERSION WITH USER SUPPORT
import asyncio
import json
import re
import smtplib
import sqlite3
import time
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from playwright.async_api import async_playwright


class StockPriceTracker:
    def __init__(self, db_path: str = "storenvy_tracker.db"):
        self.db_path = db_path
        self.init_stock_tables()
        
    def init_stock_tables(self) -> None:
        """Initialize SQLite database tables for stock tracking."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Stock alerts table with user_id
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                company_name TEXT,
                alert_type TEXT NOT NULL,
                threshold REAL NOT NULL,
                current_price REAL,
                last_checked TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_triggered BOOLEAN DEFAULT 0,
                UNIQUE(user_id, symbol, alert_type, threshold)
            )
        ''')
        
        # Check if user_id column exists in existing table
        cursor.execute("PRAGMA table_info(stock_alerts)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'user_id' not in columns:
            # Add user_id column to existing table
            cursor.execute('ALTER TABLE stock_alerts ADD COLUMN user_id INTEGER DEFAULT 1')
            print("Added user_id column to stock_alerts table")
        
        # Stock price history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                volume INTEGER,
                change_percent REAL,
                market_cap TEXT,
                checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_stock_alert(self, symbol: str, alert_type: str, threshold: float, user_id: int) -> None:
        """Add a stock alert to track for a specific user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert symbol to uppercase
        symbol = symbol.upper().strip()
        
        try:
            cursor.execute('''
                INSERT INTO stock_alerts (user_id, symbol, alert_type, threshold)
                VALUES (?, ?, ?, ?)
            ''', (user_id, symbol, alert_type, threshold))
            conn.commit()
        except sqlite3.IntegrityError:
            # Update existing alert
            cursor.execute('''
                UPDATE stock_alerts
                SET alert_type = ?, threshold = ?, is_triggered = 0
                WHERE user_id = ? AND symbol = ?
            ''', (alert_type, threshold, user_id, symbol))
            conn.commit()
        
        conn.close()
    
    def delete_stock_alert(self, alert_id: int, user_id: int) -> None:
        """Delete a stock alert for a specific user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete price history first
        cursor.execute('''
            DELETE FROM stock_price_history 
            WHERE symbol IN (
                SELECT symbol FROM stock_alerts 
                WHERE id = ? AND user_id = ?
            )
        ''', (alert_id, user_id))
        
        # Delete alert
        cursor.execute('DELETE FROM stock_alerts WHERE id = ? AND user_id = ?', (alert_id, user_id))
        
        conn.commit()
        conn.close()
    
    def get_stock_alerts(self, user_id: int) -> List[Dict[str, any]]:
        """Get all stock alerts for a specific user."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, symbol, company_name, alert_type, threshold, current_price, last_checked, is_triggered
            FROM stock_alerts
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        
        alerts: List[Dict[str, any]] = []
        for row in cursor.fetchall():
            # Determine status based on alert type and current price
            status = 'waiting'
            if row[5] and row[6]:  # current_price and last_checked exist
                if row[3] == 'price_above' and row[5] >= row[4]:
                    status = 'triggered'
                elif row[3] == 'price_below' and row[5] <= row[4]:
                    status = 'triggered'
                elif row[3] == 'percent_up' and row[5] > 0:  # We'll calculate this in scraping
                    status = 'triggered' if row[7] else 'monitoring'
                elif row[3] == 'percent_down' and row[5] > 0:
                    status = 'triggered' if row[7] else 'monitoring'
            
            alerts.append({
                'id': row[0],
                'symbol': row[1],
                'company_name': row[2] or row[1],
                'alert_type': row[3],
                'threshold': row[4],
                'current_price': row[5],
                'last_checked': row[6],
                'is_triggered': row[7],
                'status': status
            })
        
        conn.close()
        return alerts

    def get_all_alerts_for_checking(self) -> List[Dict[str, any]]:
        """Get all stock alerts from all users for checking."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.id, a.user_id, a.symbol, a.company_name, a.alert_type, a.threshold, 
                   a.current_price, a.last_checked, a.is_triggered,
                   u.email, u.smtp_password, u.first_name
            FROM stock_alerts a
            JOIN users u ON a.user_id = u.id
            ORDER BY a.created_at DESC
        ''')
        
        alerts: List[Dict[str, any]] = []
        for row in cursor.fetchall():
            alerts.append({
                'id': row[0],
                'user_id': row[1],
                'symbol': row[2],
                'company_name': row[3] or row[2],
                'alert_type': row[4],
                'threshold': row[5],
                'current_price': row[6],
                'last_checked': row[7],
                'is_triggered': row[8],
                'user_email': row[9],
                'smtp_password': row[10],
                'user_name': row[11]
            })
        
        conn.close()
        return alerts
    
    def update_stock_info(self, symbol: str, company_name: str, price: float, volume: int = None, change_percent: float = None) -> None:
        """Update stock information after scraping."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Update current price in alerts table
        cursor.execute('''
            UPDATE stock_alerts
            SET company_name = ?, current_price = ?, last_checked = ?
            WHERE symbol = ?
        ''', (company_name, price, datetime.now(), symbol))
        
        # Add to price history
        cursor.execute('''
            INSERT INTO stock_price_history (symbol, price, volume, change_percent)
            VALUES (?, ?, ?, ?)
        ''', (symbol, price, volume, change_percent))
        
        conn.commit()
        conn.close()
    
    async def scrape_yahoo_finance(self, symbol: str) -> Optional[Tuple[str, float, int, float]]:
        """Improved Yahoo Finance scraper with better reliability."""
        url = f"https://finance.yahoo.com/quote/{symbol}"
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu'
                ]
            )

            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                timezone_id='America/New_York'
            )

            page = await context.new_page()

            try:
                print(f"Scraping {symbol} from Yahoo Finance...")
                await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                await page.wait_for_timeout(5000)

                # Extract company name with multiple selectors
                company_name = symbol  # Default fallback
                name_selectors = [
                    'h1[data-testid="quote-header"]',
                    'h1.D\\(ib\\)',
                    'h1[data-field="name"]',
                    '.quote-header-info h1',
                    '[data-testid="quote-header"] h1',
                    'section[data-testid="quote-header"] h1'
                ]
                
                for selector in name_selectors:
                    try:
                        element = await page.wait_for_selector(selector, timeout=3000)
                        if element:
                            name_text = await element.text_content()
                            if name_text and len(name_text.strip()) > 0:
                                # Clean up the name (remove symbol if present)
                                company_name = name_text.strip().split('(')[0].strip()
                                print(f"Found company name: {company_name}")
                                break
                    except Exception:
                        continue

                # Extract current price with improved selectors
                price = None
                price_selectors = [
                    'fin-streamer[data-testid="quote-price"]',
                    '[data-testid="quote-price"]',
                    'fin-streamer[data-field="regularMarketPrice"]',
                    'span[data-reactid*="price"]',
                    '.quote-header-info [data-reactid] span',
                    '.Fw\\(b\\).Fz\\(36px\\)',
                    'span.Trsdu\\(0\\.3s\\).Fw\\(b\\).Fz\\(36px\\)',
                    '[data-symbol="' + symbol + '"] fin-streamer[data-field="regularMarketPrice"]'
                ]

                for selector in price_selectors:
                    try:
                        element = await page.wait_for_selector(selector, timeout=3000)
                        if element:
                            price_text = await element.text_content()
                            print(f"Found price text with selector {selector}: {price_text}")
                            
                            if price_text:
                                # Clean and extract number from price text
                                cleaned_price = price_text.replace('$', '').replace(',', '').strip()
                                price_match = re.search(r'(\d+(?:\.\d{1,4})?)', cleaned_price)
                                if price_match:
                                    price = float(price_match.group(1))
                                    if price > 0:
                                        print(f"Successfully extracted price: ${price}")
                                        break
                    except Exception:
                        continue

                # Extract change percentage
                change_percent = None
                change_selectors = [
                    'fin-streamer[data-testid="quote-price"] + fin-streamer',
                    'fin-streamer[data-field="regularMarketChangePercent"]',
                    '[data-testid="quote-price"] + span',
                    '.quote-header span[data-reactid*="percent"]'
                ]

                for selector in change_selectors:
                    try:
                        element = await page.wait_for_selector(selector, timeout=2000)
                        if element:
                            change_text = await element.text_content()
                            if change_text and '%' in change_text:
                                # Extract percentage
                                percent_match = re.search(r'([+-]?\d+(?:\.\d{1,2})?)%', change_text)
                                if percent_match:
                                    change_percent = float(percent_match.group(1))
                                    print(f"Found change percent: {change_percent}%")
                                    break
                    except Exception:
                        continue

                if price is None:
                    print(f"Could not extract price for {symbol} from Yahoo Finance")
                    return None

                return company_name, price, 0, change_percent or 0.0

            except Exception as e:
                print(f"Error scraping {symbol} from Yahoo Finance: {str(e)}")
                return None

            finally:
                await browser.close()

    async def get_stock_data(self, symbol: str) -> Optional[Tuple[str, float, int, float]]:
        """Get stock data with fallback sources."""
        print(f"Attempting to get data for {symbol}...")
        data = await self.scrape_yahoo_finance(symbol)
        if data:
            print(f"✅ Yahoo Finance success for {symbol}: ${data[1]}")
            return data
            
        print(f"❌ Failed to get data for {symbol}")
        return None

    def check_alert_conditions(self, alert: Dict, current_price: float, change_percent: float) -> bool:
        """Check if alert conditions are met."""
        alert_type = alert['alert_type']
        threshold = alert['threshold']
        
        if alert_type == 'price_above':
            return current_price >= threshold
        elif alert_type == 'price_below':
            return current_price <= threshold
        elif alert_type == 'percent_up':
            return change_percent >= threshold
        elif alert_type == 'percent_down':
            return change_percent <= -threshold  # Negative for down movement
        
        return False

    def send_stock_alert_email(self, alert: Dict, current_price: float, change_percent: float) -> None:
        """Send email alert for stock price trigger."""
        if not alert.get('smtp_password'):
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = alert['user_email']
            msg['To'] = alert['user_email']
            msg['Subject'] = f"🚨 Stock Alert: {alert['symbol']} - {alert['alert_type']}"
            
            # Create alert type description
            alert_descriptions = {
                'price_above': f"Price above ${alert['threshold']:.2f}",
                'price_below': f"Price below ${alert['threshold']:.2f}",
                'percent_up': f"Up {alert['threshold']}% or more",
                'percent_down': f"Down {alert['threshold']}% or more"
            }
            
            body = f"""
Hello {alert['user_name']}! 🚨

Stock Alert Triggered!

Stock: {alert['symbol']} ({alert['company_name']})
Alert: {alert_descriptions.get(alert['alert_type'], alert['alert_type'])}

Current Price: ${current_price:.2f}
Change Today: {change_percent:+.2f}%
Threshold: {alert['threshold']}

View on Yahoo Finance: https://finance.yahoo.com/quote/{alert['symbol']}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Happy trading! 📈

Best regards,
PriceTracker
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(alert['user_email'], alert['smtp_password'])
            server.send_message(msg)
            server.quit()
            
            print(f"📧 Alert email sent to {alert['user_name']} for {alert['symbol']}")
            
        except Exception as e:
            print(f"Failed to send stock alert email: {str(e)}")

    def mark_alert_triggered(self, alert_id: int) -> None:
        """Mark an alert as triggered to avoid spam."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE stock_alerts
            SET is_triggered = 1
            WHERE id = ?
        ''', (alert_id,))
        
        conn.commit()
        conn.close()

    async def check_all_stock_alerts(self) -> None:
        """Check all stock alerts for all users."""
        alerts = self.get_all_alerts_for_checking()
        
        if not alerts:
            print("No stock alerts to check")
            return
        
        print(f"🔄 Checking {len(alerts)} stock alerts...")
        
        for alert in alerts:
            # Skip already triggered alerts (to avoid spam)
            if alert['is_triggered']:
                continue
                
            symbol = alert['symbol']
            print(f"📊 Checking {symbol} for user {alert['user_name']}...")
            
            stock_data = await self.get_stock_data(symbol)
            
            if stock_data:
                company_name, current_price, volume, change_percent = stock_data
                
                # Update database with current info
                self.update_stock_info(symbol, company_name, current_price, volume, change_percent)
                
                # Check if alert conditions are met
                if self.check_alert_conditions(alert, current_price, change_percent):
                    print(f"🚨 ALERT TRIGGERED: {symbol} - {alert['alert_type']} for {alert['user_name']}")
                    
                    # Send notification if user has SMTP configured
                    if alert.get('smtp_password'):
                        self.send_stock_alert_email(alert, current_price, change_percent)
                    
                    # Mark as triggered to avoid repeated alerts
                    self.mark_alert_triggered(alert['id'])
                else:
                    print(f"✅ {symbol}: ${current_price:.2f} ({change_percent:+.2f}%) - No trigger")
            else:
                print(f"❌ Failed to get data for {symbol}")
            
            # Be nice to the servers
            await asyncio.sleep(3)

    def reset_triggered_alerts(self) -> None:
        """Reset all triggered alerts (useful for daily reset)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE stock_alerts SET is_triggered = 0')
        
        conn.commit()
        conn.close()
        print("All triggered alerts have been reset")

    def get_stock_stats(self, user_id: int) -> Dict:
        """Get statistics about tracked stocks for a specific user."""
        alerts = self.get_stock_alerts(user_id)
        
        total_alerts = len(alerts)
        triggered_alerts = sum(1 for alert in alerts if alert['is_triggered'])
        monitoring_alerts = total_alerts - triggered_alerts
        
        return {
            'total_alerts': total_alerts,
            'triggered_alerts': triggered_alerts,
            'monitoring_alerts': monitoring_alerts
        }


# Test function to verify everything works
async def test_stock_tracker():
    """Test function to verify the stock tracker works."""
    tracker = StockPriceTracker()
    
    print("Testing stock tracker...")
    
    # Test scraping different stocks
    test_symbols = ["AAPL", "MSFT", "GOOGL"]
    
    for symbol in test_symbols:
        print(f"\n📊 Testing {symbol}...")
        data = await tracker.get_stock_data(symbol)
        if data:
            company_name, price, volume, change_percent = data
            print(f"✅ {company_name}: ${price:.2f} ({change_percent:+.2f}%)")
        else:
            print(f"❌ Failed to get {symbol} data")


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_stock_tracker())