# backend/multi_platform_scraper.py - FIXED VERSION WITH ALL ERRORS RESOLVED
import asyncio
import re
import random
import json
from typing import Optional, Tuple, Dict
from urllib.parse import urlparse, parse_qs
from playwright.async_api import async_playwright
import time
from datetime import datetime, timedelta

class MultiPlatformScraper:
    """Enhanced e-commerce scraper with fixed Walmart/Etsy and new Roblox UGC/Flight trackers"""
    
    def __init__(self):
        # Enhanced platform-specific selectors with better extraction methods
        self.platform_configs = {
            'amazon': {
                'domain_patterns': ['amazon.com', 'amazon.co', 'amazon.ca', 'amazon.in', 'amazon.de', 'amazon.fr'],
                'title_selectors': [
                    'span#productTitle',
                    'h1#title span',
                    'h1.a-size-large span',
                    'h1[data-automation-id="product-title"]',
                    '#feature-bullets h1',
                    '.product-title'
                ],
                'price_selectors': [
                    'span.a-price.a-text-price.a-size-medium.apexPriceToPay .a-offscreen',
                    '.a-price .a-offscreen',
                    'span.a-price.a-text-price.apexPriceToPay .a-offscreen',
                    '.a-price-current .a-offscreen',
                    'span[class*="a-price-range"]',
                    '.price .a-offscreen',
                    '#priceblock_dealprice',
                    '#priceblock_ourprice'
                ],
                'price_fraction_selectors': [
                    'span.a-price-fraction',
                    '.a-price-fraction'
                ],
                'wait_time': 5000,
                'user_agents': [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ]
            },
            'ebay': {
                'domain_patterns': ['ebay.com', 'ebay.co.uk', 'ebay.ca', 'ebay.de', 'ebay.fr'],
                'title_selectors': [
                    'h1[data-testid="x-item-title-label"]',
                    'h1#x-item-title-label',
                    'h1.x-item-title-label',
                    'h1[id*="x-item-title"]',
                    'h1.it-ttl',
                    'span.ux-textspans--BOLD',
                    'h1'
                ],
                'price_selectors': [
                    'span.ux-textspans[role="text"]',
                    'span.ux-textspans',
                    'span.notranslate',
                    '.x-price-primary',
                    'span[itemprop="price"]',
                    '.u-flL.condText',
                    '#prcIsum'
                ],
                'wait_time': 4000,
                'user_agents': [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ]
            },
            'etsy': {
                'domain_patterns': ['etsy.com'],
                'title_selectors': [
                    'h1[data-test-id="listing-page-title"]',
                    'h1[data-testid="listing-page-title"]',
                    'h1.shop2-listing-page-title',
                    'h1[data-cy="listing-page-title"]',
                    'h1.listing-page-title',
                    'h1'
                ],
                'price_selectors': [
                    'p[data-testid="lp-price"] span.currency-value',
                    'p[data-test-id="lp-price"] span.currency-value',
                    'span[data-testid="currency-value"]',
                    'p.wt-text-title-larger span.currency-value',
                    'span.currency-value',
                    'p.wt-text-title-larger',
                    '.currency-symbol + .currency-value'
                ],
                'wait_time': 4000,
                'user_agents': [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ]
            },
            'walmart': {
                'domain_patterns': ['walmart.com'],
                'title_selectors': [
                    'h1[data-automation-id="product-title"]',
                    'h1[data-testid="product-title"]',
                    'h1.prod-ProductTitle',
                    'h1[id*="main-title"]',
                    'h1.f2',
                    'h1'
                ],
                'price_selectors': [
                    'span[data-automation-id="product-price"]',
                    'span[data-testid="product-price"]',
                    'span[itemprop="price"]',
                    'div[data-testid="price-wrap"] span',
                    'span.price-current',
                    'span.price-display',
                    '[data-testid="price-current"]',
                    'div.price span'
                ],
                'wait_time': 5000,
                'user_agents': [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ]
            },
            'storenvy': {
                'domain_patterns': ['storenvy.com'],
                'title_selectors': [
                    'h1.product-name',
                    'h1.product_name',
                    'h1[itemprop="name"]',
                    '.product-header h1',
                    'h1'
                ],
                'price_selectors': [
                    'div.price.vprice[itemprop="price"]',
                    'div.price.vprice',
                    'div[itemprop="price"]',
                    '.price.vprice',
                    'span.product-price',
                    '.product-price'
                ],
                'wait_time': 3000,
                'user_agents': [
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ]
            },
            'roblox': {
                'domain_patterns': ['roblox.com'],
                'title_selectors': [
                    'h1[data-testid="item-name"]',
                    'h1.item-name-container h1',
                    'h1.font-header-1',
                    '.item-name-container h1',
                    'h1'
                ],
                'price_selectors': [
                    'span[data-testid="price-label"]',
                    'span.text-robux',
                    'span.robux',
                    'span[class*="robux"]',
                    '.price-robux',
                    'span.icon-robux + span'
                ],
                'wait_time': 4000,
                'user_agents': [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ],
                'currency': 'robux'
            },
            'flights': {
                'domain_patterns': ['kayak.com', 'expedia.com', 'booking.com', 'priceline.com', 'momondo.com'],
                'title_selectors': [
                    '.flight-info h3',
                    '.itinerary-title',
                    '.trip-summary',
                    'h1.flight-header',
                    'h2.flight-details'
                ],
                'price_selectors': [
                    'span[data-testid="price"]',
                    '.price-text',
                    '.flight-price',
                    'span.price',
                    '.fare-price',
                    'div[class*="price"] span'
                ],
                'wait_time': 6000,
                'user_agents': [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ],
                'special_handling': True
            }
        }
    
    def detect_platform(self, url: str) -> Optional[str]:
        """Detect which platform the URL belongs to"""
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        for platform, config in self.platform_configs.items():
            for pattern in config['domain_patterns']:
                if pattern in domain:
                    return platform
        
        return None
    
    def get_random_user_agent(self, platform: str) -> str:
        """Get a random user agent for the specific platform"""
        config = self.platform_configs.get(platform, {})
        user_agents = config.get('user_agents', [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ])
        return random.choice(user_agents)
    
    async def stealth_browser_setup(self, browser, platform: str):
        """Enhanced stealth setup to avoid detection"""
        user_agent = self.get_random_user_agent(platform)
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='America/New_York',
            user_agent=user_agent,
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            }
        )
        
        page = await context.new_page()
        
        # Enhanced anti-detection script
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
            
            // Store the original descriptor
            const elementDescriptor = Object.getOwnPropertyDescriptor(HTMLElement.prototype, 'offsetHeight');
            
            // Redefine the property with a custom getter
            if (elementDescriptor) {
                Object.defineProperty(HTMLElement.prototype, 'offsetHeight', {
                    ...elementDescriptor,
                    get: function() {
                        if (this.id === 'modernizr') {
                            return 1;
                        }
                        return elementDescriptor.get.apply(this);
                    },
                });
            }
        """)
        
        return page
    
    async def human_like_behavior(self, page, platform: str):
        """Enhanced human-like behavior simulation"""
        try:
            # Random wait at start
            await asyncio.sleep(random.uniform(1, 3))
            
            # Simulate realistic mouse movements
            for _ in range(random.randint(2, 4)):
                x = random.randint(100, 1200)
                y = random.randint(100, 800)
                await page.mouse.move(x, y, steps=random.randint(5, 15))
                await asyncio.sleep(random.uniform(0.1, 0.3))
            
            # Random scrolling to mimic reading
            scroll_positions = [200, 400, 600, 300, 100]
            for position in scroll_positions[:random.randint(2, 4)]:
                await page.evaluate(f"window.scrollTo({{top: {position}, behavior: 'smooth'}})")
                await asyncio.sleep(random.uniform(0.5, 1.2))
            
            # Platform-specific behavior
            if platform == 'walmart':
                try:
                    # Try to interact with Walmart-specific elements
                    await page.hover('[data-testid="price-wrap"]', timeout=2000)
                except:
                    pass
            elif platform == 'etsy':
                try:
                    # Scroll to price section for Etsy
                    await page.evaluate("document.querySelector('[data-testid=\"lp-price\"]')?.scrollIntoView()")
                except:
                    pass
            elif platform == 'roblox':
                try:
                    # Wait for Roblox authentication check
                    await page.wait_for_timeout(2000)
                except:
                    pass
            
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
        except Exception as e:
            print(f"⚠️ Human behavior simulation failed: {e}")
    
    async def extract_walmart_price(self, page) -> Optional[float]:
        """Enhanced Walmart price extraction"""
        config = self.platform_configs['walmart']
        
        print("🔍 Extracting Walmart price with enhanced selectors...")
        
        # Wait for price elements to load
        await page.wait_for_timeout(3000)
        
        # Enhanced Walmart price extraction
        enhanced_selectors = [
            'span[data-automation-id="product-price"]',
            'span[data-testid="product-price"]',
            'div[data-testid="price-wrap"] span[itemprop="price"]',
            'span[itemprop="price"]',
            'div[data-testid="price-wrap"] span',
            'span.price-current',
            'span.price-display',
            '[data-testid="price-current"]',
            'div.price span'
        ]
        
        for i, selector in enumerate(enhanced_selectors):
            try:
                elements = await page.query_selector_all(selector)
                for element in elements:
                    price_text = await element.text_content()
                    if price_text and '$' in price_text:
                        print(f"💰 Walmart price from selector #{i+1}: '{price_text}'")
                        price = await self.extract_price_from_text(price_text)
                        if price and price > 0:
                            return price
            except Exception as e:
                print(f"⚠️ Walmart selector #{i+1} failed ({selector}): {str(e)[:50]}")
                continue
        
        # JavaScript fallback for Walmart
        print("🔧 Trying Walmart JavaScript fallback...")
        try:
            price_candidates = await page.evaluate('''
                () => {
                    const results = [];
                    
                    // Look for price elements with various patterns
                    const priceElements = document.querySelectorAll('*');
                    for (const element of priceElements) {
                        const text = element.textContent || '';
                        if (text.match(/\\$\\d+\\.\\d{2}/) && element.offsetParent !== null) {
                            // Check if it's likely a price (not a random number)
                            const hasPrice = text.includes('$') && text.match(/\\d+\\.\\d{2}/);
                            const isVisible = element.offsetWidth > 0 && element.offsetHeight > 0;
                            if (hasPrice && isVisible) {
                                results.push(text.trim());
                            }
                        }
                    }
                    
                    // Also check for data attributes
                    const dataElements = document.querySelectorAll('[data-automation-id*="price"], [data-testid*="price"]');
                    for (const element of dataElements) {
                        const text = element.textContent || '';
                        if (text.includes('$')) {
                            results.push(text.trim());
                        }
                    }
                    
                    return results.slice(0, 10);
                }
            ''')
            
            print(f"🔍 Walmart JavaScript found candidates: {price_candidates[:3]}")
            for price_text in price_candidates:
                price = await self.extract_price_from_text(price_text)
                if price and price > 0:
                    return price
        except Exception as e:
            print(f"⚠️ Walmart JavaScript fallback failed: {e}")
        
        print("❌ Walmart price extraction failed")
        return None
    
    async def extract_etsy_price(self, page) -> Optional[float]:
        """Enhanced Etsy price extraction"""
        config = self.platform_configs['etsy']
        
        print("🔍 Extracting Etsy price with enhanced selectors...")
        
        # Wait for Etsy page to fully load
        await page.wait_for_timeout(4000)
        
        # Enhanced Etsy price extraction
        enhanced_selectors = [
            'p[data-testid="lp-price"] span.currency-value',
            'p[data-test-id="lp-price"] span.currency-value',
            'span[data-testid="currency-value"]',
            'p.wt-text-title-larger span.currency-value',
            'span.currency-value',
            'p.wt-text-title-larger',
            '.currency-symbol + .currency-value',
            'span[class*="currency-value"]',
            'div[data-test-id="price"] span'
        ]
        
        for i, selector in enumerate(enhanced_selectors):
            try:
                elements = await page.query_selector_all(selector)
                for element in elements:
                    price_text = await element.text_content()
                    if price_text:
                        print(f"💰 Etsy price from selector #{i+1}: '{price_text}'")
                        price = await self.extract_price_from_text(price_text)
                        if price and price > 0:
                            return price
            except Exception as e:
                print(f"⚠️ Etsy selector #{i+1} failed ({selector}): {str(e)[:50]}")
                continue
        
        # JavaScript fallback for Etsy
        print("🔧 Trying Etsy JavaScript fallback...")
        try:
            price_candidates = await page.evaluate('''
                () => {
                    const results = [];
                    
                    // Look for currency values
                    const currencyElements = document.querySelectorAll('.currency-value, [class*="currency-value"]');
                    for (const element of currencyElements) {
                        const text = element.textContent || '';
                        if (text.match(/\\d+/) && element.offsetParent !== null) {
                            results.push(text.trim());
                        }
                    }
                    
                    // Look for price patterns
                    const allElements = document.querySelectorAll('*');
                    for (const element of allElements) {
                        const text = element.textContent || '';
                        if (text.match(/\\$\\d+\\.\\d{2}/) && element.offsetParent !== null) {
                            results.push(text.trim());
                        }
                    }
                    
                    return results.slice(0, 10);
                }
            ''')
            
            print(f"🔍 Etsy JavaScript found candidates: {price_candidates[:3]}")
            for price_text in price_candidates:
                price = await self.extract_price_from_text(price_text)
                if price and price > 0:
                    return price
        except Exception as e:
            print(f"⚠️ Etsy JavaScript fallback failed: {e}")
        
        print("❌ Etsy price extraction failed")
        return None
    
    async def extract_roblox_price(self, page) -> Optional[float]:
        """Extract Roblox UGC price (in Robux)"""
        config = self.platform_configs['roblox']
        
        print("🔍 Extracting Roblox UGC price...")
        
        # Wait for Roblox page to load
        await page.wait_for_timeout(4000)
        
        # Roblox-specific price extraction
        roblox_selectors = [
            'span[data-testid="price-label"]',
            'span.text-robux',
            'span.robux',
            'span[class*="robux"]',
            '.price-robux',
            'span.icon-robux + span',
            'div[class*="price"] span',
            'span[class*="Price"]'
        ]
        
        for i, selector in enumerate(roblox_selectors):
            try:
                elements = await page.query_selector_all(selector)
                for element in elements:
                    price_text = await element.text_content()
                    if price_text and ('robux' in price_text.lower() or price_text.strip().isdigit()):
                        print(f"💰 Roblox price from selector #{i+1}: '{price_text}'")
                        price = await self.extract_robux_from_text(price_text)
                        if price and price > 0:
                            return price
            except Exception as e:
                print(f"⚠️ Roblox selector #{i+1} failed ({selector}): {str(e)[:50]}")
                continue
        
        # JavaScript fallback for Roblox
        print("🔧 Trying Roblox JavaScript fallback...")
        try:
            price_candidates = await page.evaluate('''
                () => {
                    const results = [];
                    
                    // Look for Robux indicators
                    const robuxElements = document.querySelectorAll('*');
                    for (const element of robuxElements) {
                        const text = element.textContent || '';
                        if ((text.includes('Robux') || text.includes('R$') || text.match(/^\\d+$/)) && element.offsetParent !== null) {
                            results.push(text.trim());
                        }
                    }
                    
                    return results.slice(0, 10);
                }
            ''')
            
            print(f"🔍 Roblox JavaScript found candidates: {price_candidates[:3]}")
            for price_text in price_candidates:
                price = await self.extract_robux_from_text(price_text)
                if price and price > 0:
                    return price
        except Exception as e:
            print(f"⚠️ Roblox JavaScript fallback failed: {e}")
        
        print("❌ Roblox price extraction failed")
        return None
    
    async def extract_flight_price(self, page) -> Optional[float]:
        """Extract flight price from travel sites"""
        config = self.platform_configs['flights']
        
        print("🔍 Extracting flight price...")
        
        # Wait for flight data to load
        await page.wait_for_timeout(6000)
        
        # Flight-specific price extraction
        flight_selectors = [
            'span[data-testid="price"]',
            '.price-text',
            '.flight-price',
            'span.price',
            '.fare-price',
            'div[class*="price"] span',
            '.price-display',
            '[data-testid="flight-price"]',
            '.total-price'
        ]
        
        for i, selector in enumerate(flight_selectors):
            try:
                elements = await page.query_selector_all(selector)
                for element in elements:
                    price_text = await element.text_content()
                    if price_text and '$' in price_text:
                        print(f"💰 Flight price from selector #{i+1}: '{price_text}'")
                        price = await self.extract_price_from_text(price_text)
                        if price and price > 0:
                            return price
            except Exception as e:
                print(f"⚠️ Flight selector #{i+1} failed ({selector}): {str(e)[:50]}")
                continue
        
        # JavaScript fallback for flights
        print("🔧 Trying flight JavaScript fallback...")
        try:
            price_candidates = await page.evaluate('''
                () => {
                    const results = [];
                    
                    // Look for flight price patterns
                    const priceElements = document.querySelectorAll('*');
                    for (const element of priceElements) {
                        const text = element.textContent || '';
                        if (text.match(/\\$\\d{3,4}/) && element.offsetParent !== null) {
                            const hasFlightContext = text.includes('total') || text.includes('price') || 
                                                   element.className.includes('price') ||
                                                   element.className.includes('fare');
                            if (hasFlightContext) {
                                results.push(text.trim());
                            }
                        }
                    }
                    
                    return results.slice(0, 10);
                }
            ''')
            
            print(f"🔍 Flight JavaScript found candidates: {price_candidates[:3]}")
            for price_text in price_candidates:
                price = await self.extract_price_from_text(price_text)
                if price and price > 0:
                    return price
        except Exception as e:
            print(f"⚠️ Flight JavaScript fallback failed: {e}")
        
        print("❌ Flight price extraction failed")
        return None
    
    async def extract_robux_from_text(self, price_text: str) -> Optional[float]:
        """Extract Robux price from text"""
        if not price_text:
            return None
        
        print(f"🔍 Extracting Robux from text: '{price_text[:100]}'")
        
        # Clean the text
        cleaned_text = re.sub(r'[^\d,.\-\s]', ' ', price_text)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        # Robux patterns
        robux_patterns = [
            r'(\d{1,3}(?:,\d{3})*)',  # 1,000 format
            r'(\d+)',                 # Simple digits
        ]
        
        for pattern in robux_patterns:
            matches = re.findall(pattern, cleaned_text)
            if matches:
                for match in matches:
                    try:
                        price_str = match.replace(',', '').strip()
                        price = float(price_str)
                        
                        # Validate Robux price (between 1 and 999,999)
                        if 1 <= price <= 999999:
                            print(f"💰 Extracted Robux price: {price:.0f}")
                            return price
                    except (ValueError, IndexError):
                        continue
        
        print(f"❌ Could not extract Robux from: '{price_text[:100]}'")
        return None
    
    async def extract_price_from_text(self, price_text: str) -> Optional[float]:
        """Enhanced price extraction with better regex patterns"""
        if not price_text:
            return None
        
        print(f"🔍 Extracting price from text: '{price_text[:100]}'")
        
        # Clean the text - remove common currency symbols and extra whitespace
        cleaned_text = re.sub(r'[^\d.,\-\s$€£¥₹]', ' ', price_text)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        print(f"🧹 Cleaned text: '{cleaned_text}'")
        
        # Enhanced price patterns (order matters - most specific first)
        price_patterns = [
            r'US\s*\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)',  # US $135.00 format
            r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)',  # $1,234.56
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)\s*\$',  # 1,234.56$
            r'(\d{1,3}(?:,\d{3})*\.\d{2})',              # 1,234.56
            r'(\d{1,3}(?:,\d{3})*)',                     # 1,234 (whole numbers)
            r'(\d+\.\d{2})',                             # 123.45
            r'(\d+)',                                    # 123 (last resort)
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, cleaned_text)
            if matches:
                for match in matches:
                    try:
                        # Clean the matched price string
                        price_str = match.replace(',', '').replace('$', '').strip()
                        price = float(price_str)
                        
                        # Validate price is reasonable (between $0.01 and $999,999)
                        if 0.01 <= price <= 999999:
                            print(f"💰 Extracted price: ${price:.2f}")
                            return price
                    except (ValueError, IndexError):
                        continue
        
        print(f"❌ Could not extract price from: '{price_text[:100]}'")
        return None
    
    async def extract_with_fallbacks(self, page, selectors: list, extract_type: str = "text") -> Optional[str]:
        """Extract content using multiple selector fallbacks with enhanced methods"""
        for i, selector in enumerate(selectors):
            try:
                # Wait for selector with shorter timeout for each attempt
                element = await page.wait_for_selector(selector, timeout=2000)
                if element:
                    if extract_type == "text":
                        content = await element.text_content()
                    else:
                        content = await element.get_attribute(extract_type)
                    
                    if content and len(content.strip()) > 0:
                        print(f"✅ Found content with selector #{i+1}: {selector}")
                        return content.strip()
            except Exception as e:
                print(f"⚠️ Selector #{i+1} failed ({selector}): {str(e)[:100]}")
                continue
        
        # JavaScript fallback for more aggressive extraction
        print(f"🔧 Trying JavaScript fallback for content extraction...")
        try:
            if extract_type == "text":
                # Try to find any element containing price-like text
                result = await page.evaluate("""
                    () => {
                        const elements = document.querySelectorAll('*');
                        for (let element of elements) {
                            const text = element.textContent || '';
                            if (text.match(/\\$\\d+/) && element.offsetParent !== null) {
                                return text.trim();
                            }
                        }
                        return null;
                    }
                """)
                return result
        except Exception as e:
            print(f"JavaScript fallback failed: {e}")
        
        return None
    
    async def scrape_product(self, url: str) -> Optional[Tuple[str, float]]:
        """Enhanced product scraping with platform-specific extraction"""
        platform = self.detect_platform(url)
        
        if not platform:
            print(f"❌ Unsupported platform for URL: {url}")
            return None
        
        config = self.platform_configs[platform]
        
        async with async_playwright() as p:
            browser = None
            try:
                # Enhanced browser setup with stealth features
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--disable-web-security',
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-gpu',
                        '--disable-background-timer-throttling',
                        '--disable-backgrounding-occluded-windows',
                        '--disable-renderer-backgrounding',
                        '--disable-features=TranslateUI',
                        '--disable-ipc-flooding-protection'
                    ]
                )
                
                page = await self.stealth_browser_setup(browser, platform)
                
                print(f"🔍 Scraping {platform.title()} product: {url[:60]}...")
                
                # Navigate with retries
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                        break
                    except Exception as e:
                        if attempt == max_retries - 1:
                            raise e
                        print(f"Navigation attempt {attempt + 1} failed, retrying...")
                        await asyncio.sleep(2)
                
                # Wait for the page to load with platform-specific timing
                print(f"⏳ Waiting {config['wait_time']}ms for {platform} to load...")
                await page.wait_for_timeout(config['wait_time'])
                
                # Simulate human behavior
                await self.human_like_behavior(page, platform)
                
                # Extract title with enhanced methods
                print(f"📝 Extracting title for {platform}...")
                title = await self.extract_with_fallbacks(page, config['title_selectors'])
                
                if not title:
                    # Enhanced JavaScript fallback for title
                    print(f"🔧 Trying enhanced JavaScript fallback for title...")
                    title = await page.evaluate('''
                        () => {
                            // Try multiple methods to find title
                            const selectors = ['h1', '[data-testid*="title"]', '[class*="title"]', '[id*="title"]'];
                            for (const sel of selectors) {
                                const element = document.querySelector(sel);
                                if (element && element.textContent.trim()) {
                                    return element.textContent.trim();
                                }
                            }
                            // Fallback to page title
                            return document.title.split(' - ')[0] || document.title.split(' | ')[0];
                        }
                    ''')
                
                # Platform-specific price extraction
                print(f"💰 Extracting price for {platform}...")
                price = None
                
                if platform == 'amazon':
                    price = await self.extract_amazon_price(page)
                elif platform == 'ebay':
                    price = await self.extract_ebay_price(page)
                elif platform == 'walmart':
                    price = await self.extract_walmart_price(page)
                elif platform == 'etsy':
                    price = await self.extract_etsy_price(page)
                elif platform == 'roblox':
                    price = await self.extract_roblox_price(page)
                elif platform == 'flights':
                    price = await self.extract_flight_price(page)
                else:
                    # Standard price extraction for other platforms
                    for i, selector in enumerate(config['price_selectors']):
                        try:
                            elements = await page.query_selector_all(selector)
                            for element in elements:
                                price_text = await element.text_content()
                                if price_text:
                                    print(f"📄 Price text from selector #{i+1}: '{price_text[:50]}'")
                                    if platform == 'roblox':
                                        price = await self.extract_robux_from_text(price_text)
                                    else:
                                        price = await self.extract_price_from_text(price_text)
                                    if price and price > 0:
                                        break
                            if price and price > 0:
                                break
                        except Exception as e:
                            print(f"⚠️ Price selector #{i+1} failed: {str(e)[:50]}")
                            continue
                
                # Final validation
                if not title:
                    print(f"❌ Could not extract title for {platform}")
                    return None
                
                if not price:
                    print(f"❌ Could not extract price for {platform}")
                    return None
                
                # Clean up title
                title = title[:200]  # Limit title length
                
                # Format price display based on platform
                if platform == 'roblox':
                    print(f"✅ Successfully scraped {platform.title()}:")
                    print(f"   📝 Title: {title[:50]}...")
                    print(f"   💰 Price: {price:.0f} Robux")
                else:
                    print(f"✅ Successfully scraped {platform.title()}:")
                    print(f"   📝 Title: {title[:50]}...")
                    print(f"   💰 Price: ${price:.2f}")
                
                return title, price
                
            except Exception as e:
                print(f"❌ Error scraping {platform}: {str(e)}")
                return None
            
            finally:
                if browser:
                    await browser.close()
    
    async def extract_amazon_price(self, page) -> Optional[float]:
        """Amazon price extraction with whole + fraction handling"""
        config = self.platform_configs['amazon']
        
        # Method 1: Try to get complete price from .a-offscreen (most reliable)
        for selector in [
            'span.a-price.a-text-price.a-size-medium.apexPriceToPay .a-offscreen',
            '.a-price .a-offscreen',
            '.a-price-current .a-offscreen',
            'span.a-price.a-text-price.apexPriceToPay .a-offscreen'
        ]:
            try:
                element = await page.wait_for_selector(selector, timeout=2000)
                if element:
                    price_text = await element.text_content()
                    if price_text:
                        print(f"🎯 Amazon complete price from .a-offscreen: '{price_text}'")
                        price = await self.extract_price_from_text(price_text)
                        if price and price > 0:
                            return price
            except Exception as e:
                print(f"⚠️ Amazon .a-offscreen selector failed ({selector}): {str(e)[:50]}")
                continue
        
        # Method 2: Combine whole + fraction if .a-offscreen fails
        print("🔧 Trying Amazon whole + fraction method...")
        whole_price = None
        fraction_price = None
        
        # Get whole price
        for selector in config['price_selectors']:
            try:
                element = await page.wait_for_selector(selector, timeout=1500)
                if element:
                    whole_text = await element.text_content()
                    if whole_text:
                        print(f"📄 Amazon whole price text: '{whole_text}'")
                        whole_match = re.search(r'(\d+)', whole_text.replace(',', ''))
                        if whole_match:
                            whole_price = int(whole_match.group(1))
                            print(f"💰 Amazon whole price: {whole_price}")
                            break
            except Exception:
                continue
        
        # Get fraction price using specific selectors
        for selector in config.get('price_fraction_selectors', []):
            try:
                element = await page.wait_for_selector(selector, timeout=1500)
                if element:
                    fraction_text = await element.text_content()
                    if fraction_text:
                        print(f"🔢 Amazon fraction text: '{fraction_text}'")
                        fraction_match = re.search(r'(\d{1,2})', fraction_text)
                        if fraction_match:
                            fraction_price = int(fraction_match.group(1))
                            print(f"💫 Amazon fraction: {fraction_price}")
                            break
            except Exception:
                continue
        
        # Combine whole and fraction
        if whole_price is not None:
            if fraction_price is not None:
                combined_price = whole_price + (fraction_price / 100)
                print(f"✅ Amazon combined price: ${combined_price:.2f} (${whole_price}.{fraction_price:02d})")
                return combined_price
            else:
                print(f"✅ Amazon whole price only: ${whole_price:.2f}")
                return float(whole_price)
        
        print("❌ Amazon price extraction failed")
        return None
    
    async def extract_ebay_price(self, page) -> Optional[float]:
        """eBay price extraction with updated selectors"""
        config = self.platform_configs['ebay']
        
        print("🔍 Extracting eBay price with updated selectors...")
        
        enhanced_selectors = [
            'span.ux-textspans[role="text"]',
            'span.ux-textspans',
            'span.notranslate',
            '.x-price-primary',
            'span[itemprop="price"]',
            '.u-flL.condText',
            '#prcIsum'
        ]
        
        for i, selector in enumerate(enhanced_selectors):
            try:
                elements = await page.query_selector_all(selector)
                for element in elements:
                    price_text = await element.text_content()
                    if price_text and '$' in price_text:
                        print(f"💰 eBay price from selector #{i+1}: '{price_text}'")
                        price = await self.extract_price_from_text(price_text)
                        if price and price > 0:
                            return price
            except Exception as e:
                print(f"⚠️ eBay selector #{i+1} failed ({selector}): {str(e)[:50]}")
                continue
        
        # JavaScript fallback for eBay
        print("🔧 Trying eBay JavaScript fallback...")
        try:
            price_candidates = await page.evaluate('''
                () => {
                    const results = [];
                    
                    const uxElements = document.querySelectorAll('span.ux-textspans');
                    for (const element of uxElements) {
                        const text = element.textContent || '';
                        if (text.includes(') || text.includes('US') || text.match(/\\d+\\.\\d{2}/)) {
                            results.push(text.trim());
                        }
                    }
                    
                    const priceElements = document.querySelectorAll('*');
                    for (const element of priceElements) {
                        const text = element.textContent || '';
                        if (text.match(/US\\s*\\$\\d+\\.\\d{2}/) && element.offsetParent !== null) {
                            results.push(text.trim());
                        }
                    }
                    
                    return results.slice(0, 10);
                }
            ''')
            
            print(f"🔍 eBay JavaScript found candidates: {price_candidates[:3]}")
            for price_text in price_candidates:
                price = await self.extract_price_from_text(price_text)
                if price and price > 0:
                    return price
        except Exception as e:
            print(f"⚠️ eBay JavaScript fallback failed: {e}")
        
        print("❌ eBay price extraction failed")
        return None
    
    def get_supported_platforms(self) -> Dict[str, Dict[str, str]]:
        """Get information about supported platforms for UI"""
        return self.get_platform_info()
    
    @staticmethod
    def get_platform_info() -> Dict[str, Dict[str, str]]:
        """Get information about supported platforms for UI"""
        return {
            'amazon': {
                'name': 'Amazon',
                'example_url': 'https://www.amazon.com/dp/B08N5WRWNW',
                'icon': '🛒',
                'tips': 'Use the product URL from the address bar. Amazon URLs typically contain /dp/ or /gp/product/'
            },
            'ebay': {
                'name': 'eBay',
                'example_url': 'https://www.ebay.com/itm/123456789012',
                'icon': '🏷️',
                'tips': 'Use the item URL that contains /itm/ followed by the item number'
            },
            'etsy': {
                'name': 'Etsy',
                'example_url': 'https://www.etsy.com/listing/123456789/handmade-product-name',
                'icon': '🎨',
                'tips': 'Copy the listing URL that contains /listing/ followed by the listing ID'
            },
            'walmart': {
                'name': 'Walmart',
                'example_url': 'https://www.walmart.com/ip/Product-Name/123456789',
                'icon': '🏪',
                'tips': 'Walmart URLs contain /ip/ followed by the product name and ID'
            },
            'storenvy': {
                'name': 'Storenvy',
                'example_url': 'https://store-name.storenvy.com/products/123456-product-name',
                'icon': '🏬',
                'tips': 'Copy the full product URL from the product page'
            },
            'roblox': {
                'name': 'Roblox UGC',
                'example_url': 'https://www.roblox.com/catalog/123456789/Item-Name',
                'icon': '🎮',
                'tips': 'Use the catalog URL for UGC items. Prices shown in Robux.'
            },
            'flights': {
                'name': 'Flight Tickets',
                'example_url': 'https://www.kayak.com/flights/NYC-LAX/2024-03-15',
                'icon': '✈️',
                'tips': 'Use flight search result URLs from Kayak, Expedia, or similar sites'
            }
        }


# Test function
async def test_enhanced_scraper():
    """Test function to verify the enhanced scraper works"""
    scraper = MultiPlatformScraper()
    
    print("Testing Enhanced Multi-Platform Scraper")
    print("=" * 50)
    
    # Test URLs for different platforms
    test_urls = [
        "https://www.walmart.com/ip/Apple-iPhone-14-128GB-Blue/1234567890",
        "https://www.etsy.com/listing/123456789/handmade-ceramic-mug",
        "https://www.roblox.com/catalog/123456789/Cool-Hat",
    ]
    
    for url in test_urls:
        print(f"\n🎯 Testing URL: {url}")
        result = await scraper.scrape_product(url)
        if result:
            title, price = result
            platform = scraper.detect_platform(url)
            if platform == 'roblox':
                print(f"✅ Success: {title[:50]}... - {price:.0f} Robux")
            else:
                print(f"✅ Success: {title[:50]}... - ${price:.2f}")
        else:
            print(f"❌ Failed to scrape")

if __name__ == "__main__":
    asyncio.run(test_enhanced_scraper())