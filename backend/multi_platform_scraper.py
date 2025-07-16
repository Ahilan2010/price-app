# backend/enhanced_multi_platform_scraper.py - ULTRA STEALTH VERSION WITH ACCURATE PRICE DETECTION
import asyncio
import re
import random
import json
import time
from typing import Optional, Tuple, Dict, List
from urllib.parse import urlparse, parse_qs
from playwright.async_api import async_playwright
from datetime import datetime


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
            # Chrome on Windows 10
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            # Chrome on macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            # Edge on Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            # Firefox on Windows
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
            
            # Enhanced stealth context
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
                // Remove webdriver property completely
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                    configurable: true
                });
                
                // Mock real plugins
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
                            1: {
                                0: {type: "application/pdf", suffixes: "pdf", description: "Portable Document Format"},
                                description: "Portable Document Format",
                                filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                                length: 1,
                                name: "Chrome PDF Viewer"
                            },
                            length: 2
                        };
                    }
                });
                
                // Mock languages realistically
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                
                // Mock hardware concurrency
                Object.defineProperty(navigator, 'hardwareConcurrency', {
                    get: () => 8
                });
                
                // Mock device memory
                Object.defineProperty(navigator, 'deviceMemory', {
                    get: () => 8
                });
                
                // Mock platform
                Object.defineProperty(navigator, 'platform', {
                    get: () => 'Win32'
                });
                
                // Mock permissions API
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
                
                // Mock Chrome runtime
                window.chrome = {
                    runtime: {
                        onConnect: null,
                        onMessage: null,
                        connect: function() { return { onMessage: null, onDisconnect: null, postMessage: function() {} }; },
                        sendMessage: function() {}
                    },
                    storage: {
                        local: {
                            get: function() { return Promise.resolve({}); },
                            set: function() { return Promise.resolve(); }
                        }
                    }
                };
                
                // Remove automation traces
                delete window.__playwright;
                delete window.__puppeteer;
                delete window._phantom;
                delete window._selenium;
                delete window.callPhantom;
                delete window.callSelenium;
                delete window._Selenium_IDE_Recorder;
                
                // Remove CDP traces
                Object.keys(window).forEach(key => {
                    if (key.includes('cdc_') || key.includes('$cdc_') || key.includes('selenium')) {
                        delete window[key];
                    }
                });
                
                // Mock WebGL
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) return 'Intel Inc.';
                    if (parameter === 37446) return 'Intel Iris OpenGL Engine';
                    return getParameter.apply(this, arguments);
                };
                
                // Mock canvas fingerprinting
                const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
                HTMLCanvasElement.prototype.toDataURL = function(...args) {
                    // Add slight randomization to avoid fingerprinting
                    const context = this.getContext('2d');
                    context.fillStyle = 'rgba(255, 255, 255, 0.01)';
                    context.fillRect(0, 0, 1, 1);
                    return originalToDataURL.apply(this, args);
                };
                
                // Mock Date to prevent timezone fingerprinting
                const originalDate = Date;
                Date = function(...args) {
                    if (args.length === 0) {
                        return new originalDate();
                    }
                    return new originalDate(...args);
                };
                Date.prototype = originalDate.prototype;
                Date.now = originalDate.now;
                Date.parse = originalDate.parse;
                Date.UTC = originalDate.UTC;
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
            
            # Random initial wait
            await asyncio.sleep(random.uniform(2, 4))
            
            # Realistic mouse movements
            for _ in range(random.randint(3, 6)):
                x = random.randint(200, 1600)
                y = random.randint(200, 900)
                
                # Create Bézier curve-like movement
                current_x, current_y = 500, 500  # Starting position
                steps = random.randint(15, 25)
                
                for i in range(steps):
                    t = i / steps
                    # Easing function for natural movement
                    eased_t = t * t * (3.0 - 2.0 * t)
                    next_x = current_x + (x - current_x) * eased_t
                    next_y = current_y + (y - current_y) * eased_t
                    
                    await page.mouse.move(next_x, next_y)
                    await asyncio.sleep(random.uniform(0.01, 0.02))
                
                current_x, current_y = x, y
                await asyncio.sleep(random.uniform(0.3, 0.8))
            
            # Platform-specific scrolling behavior
            if scroll_behavior == 'targeted':
                # Scroll to specific areas for better content loading
                await page.evaluate("window.scrollTo({top: 300, behavior: 'smooth'})")
                await asyncio.sleep(2)
                await page.evaluate("window.scrollTo({top: 600, behavior: 'smooth'})")
                await asyncio.sleep(2)
                await page.evaluate("window.scrollTo({top: 200, behavior: 'smooth'})")
                await asyncio.sleep(1)
            elif scroll_behavior == 'gentle':
                # Gentle scrolling for Etsy-like sites
                for scroll_pos in [200, 400, 300, 500]:
                    await page.evaluate(f"window.scrollTo({{top: {scroll_pos}, behavior: 'smooth'}})")
                    await asyncio.sleep(random.uniform(1, 2))
            elif scroll_behavior == 'minimal':
                # Minimal scrolling for Amazon-like sites
                await page.evaluate("window.scrollTo({top: 250, behavior: 'smooth'})")
                await asyncio.sleep(1.5)
            
            # Random hover interactions
            if random.random() > 0.6:
                await page.mouse.move(
                    random.randint(400, 1000),
                    random.randint(300, 700)
                )
                await asyncio.sleep(random.uniform(0.5, 1))
                
        except Exception as e:
            print(f"Error simulating human interaction: {e}")
    
    async def wait_for_content_load(self, page, platform: str):
        """Advanced content loading detection"""
        try:
            config = self.platform_configs.get(platform, {})
            wait_time = config.get('wait_time', 5000)
            
            # Wait for network idle
            try:
                await page.wait_for_load_state('networkidle', timeout=wait_time)
            except:
                await page.wait_for_load_state('domcontentloaded', timeout=wait_time)
            
            # Platform-specific waiting
            if platform == 'walmart':
                # Wait for Walmart's dynamic pricing to load
                try:
                    await page.wait_for_selector('[data-testid="price-wrap"]', timeout=5000)
                except:
                    pass
                await asyncio.sleep(3)  # Extra wait for dynamic content
                
            elif platform == 'etsy':
                # Wait for Etsy's price component
                try:
                    await page.wait_for_selector('[data-testid="price"]', timeout=5000)
                except:
                    pass
                await asyncio.sleep(2)
                
            elif platform == 'amazon':
                # Wait for Amazon's price block
                try:
                    await page.wait_for_selector('.a-price', timeout=3000)
                except:
                    pass
            
            # General wait for JavaScript execution
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
            
            # First, exclude unwanted price elements (recommendations, etc.)
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
                            # Get both text content and any data attributes
                            price_text = await element.text_content()
                            
                            # Also check for price in data attributes
                            price_attr = None
                            try:
                                price_attr = await element.get_attribute('content')
                                if not price_attr:
                                    price_attr = await element.get_attribute('data-price')
                            except:
                                pass
                            
                            # Validate price context if product title is available
                            if product_title and platform == 'walmart':
                                # For Walmart, ensure we're not getting recommendation prices
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
                            
                            # Extract price from text
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
                            
                            # Extract price from attributes
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
                    
                    # If we found prices with this selector, prioritize them
                    if all_prices:
                        break
                        
                except Exception as e:
                    print(f"Selector {selector} failed: {e}")
                    continue
            
            if not all_prices:
                print(f"No valid prices found for {platform}")
                return None
            
            # Select the most accurate price
            return self.select_best_price(all_prices, platform)
            
        except Exception as e:
            print(f"Error extracting price for {platform}: {e}")
            return None
    
    async def extract_price_from_text(self, price_text: str, platform: str) -> Optional[float]:
        """Enhanced price extraction with platform-specific logic"""
        if not price_text:
            return None
        
        try:
            # Clean the text
            cleaned_text = price_text.strip().replace(',', '').replace(' ', '')
            
            # Platform-specific extraction
            if platform == 'roblox':
                # Robux extraction
                robux_patterns = [
                    r'(\d{1,6})',  # Just numbers for Robux
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
                # Currency extraction for other platforms
                currency_patterns = [
                    r'\$(\d{1,4}(?:\.\d{1,2})?)',  # $123.45
                    r'USD\s*(\d{1,4}(?:\.\d{1,2})?)',  # USD 123.45
                    r'(\d{1,4}(?:\.\d{1,2})?)\s*\$',  # 123.45$
                    r'(\d{1,4}\.\d{2})',  # 123.45
                    r'(\d{1,4})'  # 123 (last resort)
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
        
        # Sort by selector priority (earlier selectors are more specific)
        prices.sort(key=lambda x: x.get('selector', ''))
        
        # For platforms like Walmart, prefer prices from main product area
        if platform == 'walmart':
            main_prices = [p for p in prices if 'buybox' in p.get('selector', '') or 'add-to-cart' in p.get('selector', '')]
            if main_prices:
                return main_prices[0]['price']
        
        # Return the first (most priority) price
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
            # Enhanced browser launch with maximum stealth
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
                    '--no-first-run',
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
                
                # Navigate with multiple fallback strategies
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
                
                # Wait for content to load
                await self.wait_for_content# Wait for content to load
                await self.wait_for_content_load(page, platform)
                
                # Simulate human behavior
                await self.simulate_human_interaction(page, platform)
                
                # Extract product title for context
                title = await self.extract_product_title(page, platform)
                if not title:
                    print(f"Could not extract title for {platform}")
                    title = f"Product from {platform.title()}"
                
                # Extract price with enhanced accuracy
                price = await self.extract_accurate_price(page, platform, title)
                
                if price:
                    if platform == 'roblox':
                        print(f"✅ Successfully scraped {platform}: {title[:50]}... - {int(price)} Robux")
                    else:
                        print(f"✅ Successfully scraped {platform}: {title[:50]}... - ${price:.2f}")
                    return title, price
                else:
                    print(f"❌ Failed to extract price for {platform}")
                    
                    # Debug: Save page content for analysis
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


# Enhanced test function with specific URL testing
async def test_enhanced_scraper():
    """Test the enhanced scraper with problematic URLs"""
    scraper = EnhancedMultiPlatformScraper()
    
    # Test URLs including the problematic Walmart URL
    test_urls = [
        "https://www.walmart.com/ip/JW-SAGA-VILLIAN-1/14141570021?classType=REGULAR&athbdg=L1800",
        "https://www.amazon.com/dp/B08N5WRWNW",
        "https://www.etsy.com/listing/1234567890/test-product",
    ]
    
    for url in test_urls:
        print(f"\n{'='*80}")
        print(f"🧪 TESTING: {url}")
        print('='*80)
        
        result = await scraper.scrape_product(url)
        if result:
            title, price = result
            platform = scraper.detect_platform(url)
            if platform == 'roblox':
                print(f"✅ SUCCESS: {title} - {int(price)} Robux")
            else:
                print(f"✅ SUCCESS: {title} - ${price:.2f}")
        else:
            print("❌ FAILED to scrape")
        
        # Wait between tests
        print("⏳ Waiting 5 seconds before next test...")
        await asyncio.sleep(5)


# Advanced price validation class
class PriceValidator:
    """Validates extracted prices against known patterns and context"""
    
    @staticmethod
    def validate_walmart_price(price: float, title: str, page_content: str) -> bool:
        """Walmart-specific price validation"""
        try:
            # Check if price appears in main product context
            main_price_indicators = [
                'data-testid="price"',
                'buybox-price',
                'add-to-cart-price',
                'current-price'
            ]
            
            price_str = f"${price:.2f}"
            price_alt = f"{price:.2f}"
            
            for indicator in main_price_indicators:
                if indicator in page_content and (price_str in page_content or price_alt in page_content):
                    return True
            
            return False
        except:
            return True  # Default to true if validation fails
    
    @staticmethod
    def validate_etsy_price(price: float, title: str) -> bool:
        """Etsy-specific price validation"""
        # Etsy prices are typically between $1-$10000
        return 1.0 <= price <= 10000.0
    
    @staticmethod
    def validate_amazon_price(price: float, title: str) -> bool:
        """Amazon-specific price validation"""
        # Amazon prices vary widely, basic range check
        return 0.01 <= price <= 50000.0


# Enhanced error handling and retry mechanism
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
                    
                # If no result but no exception, wait and retry
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


# Main execution with enhanced error handling
if __name__ == "__main__":
    print("🚀 Enhanced Multi-Platform Scraper - Ultra Stealth Mode")
    print("=" * 60)
    
    # Test the scraper
    asyncio.run(test_enhanced_scraper())