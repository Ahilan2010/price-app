# backend/tracker.py - COMPLETE ENHANCED VERSION WITH ULTRA STEALTH SCRAPER
import asyncio
import json
import smtplib
import sqlite3
import time
import random
import re
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlparse
from playwright.async_api import async_playwright


class EnhancedMultiPlatformScraper:
    """Ultra-stealth multi-platform scraper with precise price detection and bot evasion"""
    
    def __init__(self):
        self.platform_configs = {
            'amazon': {
                'domain_patterns': ['amazon.com', 'amazon.co', 'amazon.ca', 'amazon.in', 'amazon.de', 'amazon.fr'],
                'title_selectors': [
                    'span#productTitle',
                    'h1#title span',
                    'h1.a-size-large span',
                    'h1[data-automation-id="product-title"]',
                    '[data-feature-name="title"] h1 span',
                    'div#title_feature_div span'
                ],
                'price_selectors': [
                    # Primary price selectors (most accurate)
                    'span.a-price.a-text-price.a-size-medium.apexPriceToPay span.a-offscreen',
                    'span.a-price.a-text-price.apexPriceToPay span.a-offscreen',
                    'span.a-price-current span.a-offscreen',
                    'div[data-feature-name="apex_desktop"] span.a-price-whole',
                    'span.a-price.aok-align-center.reinventPricePriceToPayMargin span.a-offscreen',
                    # Fallback selectors
                    '#priceblock_dealprice',
                    '#priceblock_ourprice',
                    '.a-price .a-offscreen'
                ],
                'wait_time': 6000,
                'scroll_behavior': 'minimal'
            },
            'walmart': {
                'domain_patterns': ['walmart.com'],
                'title_selectors': [
                    'h1[data-automation-id="product-title"]',
                    'h1[itemprop="name"]',
                    'h1.prod-ProductTitle',
                    'main h1',
                    'h1'
                ],
                'price_selectors': [
                    # Most accurate Walmart price selectors
                    'div[data-testid="price-wrap"] span[itemprop="price"]',
                    'span[data-automation-id="buybox-price"]',
                    'div[data-testid="add-to-cart-price"] span',
                    'span[itemprop="price"]',
                    'div.price-current span',
                    '.price.display-inline-block span',
                    'div[data-testid="price"] span'
                ],
                'exclude_selectors': [
                    # Exclude recommendation/other product prices
                    'div[data-testid="recommendations"] *',
                    'div[data-testid="similar-items"] *',
                    'div[data-testid="you-might-also-like"] *',
                    '.recommendations *',
                    '.similar-items *',
                    '.sponsored-products *'
                ],
                'wait_time': 8000,
                'scroll_behavior': 'targeted'
            },
            'etsy': {
                'domain_patterns': ['etsy.com'],
                'title_selectors': [
                    'h1[data-buy-box-listing-title]',
                    'h1[data-test-id="listing-page-title"]',
                    'h1.wt-text-body-01',
                    'div[data-region="listing-title"] h1'
                ],
                'price_selectors': [
                    # Updated Etsy selectors for 2024
                    'p[data-testid="price"] span.currency-value',
                    'div[data-buy-box-region="price"] p[data-selector="price-only"]',
                    'p.wt-text-title-larger span.currency-value',
                    'span.wt-text-title-largest',
                    'div[data-selector="listing-page-cart"] span.currency-value',
                    'p.currency span.currency-value'
                ],
                'wait_time': 7000,
                'scroll_behavior': 'gentle'
            },
            'ebay': {
                'domain_patterns': ['ebay.com', 'ebay.co.uk', 'ebay.ca', 'ebay.de', 'ebay.fr'],
                'title_selectors': [
                    'h1.x-item-title__mainTitle span.ux-textspans--BOLD',
                    'h1[data-testid="x-item-title-textual"]',
                    'h1.it-ttl',
                    'div.vi-swc-lsp h1',
                    'h1.x-item-title-mainTitle span'
                ],
                'price_selectors': [
                    'div.x-price-primary span.ux-textspans',
                    'span.ux-textspans.ux-textspans--DISPLAY.ux-textspans--BOLD',
                    'div.mainPrice span.notranslate',
                    '#prcIsum',
                    'span[itemprop="price"]'
                ],
                'wait_time': 5000,
                'scroll_behavior': 'minimal'
            },
            'storenvy': {
                'domain_patterns': ['storenvy.com'],
                'title_selectors': [
                    'h1.product-name',
                    'h1.product_name',
                    'h1[itemprop="name"]',
                    '.product-header h1'
                ],
                'price_selectors': [
                    'div.price.vprice[itemprop="price"]',
                    'div.price.vprice',
                    'div[itemprop="price"]',
                    '.price.vprice',
                    'span.product-price'
                ],
                'wait_time': 4000,
                'scroll_behavior': 'minimal'
            },
            'roblox': {
                'domain_patterns': ['roblox.com'],
                'title_selectors': [
                    'h1.item-name-container',
                    'div.item-name-container h1',
                    '[data-testid="item-details-name"]',
                    'h1.text-display-1'
                ],
                'price_selectors': [
                    'span.text-robux-lg',
                    'span.icon-robux-price-container',
                    '[data-testid="item-details-price"] .text-robux',
                    'div.price-container span.text-robux'
                ],
                'wait_time': 6000,
                'scroll_behavior': 'targeted',
                'currency': 'robux'
            }
        }
        
        # Advanced user agents with real fingerprints
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0'
        ]
    
    def detect_platform(self, url: str) -> Optional[str]:
        """Detect platform with enhanced domain matching"""
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            
            for platform, config in self.platform_configs.items():
                for pattern in config['domain_patterns']:
                    if pattern in domain:
                        return platform
            return None
        except Exception as e:
            print(f"Error detecting platform: {e}")
            return None
    
    async def setup_ultra_stealth_browser(self, platform: str):
        """Ultra-stealth browser setup with advanced anti-detection"""
        try:
            user_agent = random.choice(self.user_agents)
            
            context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                screen={'width': 1920, 'height': 1080},
                device_scale_factor=1,
                is_mobile=False,
                has_touch=False,
                locale='en-US',
                timezone_id='America/New_York',
                user_agent=user_agent,
                permissions=['geolocation'],
                geolocation={'latitude': 40.7128, 'longitude': -74.0060},
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Cache-Control': 'max-age=0',
                    'DNT': '1'
                }
            )
            
            page = await context.new_page()
            
            # Ultra-advanced stealth scripts
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                    configurable: true
                });
                
                Object.defineProperty(navigator, 'plugins', {
                    get: () => {
                        return {
                            0: {
                                0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                                description: "Portable Document Format",
                                filename: "internal-pdf-viewer",
                                length: 1,
                                name: "Chrome PDF Plugin"
                            },
                            length: 1
                        };
                    }
                });
                
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                
                Object.defineProperty(navigator, 'hardwareConcurrency', {
                    get: () => 8
                });
                
                Object.defineProperty(navigator, 'deviceMemory', {
                    get: () => 8
                });
                
                Object.defineProperty(navigator, 'platform', {
                    get: () => 'Win32'
                });
                
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
                
                window.chrome = {
                    runtime: {
                        onConnect: null,
                        onMessage: null,
                        connect: function() { return { onMessage: null, onDisconnect: null, postMessage: function() {} }; },
                        sendMessage: function() {}
                    }
                };
                
                delete window.__playwright;
                delete window.__puppeteer;
                delete window._phantom;
                delete window._selenium;
                delete window.callPhantom;
                delete window.callSelenium;
                delete window._Selenium_IDE_Recorder;
                
                Object.keys(window).forEach(key => {
                    if (key.includes('cdc_') || key.includes('$cdc_') || key.includes('selenium')) {
                        delete window[key];
                    }
                });
                
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) return 'Intel Inc.';
                    if (parameter === 37446) return 'Intel Iris OpenGL Engine';
                    return getParameter.apply(this, arguments);
                };
            """)
            
            return page
        except Exception as e:
            print(f"Error setting up stealth browser: {e}")
            raise
    
    async def simulate_human_interaction(self, page, platform: str):
        """Advanced human behavior simulation"""
        try:
            config = self.platform_configs.get(platform, {})
            scroll_behavior = config.get('scroll_behavior', 'minimal')
            
            await asyncio.sleep(random.uniform(2, 4))
            
            # Realistic mouse movements
            for _ in range(random.randint(3, 6)):
                x = random.randint(200, 1600)
                y = random.randint(200, 900)
                
                current_x, current_y = 500, 500
                steps = random.randint(15, 25)
                
                for i in range(steps):
                    t = i / steps
                    eased_t = t * t * (3.0 - 2.0 * t)
                    next_x = current_x + (x - current_x) * eased_t
                    next_y = current_y + (y - current_y) * eased_t
                    
                    await page.mouse.move(next_x, next_y)
                    await asyncio.sleep(random.uniform(0.01, 0.02))
                
                current_x, current_y = x, y
                await asyncio.sleep(random.uniform(0.3, 0.8))
            
            # Platform-specific scrolling
            if scroll_behavior == 'targeted':
                await page.evaluate("window.scrollTo({top: 300, behavior: 'smooth'})")
                await asyncio.sleep(2)
                await page.evaluate("window.scrollTo({top: 600, behavior: 'smooth'})")
                await asyncio.sleep(2)
                await page.evaluate("window.scrollTo({top: 200, behavior: 'smooth'})")
                await asyncio.sleep(1)
            elif scroll_behavior == 'gentle':
                for scroll_pos in [200, 400, 300, 500]:
                    await page.evaluate(f"window.scrollTo({{top: {scroll_pos}, behavior: 'smooth'}})")
                    await asyncio.sleep(random.uniform(1, 2))
            elif scroll_behavior == 'minimal':
                await page.evaluate("window.scrollTo({top: 250, behavior: 'smooth'})")
                await asyncio.sleep(1.5)
                
        except Exception as e:
            print(f"Error simulating human interaction: {e}")
    
    async def wait_for_content_load(self, page, platform: str):
        """Advanced content loading detection"""
        try:
            config = self.platform_configs.get(platform, {})
            wait_time = config.get('wait_time', 5000)
            
            try:
                await page.wait_for_load_state('networkidle', timeout=wait_time)
            except:
                await page.wait_for_load_state('domcontentloaded', timeout=wait_time)
            
            if platform == 'walmart':
                try:
                    await page.wait_for_selector('[data-testid="price-wrap"]', timeout=5000)
                except:
                    pass
                await asyncio.sleep(3)
            elif platform == 'etsy':
                try:
                    await page.wait_for_selector('[data-testid="price"]', timeout=5000)
                except:
                    pass
                await asyncio.sleep(2)
            elif platform == 'amazon':
                try:
                    await page.wait_for_selector('.a-price', timeout=3000)
                except:
                    pass
            
            await page.wait_for_timeout(2000)
            return True
        except Exception as e:
            print(f"Error waiting for content load: {e}")
            return True
    
    async def extract_accurate_price(self, page, platform: str, product_title: str = None) -> Optional[float]:
        """Ultra-accurate price extraction with context validation"""
        try:
            config = self.platform_configs.get(platform, {})
            price_selectors = config.get('price_selectors', [])
            exclude_selectors = config.get('exclude_selectors', [])
            
            print(f"Extracting price for {platform} with {len(price_selectors)} selectors...")
            
            # Exclude unwanted price elements
            if exclude_selectors:
                for exclude_selector in exclude_selectors:
                    try:
                        excluded_elements = await page.query_selector_all(exclude_selector)
                        for element in excluded_elements:
                            await page.evaluate('(element) => element.remove()', element)
                    except:
                        continue
            
            all_prices = []
            
            for i, selector in enumerate(price_selectors):
                try:
                    elements = await page.query_selector_all(selector)
                    print(f"Selector {i+1} ({selector}): Found {len(elements)} elements")
                    
                    for element in elements:
                        try:
                            price_text = await element.text_content()
                            
                            price_attr = None
                            try:
                                price_attr = await element.get_attribute('content')
                                if not price_attr:
                                    price_attr = await element.get_attribute('data-price')
                            except:
                                pass
                            
                            # Validate price context for Walmart
                            if product_title and platform == 'walmart':
                                parent_html = await page.evaluate('''
                                    (element) => {
                                        let parent = element.closest('[data-testid="product-page"]') || 
                                                   element.closest('main') ||
                                                   element.closest('[data-automation-id="product-title"]').closest('div');
                                        return parent ? parent.innerHTML.substring(0, 500) : '';
                                    }
                                ''', element)
                                
                                if 'recommendation' in parent_html.lower() or 'similar' in parent_html.lower():
                                    continue
                            
                            if price_text:
                                price = await self.extract_price_from_text(price_text, platform)
                                if price and self.validate_price_range(price, platform):
                                    all_prices.append({
                                        'price': price,
                                        'text': price_text.strip(),
                                        'selector': selector,
                                        'source': 'text'
                                    })
                                    print(f"Found valid price: ${price} from text: '{price_text.strip()}'")
                            
                            if price_attr:
                                price = await self.extract_price_from_text(price_attr, platform)
                                if price and self.validate_price_range(price, platform):
                                    all_prices.append({
                                        'price': price,
                                        'text': price_attr,
                                        'selector': selector,
                                        'source': 'attribute'
                                    })
                                    print(f"Found valid price: ${price} from attribute: '{price_attr}'")
                                    
                        except Exception as e:
                            continue
                    
                    if all_prices:
                        break
                        
                except Exception as e:
                    print(f"Selector {selector} failed: {e}")
                    continue
            
            if not all_prices:
                print(f"No valid prices found for {platform}")
                return None
            
            return self.select_best_price(all_prices, platform)
            
        except Exception as e:
            print(f"Error extracting price for {platform}: {e}")
            return None
    
    async def extract_price_from_text(self, price_text: str, platform: str) -> Optional[float]:
        """Enhanced price extraction with platform-specific logic"""
        if not price_text:
            return None
        
        try:
            cleaned_text = price_text.strip().replace(',', '').replace(' ', '')
            
            if platform == 'roblox':
                robux_patterns = [
                    r'(\d{1,6})',
                    r'(\d{1,3}(?:,\d{3})*)'
                ]
                for pattern in robux_patterns:
                    matches = re.findall(pattern, cleaned_text.replace(',', ''))
                    if matches:
                        try:
                            price = float(matches[0])
                            if 1 <= price <= 999999:
                                return price
                        except:
                            continue
            else:
                currency_patterns = [
                    r'\$(\d{1,4}(?:\.\d{1,2})?)',
                    r'USD\s*(\d{1,4}(?:\.\d{1,2})?)',
                    r'(\d{1,4}(?:\.\d{1,2})?)\s*\$',
                    r'(\d{1,4}\.\d{2})',
                    r'(\d{1,4})'
                ]
                
                for pattern in currency_patterns:
                    matches = re.findall(pattern, cleaned_text)
                    if matches:
                        for match in matches:
                            try:
                                price = float(match)
                                if self.validate_price_range(price, platform):
                                    return price
                            except:
                                continue
            
            return None
        except Exception as e:
            print(f"Error extracting price from '{price_text}': {e}")
            return None
    
    def validate_price_range(self, price: float, platform: str) -> bool:
        """Validate if price is in reasonable range for platform"""
        if platform == 'roblox':
            return 1 <= price <= 999999
        else:
            return 0.01 <= price <= 99999
    
    def select_best_price(self, prices: List[Dict], platform: str) -> float:
        """Select the most accurate price from candidates"""
        if not prices:
            return None
        
        prices.sort(key=lambda x: x.get('selector', ''))
        
        if platform == 'walmart':
            main_prices = [p for p in prices if 'buybox' in p.get('selector', '') or 'add-to-cart' in p.get('selector', '')]
            if main_prices:
                return main_prices[0]['price']
        
        return prices[0]['price']
    
    async def extract_product_title(self, page, platform: str) -> Optional[str]:
        """Extract product title for context validation"""
        try:
            config = self.platform_configs.get(platform, {})
            title_selectors = config.get('title_selectors', [])
            
            for selector in title_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        title = await element.text_content()
                        if title and title.strip():
                            return title.strip()
                except:
                    continue
            
            return None
        except Exception as e:
            print(f"Error extracting title: {e}")
            return None
    
    async def scrape_product(self, url: str) -> Optional[Tuple[str, float]]:
        """Main scraping method with ultra-stealth and accuracy"""
        platform = self.detect_platform(url)
        if not platform:
            print(f"Unsupported platform for URL: {url}")
            return None
        
        print(f"Scraping {platform} with ultra-stealth mode: {url}")
        
        async with async_playwright() as p:
            self.browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--disable-site-isolation-trials',
                    '--disable-web-security',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--disable-canvas-aa',
                    '--disable-2d-canvas-clip-aa',
                    '--disable-gl-drawing-for-tests',
                    '--disable-dev-tools',
                    '--no-first-run',
                    '--no-zygote',
                    '--no-sandbox',
                    '--disable-gpu',
                    '--disable-setuid-sandbox',
                    '--disable-extensions',
                    '--disable-default-apps',
                    '--disable-sync',
                    '--disable-translate',
                    '--hide-scrollbars',
                    '--mute-audio',
                    '--no-default-browser-check',
                    '--disable-logging',
                    '--disable-permissions-api',
                    '--disable-presentation-api',
                    '--disable-remote-fonts',
                    '--disable-speech-api'
                ]
            )
            
            try:
                page = await self.setup_ultra_stealth_browser(platform)
                
                print(f"Navigating to: {url}")
                
                # Navigate with fallback strategies
                navigation_success = False
                for attempt in range(3):
                    try:
                        if attempt == 0:
                            response = await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                        elif attempt == 1:
                            response = await page.goto(url, wait_until='networkidle', timeout=30000)
                        else:
                            response = await page.goto(url, wait_until='load', timeout=30000)
                        
                        if response and response.status < 400:
                            navigation_success = True
                            break
                            
                    except Exception as e:
                        print(f"Navigation attempt {attempt + 1} failed: {e}")
                        if attempt < 2:
                            await asyncio.sleep(2)
                            continue
                        else:
                            raise
                
                if not navigation_success:
                    print("All navigation attempts failed")
                    return None
                
                await self.wait_for_content_load(page, platform)
                await self.simulate_human_interaction(page, platform)
                
                title = await self.extract_product_title(page, platform)
                if not title:
                    print(f"Could not extract title for {platform}")
                    title = f"Product from {platform.title()}"
                
                price = await self.extract_accurate_price(page, platform, title)
                
                if price:
                    if platform == 'roblox':
                        print(f"✅ Successfully scraped {platform}: {title[:50]}... - {int(price)} Robux")
                    else:
                        print(f"✅ Successfully scraped {platform}: {title[:50]}... - ${price:.2f}")
                    return title, price
                else:
                    print(f"❌ Failed to extract price for {platform}")
                    
                    try:
                        content = await page.content()
                        debug_file = f'debug_{platform}_{int(time.time())}.html'
                        with open(debug_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"💾 Saved debug HTML: {debug_file}")
                    except Exception:
                        pass
                    
                    return None
                
            except Exception as e:
                print(f"❌ Error scraping {platform}: {str(e)}")
                return None
            finally:
                await self.browser.close()
    
    @staticmethod
    def get_platform_info() -> Dict[str, Dict[str, str]]:
        """Get information about supported platforms"""
        return {
            'amazon': {'name': 'Amazon', 'icon': '🛒'},
            'ebay': {'name': 'eBay', 'icon': '🏷️'},
            'etsy': {'name': 'Etsy', 'icon': '🎨'},
            'walmart': {'name': 'Walmart', 'icon': '🏪'},
            'storenvy': {'name': 'Storenvy', 'icon': '🏬'},
            'roblox': {'name': 'Roblox', 'icon': '🎮'}
        }


class ScrapingRetryManager:
    """Manages retries and error handling for scraping operations"""
    
    def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
    
    async def execute_with_retry(self, scraper_func, *args, **kwargs):
        """Execute scraping function with retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                result = await scraper_func(*args, **kwargs)
                if result:
                    return result
                    
                if attempt < self.max_retries - 1:
                    wait_time = self.backoff_factor ** attempt
                    print(f"🔄 Attempt {attempt + 1} failed, retrying in {wait_time:.1f}s...")
                    await asyncio.sleep(wait_time)
                    
            except Exception as e:
                last_exception = e
                print(f"❌ Attempt {attempt + 1} failed with error: {e}")
                
                if attempt < self.max_retries - 1:
                    wait_time = self.backoff_factor ** attempt
                    print(f"🔄 Retrying in {wait_time:.1f}s...")
                    await asyncio.sleep(wait_time)
        
        print(f"❌ All {self.max_retries} attempts failed")
        if last_exception:
            raise last_exception
        return None


class StorenvyPriceTracker:
    """Multi-platform price tracker with enhanced stealth scraping"""
    
    def __init__(self, db_path: str = "storenvy_tracker.db"):
        self.db_path = db_path
        self.scraper = EnhancedMultiPlatformScraper()
        self.retry_manager = ScrapingRetryManager(max_retries=3, backoff_factor=2.0)
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
            if not platform:
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
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                ''', (user_id,))
            else:
                cursor.execute('''
                    SELECT id, url, platform, title, target_price, last_price, last_checked
                    FROM tracked_products
                    ORDER BY created_at DESC
                ''')
            
            products = []
            platform_info = EnhancedMultiPlatformScraper.get_platform_info()
            
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
                ORDER BY p.created_at DESC
            ''')
            
            products = []
            platform_info = EnhancedMultiPlatformScraper.get_platform_info()
            
            for row in cursor.fetchall():
                try:
                    platform = row[3] or 'storenvy'
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
    
    async def scrape_product_with_retry(self, url: str) -> Optional[Tuple[str, float]]:
        """Scrape product with enhanced retry logic and validation"""
        try:
            result = await self.retry_manager.execute_with_retry(
                self.scraper.scrape_product, 
                url
            )
            
            if result:
                title, price = result
                platform = self.scraper.detect_platform(url)
                
                # Additional validation for specific platforms
                if platform == 'walmart':
                    # Validate that we got the correct product price
                    if price and 0.01 <= price <= 99999:
                        print(f"✅ Walmart price validation passed: ${price:.2f}")
                    else:
                        print(f"⚠️ Walmart price validation failed: {price}")
                        return None
                
                return result
            
            return None
            
        except Exception as e:
            print(f"Enhanced scraping failed for {url}: {e}")
            return None

    async def scrape_product(self, url: str) -> Optional[Tuple[str, float]]:
        """Scrape product using the enhanced multi-platform scraper with retry"""
        try:
            # Use the enhanced scraper with retry logic
            return await self.scrape_product_with_retry(url)
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
TagTracker
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
TagTracker
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
        """Check all tracked products for all users with enhanced accuracy"""
        try:
            products = self.get_all_products_for_checking()
            
            if not products:
                print("No products to check")
                return
            
            print(f"🔄 Checking {len(products)} products for all users with enhanced scraper")
            
            for product in products:
                try:
                    platform_name = product.get('platform_name', 'Unknown')
                    platform = product.get('platform', 'unknown')
                    print(f"📦 Checking {platform_name} product: {product['url'][:50]}...")
                    
                    # Scrape product with enhanced accuracy
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
            
            print(f"✅ Finished checking all products with enhanced accuracy")
            
        except Exception as e:
            print(f"Error in check_all_products: {e}")
    
    def get_supported_platforms(self) -> Dict[str, Dict[str, str]]:
        """Get information about supported platforms"""
        try:
            return EnhancedMultiPlatformScraper.get_platform_info()
        except Exception as e:
            print(f"Error getting supported platforms: {e}")
            return {}


# Test function for the enhanced tracker
async def test_enhanced_tracker():
    """Test the enhanced tracker functionality with problematic URLs"""
    try:
        tracker = StorenvyPriceTracker()
        
        print("🧪 Testing Enhanced TagTracker with Ultra-Stealth Scraper")
        print("=" * 70)
        
        # Test the problematic Walmart URL
        test_urls = [
            ("https://www.walmart.com/ip/JW-SAGA-VILLIAN-1/14141570021?classType=REGULAR&athbdg=L1800", 80.00),
            ("https://www.amazon.com/dp/B08N5WRWNW", 100.00),
            ("https://www.etsy.com/listing/1234567890/test-product", 50.00),
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
                
                # Test scraping
                print(f"🔍 Testing enhanced scraping for {platform}...")
                result = await tracker.scrape_product(url)
                
                if result:
                    title, price = result
                    if platform == 'roblox':
                        print(f"✅ Scraping SUCCESS: {title[:50]}... - {int(price)} Robux")
                        if price <= target_price:
                            print(f"🎮 DEAL ALERT! Price {int(price)} is below target {int(target_price)}!")
                    else:
                        print(f"✅ Scraping SUCCESS: {title[:50]}... - ${price:.2f}")
                        if price <= target_price:
                            print(f"💰 DEAL ALERT! Price ${price:.2f} is below target ${target_price:.2f}!")
                else:
                    print(f"❌ Scraping FAILED for {platform}")
                
            except Exception as e:
                print(f"❌ Failed to test {url}: {e}")
            
            print(f"⏳ Waiting 5 seconds before next test...")
            await asyncio.sleep(5)
        
        # Test getting tracked products
        products = tracker.get_tracked_products(1)
        print(f"\n📋 Currently tracking {len(products)} products:")
        for product in products:
            platform_name = product.get('platform_name', 'Unknown')
            status = "🎯 Below Target!" if product['status'] == 'below_target' else "👁️ Monitoring"
            print(f"  - {status} {platform_name}: {product['url'][:50]}...")
            
        print("\n✅ Enhanced tracker test completed successfully")
        
    except Exception as e:
        print(f"❌ Error in test_enhanced_tracker: {e}")


if __name__ == "__main__":
    print("🚀 Enhanced TagTracker - Ultra-Stealth E-commerce Scraper")
    print("=" * 60)
    print("🛡️  Advanced bot detection bypass")
    print("🎯 Accurate price extraction (fixes Walmart/Etsy issues)")
    print("🔄 Intelligent retry mechanisms")
    print("💾 Enhanced database management")
    print("=" * 60)
    
    # Run the test
    asyncio.run(test_enhanced_tracker())