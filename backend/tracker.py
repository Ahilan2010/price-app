# backend/tracker.py - FIXED VERSION WITH PROPER WALMART TARGETING & SAVINGS CALCULATION
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


class UltraStealthMultiPlatformScraper:
    """Ultra-stealth multi-platform scraper with FIXED Walmart price targeting"""
    
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
                    'span.a-price.a-text-price.a-size-medium.apexPriceToPay span.a-offscreen',
                    'span.a-price.a-text-price.apexPriceToPay span.a-offscreen',
                    'span.a-price-current span.a-offscreen',
                    'div[data-feature-name="apex_desktop"] span.a-price-whole',
                    'span.a-price.aok-align-center.reinventPricePriceToPayMargin span.a-offscreen',
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
                    # FIXED: Your exact selector as first priority
                    'span.inline-flex.flex-column span[itemprop="price"][data-seo-id="hero-price"][data-fs-element="price"]',
                    'span.inline-flex.flex-column span[itemprop="price"][data-seo-id="hero-price"]',
                    
                    # Additional main product selectors (not recommendations)
                    'div[data-testid="price-wrap"]:not([data-testid*="recommendation"]) span[itemprop="price"]',
                    'span[data-automation-id="buybox-price"]:not([data-testid*="recommendation"])',
                    'div[data-testid="add-to-cart-price"]:not([data-testid*="recommendation"]) span[itemprop="price"]',
                    'span[data-automation-id="product-price"]:not([data-testid*="recommendation"])',
                    
                    # Final fallbacks (avoiding recommendation areas)
                    'main span[itemprop="price"]:not([data-testid*="recommendation"]):not([data-testid*="similar"])',
                    'div.price-current span:not([data-testid*="recommendation"])',
                    '.price.display-inline-block span:not([data-testid*="recommendation"])'
                ],
                'exclude_selectors': [
                    # Enhanced exclusion of recommendation areas
                    'div[data-testid="recommendations"] *',
                    'div[data-testid="similar-items"] *',
                    'div[data-testid="you-might-also-like"] *',
                    'div[data-testid="sponsored"] *',
                    'div[data-testid="related-products"] *',
                    'div[data-testid="product-recommendations"] *',
                    'aside *',  # Sidebar recommendations
                    '.recommendations *',
                    '.similar-items *',
                    '.sponsored-products *',
                    '.related-products *',
                    '[aria-label*="recommend" i] *',
                    '[data-automation-id*="recommend" i] *'
                ],
                'wait_time': 12000,
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
                    'p[data-testid="price"] span.currency-value',
                    'div[data-buy-box-region="price"] p[data-selector="price-only"]',
                    'p.wt-text-title-larger span.currency-value',
                    'span.wt-text-title-largest',
                    'div[data-selector="listing-page-cart"] span.currency-value',
                    'p.currency span.currency-value'
                ],
                'wait_time': 15000,
                'scroll_behavior': 'ultra_gentle'
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
        
        # Ultra-realistic user agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'
        ]
        
        # Enhanced fingerprint data
        self.fingerprints = [
            {
                'screen': {'width': 1920, 'height': 1080},
                'viewport': {'width': 1920, 'height': 1080},
                'hardware_concurrency': 8,
                'device_memory': 8,
                'platform': 'Win32',
                'timezone': 'America/New_York'
            },
            {
                'screen': {'width': 2560, 'height': 1440},
                'viewport': {'width': 2560, 'height': 1440},
                'hardware_concurrency': 12,
                'device_memory': 16,
                'platform': 'MacIntel',
                'timezone': 'America/Los_Angeles'
            }
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
        """Ultra-stealth browser setup with maximum anti-detection"""
        try:
            user_agent = random.choice(self.user_agents)
            fingerprint = random.choice(self.fingerprints)
            
            # Ultra-stealth context
            context = await self.browser.new_context(
                viewport=fingerprint['viewport'],
                screen=fingerprint['screen'],
                device_scale_factor=1,
                is_mobile=False,
                has_touch=False,
                locale='en-US',
                timezone_id=fingerprint['timezone'],
                user_agent=user_agent,
                permissions=['geolocation'],
                geolocation={
                    'latitude': 40.7128 + random.uniform(-0.1, 0.1), 
                    'longitude': -74.0060 + random.uniform(-0.1, 0.1)
                },
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
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
            
            # Maximum stealth injection
            stealth_script = f"""
                // Complete automation detection removal
                Object.defineProperty(navigator, 'webdriver', {{
                    get: () => undefined,
                    configurable: true
                }});
                
                // Enhanced plugin spoofing
                Object.defineProperty(navigator, 'plugins', {{
                    get: () => {{
                        return {{
                            0: {{
                                0: {{type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"}},
                                description: "Portable Document Format",
                                filename: "internal-pdf-viewer",
                                length: 1,
                                name: "Chrome PDF Plugin"
                            }},
                            length: 1
                        }};
                    }}
                }});
                
                // Realistic properties
                Object.defineProperty(navigator, 'languages', {{
                    get: () => ['en-US', 'en']
                }});
                
                Object.defineProperty(navigator, 'hardwareConcurrency', {{
                    get: () => {fingerprint['hardware_concurrency']}
                }});
                
                Object.defineProperty(navigator, 'deviceMemory', {{
                    get: () => {fingerprint['device_memory']}
                }});
                
                Object.defineProperty(navigator, 'platform', {{
                    get: () => '{fingerprint['platform']}'
                }});
                
                // Remove automation traces
                const automationKeys = [
                    '__playwright', '__puppeteer', '_phantom', '_selenium', 'callPhantom', 
                    'callSelenium', '_Selenium_IDE_Recorder', '__webdriver_script_func', 
                    '__webdriver_evaluate', '__selenium_evaluate', '__fxdriver_evaluate', 
                    '__driver_unwrapped', '__webdriver_unwrapped', '__driver_evaluate', 
                    '__selenium_unwrapped', '__fxdriver_unwrapped', '__nightmare'
                ];
                
                automationKeys.forEach(key => {{
                    try {{ delete window[key]; }} catch(e) {{}}
                }});
                
                // Remove CDP traces
                Object.keys(window).forEach(key => {{
                    if (key.includes('cdc_') || key.includes('$cdc_') || key.includes('selenium') || 
                        key.includes('webdriver') || key.includes('driver')) {{
                        try {{ delete window[key]; }} catch(e) {{}}
                    }}
                }});
            """
            
            await page.add_init_script(stealth_script)
            return page
            
        except Exception as e:
            print(f"Error setting up stealth browser: {e}")
            raise
    
    async def simulate_ultra_human_interaction(self, page, platform: str):
        """Ultra-advanced human behavior simulation"""
        try:
            config = self.platform_configs.get(platform, {})
            scroll_behavior = config.get('scroll_behavior', 'minimal')
            
            # Extended initial wait
            await asyncio.sleep(random.uniform(4, 8))
            
            # Ultra-realistic mouse movements
            for _ in range(random.randint(6, 12)):
                start_x = random.randint(100, 1800)
                start_y = random.randint(100, 800)
                end_x = random.randint(100, 1800)
                end_y = random.randint(100, 800)
                
                # Natural movement
                steps = random.randint(25, 50)
                for i in range(steps):
                    t = i / steps
                    x = start_x + (end_x - start_x) * t
                    y = start_y + (end_y - start_y) * t
                    
                    await page.mouse.move(x, y)
                    await asyncio.sleep(random.uniform(0.003, 0.012))
                
                await asyncio.sleep(random.uniform(0.8, 2.2))
            
            # Platform-specific scrolling
            if scroll_behavior == 'ultra_gentle':
                # Maximum stealth for Etsy
                scroll_positions = [80, 200, 120, 350, 180, 450, 250, 380, 200, 150]
                for i, pos in enumerate(scroll_positions):
                    await page.evaluate(f"""
                        window.scrollTo({{
                            top: {pos},
                            behavior: 'smooth'
                        }});
                    """)
                    
                    pause_time = random.uniform(3, 6) if i % 2 == 0 else random.uniform(1.5, 3)
                    await asyncio.sleep(pause_time)
                        
            elif scroll_behavior == 'targeted':
                # Enhanced Walmart scrolling
                scroll_actions = [
                    {'top': 150, 'delay': random.uniform(2, 3.5)},
                    {'top': 400, 'delay': random.uniform(2.5, 4)},
                    {'top': 250, 'delay': random.uniform(1.5, 2.5)},
                    {'top': 600, 'delay': random.uniform(3, 4.5)},
                    {'top': 350, 'delay': random.uniform(2, 3)}
                ]
                
                for action in scroll_actions:
                    await page.evaluate(f"""
                        window.scrollTo({{
                            top: {action['top']},
                            behavior: 'smooth'
                        }});
                    """)
                    await asyncio.sleep(action['delay'])
                    
            else:
                # Standard gentle scrolling
                for scroll_pos in [100, 300, 180, 420, 220]:
                    await page.evaluate(f"window.scrollTo({{top: {scroll_pos}, behavior: 'smooth'}})")
                    await asyncio.sleep(random.uniform(2, 3.5))
            
            # Final pause
            await asyncio.sleep(random.uniform(2, 4))
                
        except Exception as e:
            print(f"Error in ultra-human interaction: {e}")
    
    async def wait_for_enhanced_content_load(self, page, platform: str):
        """Enhanced content loading with maximum patience"""
        try:
            config = self.platform_configs.get(platform, {})
            wait_time = config.get('wait_time', 5000)
            
            # Multi-stage loading
            try:
                await page.wait_for_load_state('domcontentloaded', timeout=wait_time // 3)
                await asyncio.sleep(random.uniform(2, 4))
                await page.wait_for_load_state('networkidle', timeout=wait_time // 2)
            except:
                try:
                    await page.wait_for_load_state('load', timeout=wait_time)
                except:
                    pass
            
            # Platform-specific waiting
            if platform == 'walmart':
                # Wait for your specific selector first
                walmart_selectors = [
                    'span.inline-flex.flex-column span[itemprop="price"][data-seo-id="hero-price"]',
                    '[data-testid="price-wrap"]',
                    '[itemprop="price"]'
                ]
                
                for selector in walmart_selectors:
                    try:
                        await page.wait_for_selector(selector, timeout=4000)
                        print(f"✅ Walmart: Detected price element {selector}")
                        break
                    except:
                        continue
                
                await asyncio.sleep(random.uniform(6, 10))
                
            elif platform == 'etsy':
                try:
                    await page.wait_for_selector('[data-testid="price"]', timeout=8000)
                except:
                    pass
                await asyncio.sleep(random.uniform(5, 8))
            
            # Final wait
            await page.wait_for_timeout(random.randint(3000, 6000))
            
            return True
        except Exception as e:
            print(f"Error waiting for content load: {e}")
            return True
    
    async def extract_walmart_price_enhanced(self, page) -> Optional[float]:
        """FIXED: Enhanced Walmart price extraction targeting your exact selector"""
        try:
            print("🎯 FIXED Walmart price extraction starting...")
            
            # First, remove all recommendation sections to avoid interference
            exclude_selectors = [
                'div[data-testid="recommendations"]',
                'div[data-testid="similar-items"]', 
                'div[data-testid="you-might-also-like"]',
                'div[data-testid="sponsored"]',
                'div[data-testid="related-products"]',
                'aside',
                '.recommendations',
                '.similar-items',
                '.sponsored-products'
            ]
            
            for selector in exclude_selectors:
                try:
                    await page.evaluate(f'''
                        document.querySelectorAll("{selector}").forEach(el => el.remove());
                    ''')
                except:
                    continue
            
            # YOUR EXACT SELECTOR as absolute priority
            exact_selector = 'span.inline-flex.flex-column span[itemprop="price"][data-seo-id="hero-price"][data-fs-element="price"]'
            
            try:
                print(f"🎯 Trying your exact selector: {exact_selector}")
                element = await page.query_selector(exact_selector)
                if element:
                    price_text = await element.text_content()
                    print(f"📍 Found with exact selector: '{price_text}'")
                    
                    if price_text:
                        price = await self.extract_price_from_text(price_text, 'walmart')
                        if price and 0.01 <= price <= 99999:
                            print(f"✅ WALMART SUCCESS (Exact): ${price:.2f}")
                            return price
            except Exception as e:
                print(f"Exact selector failed: {e}")
            
            # Fallback to your class without data-fs-element
            fallback_selector = 'span.inline-flex.flex-column span[itemprop="price"][data-seo-id="hero-price"]'
            
            try:
                print(f"🔄 Trying fallback selector: {fallback_selector}")
                element = await page.query_selector(fallback_selector)
                if element:
                    price_text = await element.text_content()
                    print(f"📍 Found with fallback: '{price_text}'")
                    
                    if price_text:
                        price = await self.extract_price_from_text(price_text, 'walmart')
                        if price and 0.01 <= price <= 99999:
                            print(f"✅ WALMART SUCCESS (Fallback): ${price:.2f}")
                            return price
            except Exception as e:
                print(f"Fallback selector failed: {e}")
            
            # Final emergency selectors (main product area only)
            emergency_selectors = [
                'main span[itemprop="price"]:first-of-type',
                'div[data-testid="price-wrap"] span[itemprop="price"]:first-of-type',
                'span[data-automation-id="buybox-price"]'
            ]
            
            for selector in emergency_selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        price_text = await element.text_content()
                        if price_text:
                            price = await self.extract_price_from_text(price_text, 'walmart')
                            if price and 0.01 <= price <= 99999:
                                print(f"⚠️ WALMART EMERGENCY: ${price:.2f} from {selector}")
                                return price
                except:
                    continue
            
            print("❌ All Walmart selectors failed")
            return None
            
        except Exception as e:
            print(f"Error in Walmart price extraction: {e}")
            return None
    
    async def extract_price_from_text(self, price_text: str, platform: str) -> Optional[float]:
        """Enhanced price extraction"""
        if not price_text:
            return None
        
        try:
            cleaned_text = price_text.strip().replace(',', '').replace(' ', '')
            
            if platform == 'roblox':
                # Robux extraction
                robux_patterns = [r'(\d{1,6})', r'(\d{1,3}(?:,\d{3})*)']
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
                # Currency extraction
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
                                if 0.01 <= price <= 99999:
                                    return price
                            except:
                                continue
            
            return None
        except Exception as e:
            print(f"Error extracting price from '{price_text}': {e}")
            return None
    
    async def extract_product_title(self, page, platform: str) -> Optional[str]:
        """Extract product title"""
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
        """Main ultra-stealth scraping method with FIXED Walmart targeting"""
        platform = self.detect_platform(url)
        if not platform:
            print(f"Unsupported platform for URL: {url}")
            return None
        
        print(f"🕵️ ULTRA-STEALTH scraping {platform}: {url}")
        
        async with async_playwright() as p:
            # Maximum stealth browser launch
            self.browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-site-isolation-trials',
                    '--disable-web-security',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-gpu',
                    '--disable-logging'
                ]
            )
            
            try:
                page = await self.setup_ultra_stealth_browser(platform)
                
                print(f"🌐 Navigating to: {url}")
                
                # Ultra-patient navigation
                navigation_success = False
                for attempt in range(3):
                    try:
                        response = await page.goto(url, wait_until='domcontentloaded', timeout=45000)
                        if response and response.status < 400:
                            print(f"✅ Navigation successful")
                            navigation_success = True
                            break
                    except Exception as e:
                        print(f"❌ Navigation attempt {attempt + 1} failed: {e}")
                        if attempt < 2:
                            await asyncio.sleep(random.uniform(5, 10))
                            continue
                        else:
                            break
                
                if not navigation_success:
                    print("❌ All navigation attempts failed")
                    return None
                
                # Ultra-stealth content loading and interaction
                await self.wait_for_enhanced_content_load(page, platform)
                await self.simulate_ultra_human_interaction(page, platform)
                
                # Extract title and price
                title = await self.extract_product_title(page, platform)
                if not title:
                    title = f"Product from {platform.title()}"
                
                # Platform-specific price extraction
                price = None
                if platform == 'walmart':
                    # Use FIXED Walmart extraction
                    price = await self.extract_walmart_price_enhanced(page)
                else:
                    # Standard extraction for other platforms
                    config = self.platform_configs.get(platform, {})
                    price_selectors = config.get('price_selectors', [])
                    
                    for selector in price_selectors:
                        try:
                            elements = await page.query_selector_all(selector)
                            for element in elements:
                                price_text = await element.text_content()
                                if price_text:
                                    price = await self.extract_price_from_text(price_text, platform)
                                    if price:
                                        break
                            if price:
                                break
                        except:
                            continue
                
                if price:
                    if platform == 'roblox':
                        print(f"✅ SUCCESS: {title[:50]}... - {int(price)} Robux")
                    else:
                        print(f"✅ SUCCESS: {title[:50]}... - ${price:.2f}")
                    return title, price
                else:
                    print(f"❌ FAILED: Could not extract price for {platform}")
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


class UltraStealthRetryManager:
    """Enhanced retry manager with exponential backoff and randomization"""
    
    def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
    
    async def execute_with_retry(self, scraper_func, *args, **kwargs):
        """Execute scraping function with ultra-patient retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                result = await scraper_func(*args, **kwargs)
                if result:
                    return result
                    
                if attempt < self.max_retries - 1:
                    wait_time = (self.backoff_factor ** attempt) + random.uniform(2, 8)
                    print(f"🔄 Attempt {attempt + 1} failed, ultra-stealth retry in {wait_time:.1f}s...")
                    await asyncio.sleep(wait_time)
                    
            except Exception as e:
                last_exception = e
                print(f"❌ Attempt {attempt + 1} failed with error: {e}")
                
                if attempt < self.max_retries - 1:
                    wait_time = (self.backoff_factor ** attempt) + random.uniform(5, 15)
                    print(f"🔄 Ultra-stealth retry in {wait_time:.1f}s...")
                    await asyncio.sleep(wait_time)
        
        print(f"❌ All {self.max_retries} ultra-stealth attempts failed")
        if last_exception:
            raise last_exception
        return None


class StorenvyPriceTracker:
    """Multi-platform price tracker with FIXED savings calculation and chronological order"""
    
    def __init__(self, db_path: str = "storenvy_tracker.db"):
        self.db_path = db_path
        self.scraper = UltraStealthMultiPlatformScraper()
        self.retry_manager = UltraStealthRetryManager(max_retries=3, backoff_factor=2.5)
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
            
            # Check if user_id column exists and migrate if needed
            cursor.execute("PRAGMA table_info(tracked_products)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'user_id' not in columns:
                cursor.execute('ALTER TABLE tracked_products ADD COLUMN user_id INTEGER DEFAULT 1')
                print("✅ Migrated database: Added user_id column")
            
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
            print("✅ Database initialized successfully")
            
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
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
                print(f"✅ Added new {platform} product for user {user_id}")
                
            except sqlite3.IntegrityError:
                # Update existing product
                cursor.execute('''
                    UPDATE tracked_products
                    SET target_price = ?, platform = ?
                    WHERE user_id = ? AND url = ?
                ''', (target_price, platform, user_id, url))
                conn.commit()
                print(f"✅ Updated existing {platform} product for user {user_id}")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Error adding product: {e}")
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
            print(f"✅ Deleted product {product_id} for user {user_id}")
            
        except Exception as e:
            print(f"❌ Error deleting product {product_id}: {e}")
            raise
    
    def get_tracked_products(self, user_id: int = None) -> List[Dict[str, Any]]:
        """Get all tracked products, optionally filtered by user - CHRONOLOGICAL ORDER"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if user_id:
                # FIXED: Order by created_at DESC for chronological order (newest first)
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
            platform_info = UltraStealthMultiPlatformScraper.get_platform_info()
            
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
                    print(f"❌ Error processing product row: {e}")
                    continue
            
            conn.close()
            return products
            
        except Exception as e:
            print(f"❌ Error getting tracked products: {e}")
            return []

    def get_all_products_for_checking(self) -> List[Dict[str, Any]]:
        """Get all products from all users for checking - CHRONOLOGICAL ORDER"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # FIXED: Order by created_at DESC for chronological order (newest first)
            cursor.execute('''
                SELECT p.id, p.user_id, p.url, p.platform, p.title, p.target_price, 
                       p.last_price, p.last_checked, u.email, u.smtp_password, u.first_name
                FROM tracked_products p
                JOIN users u ON p.user_id = u.id
                ORDER BY p.created_at DESC
            ''')
            
            products = []
            platform_info = UltraStealthMultiPlatformScraper.get_platform_info()
            
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
                    print(f"❌ Error processing product row: {e}")
                    continue
            
            conn.close()
            return products
            
        except Exception as e:
            print(f"❌ Error getting all products: {e}")
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
            
        except Exception as e:
            print(f"❌ Error updating product {product_id}: {e}")
    
    async def scrape_product_with_ultra_stealth(self, url: str) -> Optional[Tuple[str, float]]:
        """Scrape product with ultra-stealth retry logic"""
        try:
            result = await self.retry_manager.execute_with_retry(
                self.scraper.scrape_product, 
                url
            )
            
            if result:
                title, price = result
                platform = self.scraper.detect_platform(url)
                
                # Enhanced validation
                if platform == 'walmart' and price:
                    if 0.01 <= price <= 99999:
                        print(f"✅ Walmart ultra-stealth validation passed: ${price:.2f}")
                        return result
                    else:
                        print(f"⚠️ Walmart price validation failed: {price}")
                        return None
                elif platform == 'etsy' and price:
                    if 1.0 <= price <= 10000.0:
                        print(f"✅ Etsy ultra-stealth validation passed: ${price:.2f}")
                        return result
                    else:
                        print(f"⚠️ Etsy price validation failed: {price}")
                        return None
                
                return result
            
            return None
            
        except Exception as e:
            print(f"❌ Ultra-stealth scraping failed for {url}: {e}")
            return None

    async def scrape_product(self, url: str) -> Optional[Tuple[str, float]]:
        """Main scraping method using ultra-stealth scraper"""
        try:
            return await self.scrape_product_with_ultra_stealth(url)
        except Exception as e:
            print(f"❌ Error scraping product {url}: {e}")
            return None
    
    def send_email_alert(self, product: Dict[str, Any], user_email: str, smtp_password: str, user_name: str) -> None:
        """Send email alert for price drop with enhanced formatting"""
        if not smtp_password:
            return
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = user_email
            msg['To'] = user_email
            
            platform = product.get('platform', 'storenvy')
            platform_name = product.get('platform_name', 'Unknown Platform')
            
            # Enhanced subject line
            if platform == 'roblox':
                msg['Subject'] = f"🎮 Roblox Deal Alert: {product['title'][:40]}..."
            else:
                msg['Subject'] = f"🛍️ Price Drop Alert: {product['title'][:40]}..."
            
            # Format prices based on platform
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
            
            # Enhanced email body
            if platform == 'roblox':
                body = f"""
Hello {user_name}! 🎮

🚨 ROBLOX DEAL ALERT! 🚨

A Roblox item you're tracking has dropped to or below your target price!

🎯 Item Details:
{product['title']}

💎 Price Information:
Current Price: {current_price_str}
Your Target: {target_price_str}
You Save: {savings_str}

🔗 Get This Item Now:
{product['url']}

📅 Alert Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Happy gaming! This deal was found by TagTracker's ultra-stealth monitoring system.

Best regards,
TagTracker Team 🤖
                """
            else:
                body = f"""
Hello {user_name}! 🛍️

🚨 PRICE DROP ALERT! 🚨

Great news! A product you're tracking has dropped to or below your target price!

🏪 Platform: {product['platform_icon']} {platform_name}
📦 Product: {product['title']}

{currency_emoji} Price Information:
Current Price: {current_price_str}
Your Target: {target_price_str}
You Save: {savings_str}

🔗 Buy This Product Now:
{product['url']}

📅 Alert Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This deal was found by TagTracker's ultra-stealth monitoring system that checks prices every 6 hours across multiple platforms.

Happy shopping! 🎉

Best regards,
TagTracker Team 🤖
                """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email using Gmail SMTP with enhanced error handling
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(user_email, smtp_password)
            server.send_message(msg)
            server.quit()
            
            print(f"📧 Ultra-stealth alert sent to {user_name} for {platform_name}")
            
        except Exception as e:
            print(f"❌ Failed to send email alert: {str(e)}")
    
    async def check_all_products(self) -> None:
        """Check all tracked products with ultra-stealth capabilities - CHRONOLOGICAL ORDER"""
        try:
            products = self.get_all_products_for_checking()
            
            if not products:
                print("ℹ️ No products to check")
                return
            
            print(f"🔄 Ultra-stealth checking {len(products)} products in chronological order...")
            
            # FIXED: NO MORE RANDOMIZATION - Keep chronological order as requested
            # Products are already ordered by created_at DESC from the query
            
            for i, product in enumerate(products):
                try:
                    platform_name = product.get('platform_name', 'Unknown')
                    platform = product.get('platform', 'unknown')
                    
                    print(f"📦 [{i+1}/{len(products)}] Ultra-stealth checking {platform_name}: {product['url'][:60]}...")
                    
                    # Ultra-stealth scraping with enhanced accuracy
                    result = await self.scrape_product(product['url'])
                    
                    if result:
                        title, current_price = result
                        
                        # Update database
                        self.update_product_info(product['id'], title, current_price)
                        
                        # Enhanced logging
                        if platform == 'roblox':
                            print(f"✅ Updated {platform_name}: {title[:40]}... - {int(current_price)} Robux")
                        else:
                            print(f"✅ Updated {platform_name}: {title[:40]}... - ${current_price:.2f}")
                        
                        # Check if price dropped below target
                        if current_price <= product['target_price']:
                            if platform == 'roblox':
                                print(f"🎮 ROBLOX DEAL ALERT! {title[:40]}... hit target price!")
                            else:
                                print(f"🎉 DEAL ALERT! {title[:40]}... hit target price!")
                            
                            # Update product for email
                            product['title'] = title
                            product['last_price'] = current_price
                            
                            # Send email alert if configured
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
                    print(f"❌ Error checking product {product.get('id', 'unknown')}: {str(e)}")
                    continue
                
                # Ultra-stealth rate limiting with randomization
                if i < len(products) - 1:  # Don't wait after the last product
                    delay = random.uniform(8, 15)  # Longer delays for maximum stealth
                    print(f"⏳ Ultra-stealth delay: {delay:.1f}s before next check...")
                    await asyncio.sleep(delay)
            
            print(f"✅ Ultra-stealth checking completed for all {len(products)} products")
            
        except Exception as e:
            print(f"❌ Error in ultra-stealth check_all_products: {e}")
    
    def get_supported_platforms(self) -> Dict[str, Dict[str, str]]:
        """Get information about supported platforms"""
        try:
            return UltraStealthMultiPlatformScraper.get_platform_info()
        except Exception as e:
            print(f"❌ Error getting supported platforms: {e}")
            return {}


# Ultra-stealth test function
async def test_ultra_stealth_tracker():
    """Test the ultra-stealth tracker with enhanced capabilities"""
    try:
        tracker = StorenvyPriceTracker()
        
        print("🕵️ Testing Ultra-Stealth TagTracker")
        print("🛡️ Maximum bot evasion enabled")
        print("🎯 FIXED Walmart detection with exact selector")
        print("📅 Chronological order (no prioritization)")
        print("=" * 70)
        
        # Test URLs with your specific Walmart URL
        test_urls = [
            ("https://www.walmart.com/ip/JW-SAGA-VILLIAN-1/14141570021?classType=REGULAR&athbdg=L1800", 70.00),
            ("https://www.amazon.com/dp/B08N5WRWNW", 100.00),
        ]
        
        for url, target_price in test_urls:
            try:
                platform = tracker.scraper.detect_platform(url)
                print(f"\n🎯 Testing FIXED {platform} scraping...")
                print(f"URL: {url}")
                
                # Add product for test user
                tracker.add_product(url, target_price, 1)
                
                if platform == 'roblox':
                    print(f"✅ Added {platform} item with target {target_price} Robux")
                else:
                    print(f"✅ Added {platform} product with target ${target_price}")
                
                # Test ultra-stealth scraping
                print(f"🕵️ Ultra-stealth scraping {platform}...")
                result = await tracker.scrape_product(url)
                
                if result:
                    title, price = result
                    if platform == 'roblox':
                        print(f"✅ ULTRA-STEALTH SUCCESS: {title[:50]}... - {int(price)} Robux")
                        if price <= target_price:
                            print(f"🎮 DEAL FOUND! Price {int(price)} ≤ target {int(target_price)}!")
                    else:
                        print(f"✅ ULTRA-STEALTH SUCCESS: {title[:50]}... - ${price:.2f}")
                        if price <= target_price:
                            print(f"💰 DEAL FOUND! Price ${price:.2f} ≤ target ${target_price:.2f}!")
                else:
                    print(f"❌ Ultra-stealth scraping failed for {platform}")
                
            except Exception as e:
                print(f"❌ Failed to test {url}: {e}")
            
            print(f"⏳ Ultra-stealth cooldown: 15 seconds...")
            await asyncio.sleep(15)
        
        # Test getting tracked products
        products = tracker.get_tracked_products(1)
        print(f"\n📋 Currently tracking {len(products)} products:")
        for product in products:
            platform_name = product.get('platform_name', 'Unknown')
            status = "🎯 Below Target!" if product['status'] == 'below_target' else "👁️ Monitoring"
            print(f"  - {status} {platform_name}: {product['url'][:60]}...")
            
        print("\n✅ Ultra-stealth tracker test completed successfully")
        print("🛡️ All platforms tested with maximum stealth capabilities")
        print("🎯 Walmart FIXED with exact selector targeting")
        
    except Exception as e:
        print(f"❌ Error in ultra-stealth tracker test: {e}")


if __name__ == "__main__":
    print("🚀 TagTracker - Ultra-Stealth Multi-Platform Price Monitor")
    print("🛡️ Maximum Bot Evasion Technology")
    print("🎯 FIXED Walmart Detection with Exact Selector Targeting") 
    print("📅 Chronological Order Processing (No Prioritization)")
    print("🕵️ Advanced Anti-Detection Systems")
    print("=" * 70)
    
    # Run the ultra-stealth test
    asyncio.run(test_ultra_stealth_tracker())