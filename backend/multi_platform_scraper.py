# backend/multi_platform_scraper.py - ULTRA STEALTH VERSION WITH PRECISE WALMART EXTRACTION
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
    """Ultra-stealth multi-platform scraper with precise Walmart price extraction"""
    
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
                    # HIGHEST PRIORITY: The exact selector you specified
                    'span[itemprop="price"][data-seo-id="hero-price"][data-fs-element="price"]',
                    'span[itemprop="price"][data-seo-id="hero-price"]',
                    
                    # Secondary hero price variants
                    '[data-seo-id="hero-price"] span[itemprop="price"]',
                    '[data-testid="price-wrap"] [data-seo-id="hero-price"]',
                    
                    # Main buybox prices (high priority)
                    'span[data-automation-id="buybox-price"]',
                    'div[data-testid="price-wrap"] span[itemprop="price"]',
                    'div[data-testid="add-to-cart-price"] span[itemprop="price"]',
                    
                    # Fallback selectors
                    'span[data-automation-id="product-price"]',
                    'span[itemprop="price"]',
                    'div.price-current span',
                    '.price.display-inline-block span'
                ],
                'exclude_selectors': [
                    # Exclude recommendation/other product prices
                    'div[data-testid="recommendations"] *',
                    'div[data-testid="similar-items"] *',
                    'div[data-testid="you-might-also-like"] *',
                    '.recommendations *',
                    '.similar-items *',
                    '.sponsored-products *',
                    '[data-testid="similar-products"] *',
                    '[data-testid="related-products"] *',
                    '[data-testid="sponsored-products"] *',
                    '.js-product-recommendations *',
                    '[data-automation-id="related-products"] *'
                ],
                'wait_time': 12000,  # Increased wait time for Walmart
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
        
        # Advanced stealth user agents (latest versions)
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15'
        ]
        
        # Realistic device fingerprints
        self.fingerprints = [
            {
                'screen': {'width': 1920, 'height': 1080},
                'viewport': {'width': 1366, 'height': 768},
                'hardware_concurrency': 8,
                'device_memory': 8,
                'platform': 'Win32',
                'timezone': 'America/New_York'
            },
            {
                'screen': {'width': 2560, 'height': 1440},
                'viewport': {'width': 1920, 'height': 1080},
                'hardware_concurrency': 12,
                'device_memory': 16,
                'platform': 'MacIntel',
                'timezone': 'America/Los_Angeles'
            },
            {
                'screen': {'width': 1366, 'height': 768},
                'viewport': {'width': 1280, 'height': 720},
                'hardware_concurrency': 4,
                'device_memory': 4,
                'platform': 'Win32',
                'timezone': 'America/Chicago'
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
            
            # Create context with realistic settings
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
                geolocation={'latitude': 40.7128 + random.uniform(-0.1, 0.1), 'longitude': -74.0060 + random.uniform(-0.1, 0.1)},
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
                    'DNT': '1',
                    'Sec-Ch-Ua': '"Chromium";v="124", "Not(A:Brand";v="24", "Google Chrome";v="124"',
                    'Sec-Ch-Ua-Mobile': '?0',
                    'Sec-Ch-Ua-Platform': f'"{fingerprint["platform"]}"'
                }
            )
            
            page = await context.new_page()
            
            # Advanced stealth injection
            await page.add_init_script(f"""
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
                            1: {{
                                0: {{type: "application/pdf", suffixes: "pdf", description: "Portable Document Format"}},
                                description: "Portable Document Format", 
                                filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                                length: 1,
                                name: "Chrome PDF Viewer"
                            }},
                            length: 2
                        }};
                    }}
                }});
                
                // Hardware spoofing
                Object.defineProperty(navigator, 'hardwareConcurrency', {{
                    get: () => {fingerprint['hardware_concurrency']}
                }});
                
                Object.defineProperty(navigator, 'deviceMemory', {{
                    get: () => {fingerprint['device_memory']}
                }});
                
                Object.defineProperty(navigator, 'platform', {{
                    get: () => '{fingerprint['platform']}'
                }});
                
                Object.defineProperty(navigator, 'languages', {{
                    get: () => ['en-US', 'en']
                }});
                
                // Enhanced permissions API
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => {{
                    return Promise.resolve({{ state: 'granted' }});
                }};
                
                // Chrome runtime mock
                window.chrome = {{
                    runtime: {{
                        onConnect: null,
                        onMessage: null,
                        connect: function() {{ return {{ onMessage: null, onDisconnect: null, postMessage: function() {{}} }}; }},
                        sendMessage: function() {{}}
                    }},
                    loadTimes: function() {{
                        return {{
                            commitLoadTime: Date.now() / 1000 - Math.random() * 100,
                            connectionInfo: 'http/1.1',
                            finishDocumentLoadTime: Date.now() / 1000 - Math.random() * 10,
                            finishLoadTime: Date.now() / 1000 - Math.random() * 10,
                            firstPaintTime: Date.now() / 1000 - Math.random() * 10,
                            navigationType: 'Other',
                            requestTime: Date.now() / 1000 - Math.random() * 200,
                            startLoadTime: Date.now() / 1000 - Math.random() * 200
                        }};
                    }}
                }};
                
                // Remove all automation traces
                delete window.__playwright;
                delete window.__puppeteer;
                delete window._phantom;
                delete window.callPhantom;
                delete window._selenium;
                delete window.__webdriver_script_func;
                delete window.__webdriver_evaluate;
                delete window.__selenium_evaluate;
                delete window.__fxdriver_evaluate;
                delete window.__driver_unwrapped;
                delete window.__webdriver_unwrapped;
                delete window.__driver_evaluate;
                delete window.__selenium_unwrapped;
                delete window.__fxdriver_unwrapped;
                
                // Remove CDP traces
                Object.keys(window).forEach(key => {{
                    if (key.includes('cdc_') || key.includes('$cdc_') || key.includes('selenium') || 
                        key.includes('webdriver') || key.includes('driver') || key.includes('__nightmare')) {{
                        try {{ delete window[key]; }} catch(e) {{}}
                    }}
                }});
                
                // WebGL spoofing
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {{
                    if (parameter === 37445) return 'Intel Inc.';
                    if (parameter === 37446) return 'Intel Iris OpenGL Engine';
                    return getParameter.apply(this, arguments);
                }};
                
                // Canvas fingerprint protection
                const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
                HTMLCanvasElement.prototype.toDataURL = function(...args) {{
                    const context = this.getContext('2d');
                    if (context) {{
                        const imageData = context.getImageData(0, 0, this.width, this.height);
                        for (let i = 0; i < imageData.data.length; i += 4) {{
                            if (Math.random() < 0.001) {{
                                imageData.data[i] = imageData.data[i] ^ 1;
                            }}
                        }}
                        context.putImageData(imageData, 0, 0);
                    }}
                    return originalToDataURL.apply(this, args);
                }};
                
                // Enhanced Date spoofing
                const originalDate = Date;
                const timeOffset = Math.floor(Math.random() * 1000) + 500;
                Date = function(...args) {{
                    if (args.length === 0) {{
                        const d = new originalDate();
                        d.setTime(d.getTime() + timeOffset);
                        return d;
                    }}
                    return new originalDate(...args);
                }};
                Date.prototype = originalDate.prototype;
                Date.now = function() {{ return originalDate.now() + timeOffset; }};
                
                // Screen properties
                Object.defineProperty(screen, 'width', {{ get: () => {fingerprint['screen']['width']} }});
                Object.defineProperty(screen, 'height', {{ get: () => {fingerprint['screen']['height']} }});
                Object.defineProperty(screen, 'availWidth', {{ get: () => {fingerprint['screen']['width']} }});
                Object.defineProperty(screen, 'availHeight', {{ get: () => {fingerprint['screen']['height'] - 40} }});
                
                // Connection info
                Object.defineProperty(navigator, 'connection', {{
                    get: () => ({{
                        effectiveType: '4g',
                        rtt: 50 + Math.random() * 50,
                        downlink: 10 + Math.random() * 5,
                        saveData: false
                    }})
                }});
                
                // Console protection
                const noop = () => {{}};
                ['debug', 'clear', 'error', 'info', 'log', 'warn', 'dir', 'dirxml', 'table', 'trace', 'group', 'groupCollapsed', 'groupEnd', 'time', 'timeEnd', 'profile', 'profileEnd', 'timeStamp'].forEach(method => {{
                    if (console[method]) console[method] = noop;
                }});
            """)
            
            return page
        except Exception as e:
            print(f"Error setting up stealth browser: {e}")
            raise
    
    async def simulate_human_behavior(self, page, platform: str):
        """Simulate realistic human browsing behavior"""
        try:
            config = self.platform_configs.get(platform, {})
            scroll_behavior = config.get('scroll_behavior', 'minimal')
            
            # Initial random delay
            await asyncio.sleep(random.uniform(2, 4))
            
            # Realistic mouse movements
            for _ in range(random.randint(3, 6)):
                x = random.randint(100, 1000)
                y = random.randint(100, 600)
                await page.mouse.move(x, y)
                await asyncio.sleep(random.uniform(0.1, 0.3))
            
            # Platform-specific scrolling
            if scroll_behavior == 'ultra_gentle':
                # Very gentle scrolling for Etsy
                for pos in [150, 300, 200, 400, 250]:
                    await page.evaluate(f"window.scrollTo({{top: {pos}, behavior: 'smooth'}})")
                    await asyncio.sleep(random.uniform(2, 4))
                    
            elif scroll_behavior == 'targeted':
                # Targeted scrolling for Walmart
                await page.evaluate("window.scrollTo({top: 200, behavior: 'smooth'})")
                await asyncio.sleep(random.uniform(1.5, 2.5))
                await page.evaluate("window.scrollTo({top: 400, behavior: 'smooth'})")
                await asyncio.sleep(random.uniform(2, 3))
                await page.evaluate("window.scrollTo({top: 100, behavior: 'smooth'})")
                await asyncio.sleep(random.uniform(1, 2))
                
            else:
                # Minimal scrolling
                await page.evaluate("window.scrollTo({top: 150, behavior: 'smooth'})")
                await asyncio.sleep(random.uniform(1, 2))
            
            # Random pause
            await asyncio.sleep(random.uniform(1, 2))
                
        except Exception as e:
            print(f"Error simulating human behavior: {e}")
    
    async def wait_for_content_load(self, page, platform: str):
        """Enhanced content loading detection"""
        try:
            config = self.platform_configs.get(platform, {})
            wait_time = config.get('wait_time', 5000)
            
            # Multi-stage loading
            try:
                await page.wait_for_load_state('domcontentloaded', timeout=wait_time // 2)
                await asyncio.sleep(1)
                await page.wait_for_load_state('networkidle', timeout=wait_time // 2)
            except:
                await page.wait_for_load_state('load', timeout=wait_time)
            
            # Platform-specific waits
            if platform == 'walmart':
                # Wait for key Walmart elements
                selectors_to_wait = [
                    '[data-seo-id="hero-price"]',
                    '[data-testid="price-wrap"]',
                    '[itemprop="price"]'
                ]
                
                for selector in selectors_to_wait:
                    try:
                        await page.wait_for_selector(selector, timeout=3000)
                        print(f"✅ Walmart: Found element {selector}")
                        break
                    except:
                        continue
                
                # Extra wait for dynamic content
                await asyncio.sleep(random.uniform(3, 5))
                
            elif platform == 'etsy':
                try:
                    await page.wait_for_selector('[data-testid="price"]', timeout=8000)
                except:
                    pass
                await asyncio.sleep(random.uniform(2, 4))
                
            # General wait
            await page.wait_for_timeout(random.randint(1000, 3000))
            
            return True
        except Exception as e:
            print(f"Error waiting for content: {e}")
            return True
    
    async def extract_walmart_price_precise(self, page) -> Optional[float]:
        """Precise Walmart price extraction targeting your specific element"""
        try:
            print("🎯 Precise Walmart price extraction starting...")
            
            # Your exact priority selectors
            exact_selectors = [
                'span[itemprop="price"][data-seo-id="hero-price"][data-fs-element="price"]',
                'span[itemprop="price"][data-seo-id="hero-price"]',
                '[data-seo-id="hero-price"][itemprop="price"]',
                '[data-seo-id="hero-price"] span[itemprop="price"]'
            ]
            
            # Try exact selectors first
            for i, selector in enumerate(exact_selectors):
                try:
                    elements = await page.query_selector_all(selector)
                    print(f"Exact selector {i+1}: '{selector}' found {len(elements)} elements")
                    
                    for element in elements:
                        # Get all attributes for debugging
                        attributes = await page.evaluate('''
                            (element) => {
                                const attrs = {};
                                for (let attr of element.attributes) {
                                    attrs[attr.name] = attr.value;
                                }
                                return attrs;
                            }
                        ''', element)
                        
                        price_text = await element.text_content()
                        print(f"Element attributes: {attributes}")
                        print(f"Element text: '{price_text}'")
                        
                        if price_text:
                            price = await self.extract_price_from_text(price_text, 'walmart')
                            if price and 0.01 <= price <= 99999:
                                print(f"✅ WALMART EXACT: Found price ${price:.2f} with selector: {selector}")
                                return price
                                
                except Exception as e:
                    print(f"Exact selector '{selector}' failed: {e}")
                    continue
            
            # Fallback: try broader hero-price selectors
            print("🔄 Exact selectors failed, trying broader hero-price selectors...")
            fallback_selectors = [
                '[data-seo-id="hero-price"]',
                '[data-testid="price-wrap"] [data-seo-id="hero-price"]',
                'div[data-testid="price-wrap"] span[itemprop="price"]'
            ]
            
            for i, selector in enumerate(fallback_selectors):
                try:
                    elements = await page.query_selector_all(selector)
                    print(f"Fallback selector {i+1}: '{selector}' found {len(elements)} elements")
                    
                    for element in elements:
                        # Check if this is in the main product area
                        is_main_product = await page.evaluate('''
                            (element) => {
                                // Check if element is in main product section
                                const mainProduct = element.closest('[data-automation-id="product-title"]') ||
                                                   element.closest('main') ||
                                                   element.closest('[data-testid="product-page"]');
                                
                                // Check if it's NOT in recommendations
                                const isRecommendation = element.closest('[data-testid="recommendations"]') ||
                                                        element.closest('[data-testid="similar-items"]') ||
                                                        element.closest('.recommendations') ||
                                                        element.closest('[data-testid="sponsored-products"]');
                                
                                return mainProduct && !isRecommendation;
                            }
                        ''', element)
                        
                        if not is_main_product:
                            print(f"Skipping element not in main product area")
                            continue
                        
                        price_text = await element.text_content()
                        if price_text:
                            price = await self.extract_price_from_text(price_text, 'walmart')
                            if price and 0.01 <= price <= 99999:
                                print(f"✅ WALMART FALLBACK: Found price ${price:.2f} with selector: {selector}")
                                return price
                                
                except Exception as e:
                    print(f"Fallback selector '{selector}' failed: {e}")
                    continue
            
            print("❌ All Walmart price selectors failed")
            return None
            
        except Exception as e:
            print(f"Error in precise Walmart extraction: {e}")
            return None
    
    async def extract_price_from_text(self, price_text: str, platform: str) -> Optional[float]:
        """Enhanced price extraction with better pattern matching"""
        if not price_text:
            return None
        
        try:
            # Clean the text
            cleaned_text = price_text.strip().replace(',', '').replace(' ', '')
            print(f"Extracting price from: '{price_text}' -> cleaned: '{cleaned_text}'")
            
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
                # Enhanced currency extraction
                currency_patterns = [
                    r'\$(\d{1,5}(?:\.\d{1,2})?)',  # $49.84, $123.45
                    r'USD\s*(\d{1,5}(?:\.\d{1,2})?)',  # USD 49.84
                    r'(\d{1,5}\.\d{2})',  # 49.84
                    r'(\d{1,5})'  # 49 (last resort)
                ]
                
                for pattern in currency_patterns:
                    matches = re.findall(pattern, cleaned_text)
                    if matches:
                        for match in matches:
                            try:
                                price = float(match)
                                print(f"Pattern '{pattern}' extracted: {price}")
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
    
    async def extract_accurate_price(self, page, platform: str, product_title: str = None) -> Optional[float]:
        """Ultra-accurate price extraction with platform-specific logic"""
        try:
            print(f"🔍 Extracting price for {platform}...")
            
            # Use precise Walmart extraction
            if platform == 'walmart':
                return await self.extract_walmart_price_precise(page)
            
            config = self.platform_configs.get(platform, {})
            price_selectors = config.get('price_selectors', [])
            exclude_selectors = config.get('exclude_selectors', [])
            
            print(f"Using {len(price_selectors)} selectors for {platform}")
            
            # Remove unwanted elements first
            if exclude_selectors:
                for exclude_selector in exclude_selectors:
                    try:
                        excluded_elements = await page.query_selector_all(exclude_selector)
                        for element in excluded_elements:
                            await page.evaluate('(element) => element.remove()', element)
                        if excluded_elements:
                            print(f"Removed {len(excluded_elements)} unwanted elements with selector: {exclude_selector}")
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
                            
                            # Check for price in data attributes
                            price_attr = None
                            try:
                                price_attr = await element.get_attribute('content')
                                if not price_attr:
                                    price_attr = await element.get_attribute('data-price')
                                if not price_attr:
                                    price_attr = await element.get_attribute('value')
                            except:
                                pass
                            
                            # Extract from text
                            if price_text:
                                price = await self.extract_price_from_text(price_text, platform)
                                if price and self.validate_price_range(price, platform):
                                    all_prices.append({
                                        'price': price,
                                        'text': price_text.strip(),
                                        'selector': selector,
                                        'source': 'text'
                                    })
                                    print(f"Valid price: {self.format_price(price, platform)} from text: '{price_text.strip()}'")
                            
                            # Extract from attributes
                            if price_attr:
                                price = await self.extract_price_from_text(price_attr, platform)
                                if price and self.validate_price_range(price, platform):
                                    all_prices.append({
                                        'price': price,
                                        'text': price_attr,
                                        'selector': selector,
                                        'source': 'attribute'
                                    })
                                    print(f"Valid price: {self.format_price(price, platform)} from attribute: '{price_attr}'")
                                    
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
            
            # Select the best price
            return self.select_best_price(all_prices, platform)
            
        except Exception as e:
            print(f"Error extracting price for {platform}: {e}")
            return None
    
    def format_price(self, price: float, platform: str) -> str:
        """Format price display based on platform"""
        if platform == 'roblox':
            return f"{int(price)} Robux"
        else:
            return f"${price:.2f}"
    
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
        
        # For Walmart, prefer hero-price elements
        if platform == 'walmart':
            hero_prices = [p for p in prices if 'hero-price' in p.get('selector', '')]
            if hero_prices:
                return hero_prices[0]['price']
            
            buybox_prices = [p for p in prices if any(keyword in p.get('selector', '') for keyword in ['buybox', 'add-to-cart'])]
            if buybox_prices:
                return buybox_prices[0]['price']
        
        # Return the first (highest priority) price
        return prices[0]['price']
    
    async def scrape_product(self, url: str) -> Optional[Tuple[str, float]]:
        """Main scraping method with ultra-stealth and precise extraction"""
        platform = self.detect_platform(url)
        if not platform:
            print(f"Unsupported platform for URL: {url}")
            return None
        
        print(f"🕵️ Scraping {platform} with ULTRA-STEALTH mode: {url}")
        
        async with async_playwright() as p:
            # Enhanced browser launch with maximum stealth
            self.browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=VizDisplayCompositor',
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
                    '--disable-speech-api',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-features=TranslateUI',
                    '--disable-component-extensions-with-background-pages',
                    '--disable-http2',
                    '--disable-plugins',
                    '--disable-plugins-discovery',
                    '--disable-preconnect',
                    '--disable-hang-monitor'
                ]
            )
            
            try:
                page = await self.setup_ultra_stealth_browser(platform)
                
                print(f"🌐 Navigating to: {url}")
                
                # Enhanced navigation with retry logic
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
                            print(f"✅ Navigation successful (attempt {attempt + 1})")
                            break
                            
                    except Exception as e:
                        print(f"❌ Navigation attempt {attempt + 1} failed: {e}")
                        if attempt < 2:
                            await asyncio.sleep(random.uniform(3, 6))
                            continue
                        else:
                            raise
                
                if not navigation_success:
                    print("❌ All navigation attempts failed")
                    return None
                
                # Enhanced content loading and human simulation
                await self.wait_for_content_load(page, platform)
                await self.simulate_human_behavior(page, platform)
                
                # Extract product title
                title = await self.extract_product_title(page, platform)
                if not title:
                    print(f"⚠️ Could not extract title for {platform}")
                    title = f"Product from {platform.title()}"
                
                # Extract price with enhanced precision
                price = await self.extract_accurate_price(page, platform, title)
                
                if price:
                    formatted_price = self.format_price(price, platform)
                    print(f"✅ SUCCESS: {platform.upper()} - {title[:50]}... - {formatted_price}")
                    return title, price
                else:
                    print(f"❌ FAILED: Could not extract price for {platform}")
                    
                    # Debug: Save page content for analysis
                    try:
                        content = await page.content()
                        debug_file = f'debug_{platform}_{int(time.time())}.html'
                        with open(debug_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"💾 Debug: Saved HTML to {debug_file}")
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


# Enhanced retry mechanism
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
                    wait_time = self.backoff_factor ** attempt + random.uniform(1, 3)
                    print(f"🔄 Attempt {attempt + 1} failed, retrying in {wait_time:.1f}s...")
                    await asyncio.sleep(wait_time)
                    
            except Exception as e:
                last_exception = e
                print(f"❌ Attempt {attempt + 1} failed with error: {e}")
                
                if attempt < self.max_retries - 1:
                    wait_time = self.backoff_factor ** attempt + random.uniform(2, 5)
                    print(f"🔄 Retrying in {wait_time:.1f}s...")
                    await asyncio.sleep(wait_time)
        
        print(f"❌ All {self.max_retries} attempts failed")
        if last_exception:
            raise last_exception
        return None


# Test function for the specific Walmart URL
async def test_walmart_precise():
    """Test the precise Walmart extraction with your specific URL"""
    scraper = EnhancedMultiPlatformScraper()
    retry_manager = ScrapingRetryManager(max_retries=2)
    
    walmart_url = "https://www.walmart.com/ip/JW-SAGA-VILLIAN-1/14141570021?classType=REGULAR&athbdg=L1800"
    
    print(f"\n{'='*80}")
    print(f"🧪 TESTING PRECISE WALMART EXTRACTION")
    print(f"🎯 Target: $49.84 from hero-price element")
    print(f"🌐 URL: {walmart_url}")
    print('='*80)
    
    try:
        result = await retry_manager.execute_with_retry(scraper.scrape_product, walmart_url)
        if result:
            title, price = result
            print(f"✅ SUCCESS: {title}")
            print(f"💰 Price: ${price:.2f}")
            
            if abs(price - 49.84) < 0.01:
                print("🎯 PERFECT: Extracted the correct $49.84 price!")
            else:
                print(f"⚠️ NOTICE: Expected $49.84, got ${price:.2f}")
        else:
            print("❌ FAILED to scrape")
    except Exception as e:
        print(f"❌ ERROR: {e}")


# Enhanced test function for multiple platforms
async def test_enhanced_scraper():
    """Test the enhanced scraper with multiple URLs"""
    scraper = EnhancedMultiPlatformScraper()
    retry_manager = ScrapingRetryManager()
    
    test_urls = [
        "https://www.walmart.com/ip/JW-SAGA-VILLIAN-1/14141570021?classType=REGULAR&athbdg=L1800",
        "https://www.amazon.com/dp/B08N5WRWNW",
        "https://www.etsy.com/listing/1234567890/test-product",
        "https://www.ebay.com/itm/123456789"
    ]
    
    for url in test_urls:
        print(f"\n{'='*80}")
        print(f"🧪 TESTING: {url}")
        print('='*80)
        
        try:
            result = await retry_manager.execute_with_retry(scraper.scrape_product, url)
            if result:
                title, price = result
                platform = scraper.detect_platform(url)
                formatted_price = scraper.format_price(price, platform)
                print(f"✅ SUCCESS: {title[:50]}... - {formatted_price}")
            else:
                print("❌ FAILED to scrape")
        except Exception as e:
            print(f"❌ ERROR: {e}")
        
        # Wait between tests
        print("⏳ Waiting 8 seconds before next test...")
        await asyncio.sleep(8)


# Main execution
if __name__ == "__main__":
    print("🚀 Enhanced Multi-Platform Scraper - ULTRA STEALTH MODE")
    print("🎯 Precise Walmart Price Extraction")
    print("🛡️ Maximum Bot Detection Evasion")
    print("=" * 60)
    
    # Test the specific Walmart URL first
    print("\n🎯 Testing specific Walmart URL...")
    asyncio.run(test_walmart_precise())
    
    # Uncomment to test multiple platforms
    # print("\n🧪 Testing multiple platforms...")
    # asyncio.run(test_enhanced_scraper())