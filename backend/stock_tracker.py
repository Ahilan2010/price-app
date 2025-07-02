# backend/stock_tracker.py
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
        
        # Stock alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                company_name TEXT,
                alert_type TEXT NOT NULL,
                threshold REAL NOT NULL,
                current_price REAL,
                last_checked TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_triggered BOOLEAN DEFAULT 0
            )
        ''')
        
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
    
    def add_stock_alert(self, symbol: str, alert_type: str, threshold: float) -> None:
        """Add a stock alert to track."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert symbol to uppercase
        symbol = symbol.upper().strip()
        
        try:
            cursor.execute('''
                INSERT INTO stock_alerts (symbol, alert_type, threshold)
                VALUES (?, ?, ?)
            ''', (symbol, alert_type, threshold))
            conn.commit()
        except sqlite3.IntegrityError:
            # Update existing alert
            cursor.execute('''
                UPDATE stock_alerts
                SET alert_type = ?, threshold = ?, is_triggered = 0
                WHERE symbol = ?
            ''', (alert_type, threshold, symbol))
            conn.commit()
        
        conn.close()
    
    def delete_stock_alert(self, alert_id: int) -> None:
        """Delete a stock alert."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Delete price history first
        cursor.execute('DELETE FROM stock_price_history WHERE symbol IN (SELECT symbol FROM stock_alerts WHERE id = ?)', (alert_id,))
        # Delete alert
        cursor.execute('DELETE FROM stock_alerts WHERE id = ?', (alert_id,))
        
        conn.commit()
        conn.close()
    
    def get_stock_alerts(self) -> List[Dict[str, any]]:
        """Get all stock alerts from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, symbol, company_name, alert_type, threshold, current_price, last_checked, is_triggered
            FROM stock_alerts
            ORDER BY created_at DESC
        ''')
        
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
        """Scrape stock data from Yahoo Finance."""
        url = f"https://finance.yahoo.com/quote/{symbol}"
        
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

                # Extract company name
                company_name = symbol  # Default fallback
                name_selectors = [
                    'h1[data-testid="quote-header"]',
                    'h1.D\\(ib\\)',
                    'h1[data-field="name"]',
                    '.quote-header-info h1'
                ]
                
                for selector in name_selectors:
                    try:
                        element = await page.wait_for_selector(selector, timeout=2000)
                        if element:
                            name_text = await element.text_content()
                            if name_text and len(name_text.strip()) > 0:
                                # Clean up the name (remove symbol if present)
                                company_name = name_text.strip().split('(')[0].strip()
                                break
                    except Exception:
                        continue

                # Extract current price
                price = None
                price_selectors = [
                    '[data-testid="quote-price"]',
                    'fin-streamer[data-field="regularMarketPrice"]',
                    '.quote-header-info [data-reactid] span',
                    '.quote-header .Fw\\(b\\).Fz\\(36px\\)',
                    'span.Trsdu\\(0\\.3s\\).Fw\\(b\\).Fz\\(36px\\)'
                ]

                for selector in price_selectors:
                    try:
                        element = await page.wait_for_selector(selector, timeout=2000)
                        if element:
                            price_text = await element.text_content()
                            if price_text:
                                # Extract number from price text
                                price_match = re.search(r'(\d+(?:,\d{3})*(?:\.\d{1,4})?)', price_text.replace(',', ''))
                                if price_match:
                                    price = float(price_match.group(1))
                                    if price > 0:
                                        break
                    except Exception:
                        continue

                # Extract volume
                volume = None
                volume_selectors = [
                    '[data-testid="quote-statistics"] td:contains("Volume") + td',
                    'td[data-test="VOLUME-value"]',
                    'span[data-reactid]:contains("Volume")',
                ]

                # Note: Volume extraction is complex on Yahoo Finance, we'll start without it
                # and add later if needed

                # Extract change percentage
                change_percent = None
                change_selectors = [
                    '[data-testid="quote-price"] + span',
                    'fin-streamer[data-field="regularMarketChangePercent"]',
                    '.quote-header span[data-reactid]:contains("%")'
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
                                    break
                    except Exception:
                        continue

                if price is None:
                    print(f"Could not extract price for {symbol}")
                    return None

                return company_name, price, volume or 0, change_percent or 0.0

            except Exception as e:
                print(f"Error scraping {symbol}: {str(e)}")
                return None

            finally:
                await browser.close()

    async def scrape_google_finance_fallback(self, symbol: str) -> Optional[Tuple[str, float, int, float]]:
        """Fallback scraper for Google Finance."""
        url = f"https://www.google.com/finance/quote/{symbol}:NASDAQ"
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                await page.goto(url, wait_until='domcontentloaded', timeout=15000)
                await page.wait_for_timeout(2000)

                # Google Finance selectors (simplified)
                company_name = symbol
                price = None
                
                # Try to get price
                try:
                    price_element = await page.wait_for_selector('.YMlKec.fxKbKc', timeout=3000)
                    if price_element:
                        price_text = await price_element.text_content()
                        price_match = re.search(r'(\d+(?:\.\d{1,4})?)', price_text.replace('$', '').replace(',', ''))
                        if price_match:
                            price = float(price_match.group(1))
                except Exception:
                    pass

                if price:
                    return company_name, price, 0, 0.0
                return None

            except Exception as e:
                print(f"Google Finance fallback failed for {symbol}: {str(e)}")
                return None
            finally:
                await browser.close()

    async def get_stock_data(self, symbol: str) -> Optional[Tuple[str, float, int, float]]:
        """Get stock data with fallback sources."""
        # Try Yahoo Finance first
        data = await self.scrape_yahoo_finance(symbol)
        if data:
            return data
        
        print(f"Yahoo Finance failed for {symbol}, trying Google Finance...")
        # Fallback to Google Finance
        data = await self.scrape_google_finance_fallback(symbol)
        return data

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

    def send_stock_alert_email(self, alert: Dict, current_price: float, change_percent: float, smtp_config: Dict) -> None:
        """Send email alert for stock price trigger."""
        if not smtp_config.get('enabled'):
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_config['from_email']
            msg['To'] = smtp_config['to_email']
            msg['Subject'] = f"Stock Alert: {alert['symbol']} - {alert['alert_type']}"
            
            # Create alert type description
            alert_descriptions = {
                'price_above': f"Price above ${alert['threshold']:.2f}",
                'price_below': f"Price below ${alert['threshold']:.2f}",
                'percent_up': f"Up {alert['threshold']}% or more",
                'percent_down': f"Down {alert['threshold']}% or more"
            }
            
            body = f"""
            🚨 Stock Alert Triggered! 🚨
            
            Stock: {alert['symbol']} ({alert['company_name']})
            Alert: {alert_descriptions.get(alert['alert_type'], alert['alert_type'])}
            
            Current Price: ${current_price:.2f}
            Change Today: {change_percent:+.2f}%
            Threshold: {alert['threshold']}
            
            View on Yahoo Finance: https://finance.yahoo.com/quote/{alert['symbol']}
            
            Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            Happy trading! 📈
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(smtp_config['smtp_server'], smtp_config['smtp_port'])
            server.starttls()
            server.login(smtp_config['from_email'], smtp_config['password'])
            server.send_message(msg)
            server.quit()
            
            print(f"Alert email sent for {alert['symbol']}")
            
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

    async def check_all_stock_alerts(self, smtp_config: Optional[Dict] = None) -> None:
        """Check all stock alerts for triggers."""
        alerts = self.get_stock_alerts()
        
        if not alerts:
            print("No stock alerts to check")
            return
        
        print(f"Checking {len(alerts)} stock alerts...")
        
        for alert in alerts:
            # Skip already triggered alerts (to avoid spam)
            if alert['is_triggered']:
                continue
                
            symbol = alert['symbol']
            print(f"Checking {symbol}...")
            
            stock_data = await self.get_stock_data(symbol)
            
            if stock_data:
                company_name, current_price, volume, change_percent = stock_data
                
                # Update database with current info
                self.update_stock_info(symbol, company_name, current_price, volume, change_percent)
                
                # Check if alert conditions are met
                if self.check_alert_conditions(alert, current_price, change_percent):
                    print(f"🚨 ALERT TRIGGERED: {symbol} - {alert['alert_type']}")
                    
                    # Send notification
                    if smtp_config:
                        self.send_stock_alert_email(alert, current_price, change_percent, smtp_config)
                    
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

    def get_stock_stats(self) -> Dict:
        """Get statistics about tracked stocks."""
        alerts = self.get_stock_alerts()
        
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
    
    # Test scraping Apple stock
    print("Testing Apple (AAPL) scraping...")
    data = await tracker.get_stock_data("AAPL")
    if data:
        company_name, price, volume, change_percent = data
        print(f"✅ {company_name}: ${price:.2f} ({change_percent:+.2f}%)")
    else:
        print("❌ Failed to get Apple data")
    
    # Test scraping Microsoft stock
    print("Testing Microsoft (MSFT) scraping...")
    data = await tracker.get_stock_data("MSFT")
    if data:
        company_name, price, volume, change_percent = data
        print(f"✅ {company_name}: ${price:.2f} ({change_percent:+.2f}%)")
    else:
        print("❌ Failed to get Microsoft data")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_stock_tracker())
