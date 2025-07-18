# backend/multi_platform_scraper.py - ULTRA STEALTH VERSION WITH ENHANCED WALMART DETECTION
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
    """Ultra-stealth multi-platform scraper with enhanced Walmart detection and maximum bot evasion"""
    
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
                    # PRIORITY: Your specific Walmart price selector
                    'span.inline-flex.flex-column span[itemprop="price"][data-seo-id="hero-price"]',
                    'span[itemprop="price"][data-seo-id="hero-price"][data-fs-element="price"]',
                    'span[itemprop="price"][data-seo-id="hero-price"]',
                    
                    # High-priority main product price selectors
                    'div[data-testid="price-wrap"] span[itemprop="price"]',
                    'span[data-automation-id="buybox-price"]',
                    'div[data-testid="add-to-cart-price"] span[itemprop="price"]',
                    'span[data-automation-id="product-price"]',
                    
                    # Additional backup selectors
                    'span[itemprop="price"]',
                    'div.price-current span',
                    '.price.display-inline-block span',
                    'div[data-testid="price"] span',
                    '[data-testid="price-section"] span[itemprop="price"]'
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
                    '[data-testid="related-products"] *'
                ],
                'wait_time': 10000,  # Increased wait time for Walmart
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
                'wait_time': 12000,  # Increased wait time for Etsy stealth
                'scroll_behavior': 'ultra_gentle'  # New ultra-gentle mode for Etsy
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
        
        # Ultra-realistic user agents with latest versions
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15'
        ]
        
        # Enhanced fingerprint data for ultra-stealth
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
            },
            {
                'screen': {'width': 1366, 'height': 768},
                'viewport': {'width': 1366, 'height': 768},
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
        """Ultra-stealth browser setup with maximum anti-detection for Etsy and enhanced Walmart support"""
        try:
            user_agent = random.choice(self.user_agents)
            fingerprint = random.choice(self.fingerprints)
            
            # Enhanced context setup with randomized fingerprinting
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
                    'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
                    'Sec-Ch-Ua-Mobile': '?0',
                    'Sec-Ch-Ua-Platform': f'"{fingerprint["platform"]}"'
                }
            )
            
            page = await context.new_page()
            
            # Ultra-advanced stealth scripts with enhanced Etsy bypass
            await page.add_init_script(f"""
                // Remove ALL automation traces
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
                            2: {{
                                0: {{type: "application/x-nacl", suffixes: "nexe", description: "Native Client Executable"}},
                                description: "Native Client",
                                filename: "internal-nacl-plugin",
                                length: 1,
                                name: "Native Client"
                            }},
                            length: 3
                        }};
                    }}
                }});
                
                // Mock languages with regional variations
                Object.defineProperty(navigator, 'languages', {{
                    get: () => ['en-US', 'en', 'es']
                }});
                
                // Mock hardware with realistic values
                Object.defineProperty(navigator, 'hardwareConcurrency', {{
                    get: () => {fingerprint['hardware_concurrency']}
                }});
                
                Object.defineProperty(navigator, 'deviceMemory', {{
                    get: () => {fingerprint['device_memory']}
                }});
                
                Object.defineProperty(navigator, 'platform', {{
                    get: () => '{fingerprint['platform']}'
                }});
                
                // Enhanced permissions API mock
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => {{
                    const permission = parameters.name;
                    if (permission === 'notifications') {{
                        return Promise.resolve({{ state: 'default' }});
                    }}
                    if (permission === 'geolocation') {{
                        return Promise.resolve({{ state: 'granted' }});
                    }}
                    return originalQuery ? originalQuery(parameters) : Promise.resolve({{ state: 'granted' }});
                }};
                
                // Enhanced Chrome object mock
                window.chrome = {{
                    runtime: {{
                        onConnect: null,
                        onMessage: null,
                        connect: function() {{ return {{ onMessage: null, onDisconnect: null, postMessage: function() {{}} }}; }},
                        sendMessage: function() {{}}
                    }},
                    storage: {{
                        local: {{
                            get: function() {{ return Promise.resolve({{}}); }},
                            set: function() {{ return Promise.resolve(); }}
                        }}
                    }},
                    loadTimes: function() {{
                        return {{
                            commitLoadTime: Date.now() / 1000 - Math.random() * 100,
                            connectionInfo: 'http/1.1',
                            finishDocumentLoadTime: Date.now() / 1000 - Math.random() * 10,
                            finishLoadTime: Date.now() / 1000 - Math.random() * 10,
                            firstPaintAfterLoadTime: Date.now() / 1000 - Math.random() * 10,
                            firstPaintTime: Date.now() / 1000 - Math.random() * 10,
                            navigationType: 'Other',
                            npnNegotiatedProtocol: 'http/1.1',
                            requestTime: Date.now() / 1000 - Math.random() * 200,
                            startLoadTime: Date.now() / 1000 - Math.random() * 200,
                            wasAlternateProtocolAvailable: false,
                            wasFetchedViaSpdy: false,
                            wasNpnNegotiated: false
                        }};
                    }}
                }};
                
                // Remove ALL automation traces
                delete window.__playwright;
                delete window.__puppeteer;
                delete window._phantom;
                delete window._selenium;
                delete window.callPhantom;
                delete window.callSelenium;
                delete window._Selenium_IDE_Recorder;
                delete window.__webdriver_script_func;
                delete window.__webdriver_evaluate;
                delete window.__selenium_evaluate;
                delete window.__fxdriver_evaluate;
                delete window.__driver_unwrapped;
                delete window.__webdriver_unwrapped;
                delete window.__driver_evaluate;
                delete window.__selenium_unwrapped;
                delete window.__fxdriver_unwrapped;
                
                // Remove CDP traces with enhanced detection
                Object.keys(window).forEach(key => {{
                    if (key.includes('cdc_') || key.includes('$cdc_') || key.includes('selenium') || 
                        key.includes('webdriver') || key.includes('driver') || key.includes('__nightmare')) {{
                        try {{ delete window[key]; }} catch(e) {{}}
                    }}
                }});
                
                // Enhanced WebGL spoofing
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {{
                    // Vendor and renderer spoofing with realistic values
                    if (parameter === 37445) return 'Intel Inc.';
                    if (parameter === 37446) return 'Intel Iris OpenGL Engine';
                    if (parameter === 35724) return 'WebGL 1.0 (OpenGL ES 2.0 Chromium)';
                    if (parameter === 37448) return 'OpenGL ES 2.0 Chromium';
                    return getParameter.apply(this, arguments);
                }};
                
                // Enhanced canvas fingerprinting resistance
                const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
                HTMLCanvasElement.prototype.toDataURL = function(...args) {{
                    // Add noise to canvas fingerprinting
                    const context = this.getContext('2d');
                    const imageData = context.getImageData(0, 0, this.width, this.height);
                    for (let i = 0; i < imageData.data.length; i += 4) {{
                        if (Math.random() < 0.001) {{
                            imageData.data[i] = imageData.data[i] ^ (Math.random() < 0.5 ? 1 : 2);
                        }}
                    }}
                    context.putImageData(imageData, 0, 0);
                    return originalToDataURL.apply(this, args);
                }};
                
                // Enhanced Date and timezone spoofing
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
                Date.parse = originalDate.parse;
                Date.UTC = originalDate.UTC;
                
                // Mock screen properties with realistic variations
                Object.defineProperty(screen, 'width', {{ get: () => {fingerprint['screen']['width']} }});
                Object.defineProperty(screen, 'height', {{ get: () => {fingerprint['screen']['height']} }});
                Object.defineProperty(screen, 'availWidth', {{ get: () => {fingerprint['screen']['width']} }});
                Object.defineProperty(screen, 'availHeight', {{ get: () => {fingerprint['screen']['height'] - 40} }});
                Object.defineProperty(screen, 'colorDepth', {{ get: () => 24 }});
                Object.defineProperty(screen, 'pixelDepth', {{ get: () => 24 }});
                
                // Enhanced mouse and keyboard event spoofing
                const originalAddEventListener = EventTarget.prototype.addEventListener;
                EventTarget.prototype.addEventListener = function(type, listener, options) {{
                    // Allow all events but add slight randomization to timing
                    if (type === 'mousemove' || type === 'click') {{
                        const wrappedListener = function(event) {{
                            // Add human-like delay
                            setTimeout(() => {{
                                if (typeof listener === 'function') {{
                                    listener.call(this, event);
                                }} else if (listener && typeof listener.handleEvent === 'function') {{
                                    listener.handleEvent(event);
                                }}
                            }}, Math.random() * 2);
                        }};
                        return originalAddEventListener.call(this, type, wrappedListener, options);
                    }}
                    return originalAddEventListener.call(this, type, listener, options);
                }};
                
                // Mock connection info for enhanced realism
                Object.defineProperty(navigator, 'connection', {{
                    get: () => ({{
                        effectiveType: '4g',
                        rtt: 50 + Math.random() * 50,
                        downlink: 10 + Math.random() * 5,
                        saveData: false
                    }})
                }});
                
                // Enhanced console protection
                const noop = () => {{}};
                ['debug', 'clear', 'error', 'info', 'log', 'warn', 'dir', 'dirxml', 'table', 'trace', 'group', 'groupCollapsed', 'groupEnd', 'time', 'timeEnd', 'profile', 'profileEnd', 'timeStamp'].forEach(method => {{
                    if (console[method]) {{
                        console[method] = noop;
                    }}
                }});
            """)
            
            return page
        except Exception as e:
            print(f"Error setting up stealth browser: {e}")
            raise
    
    async def simulate_human_interaction(self, page, platform: str):
        """Ultra-advanced human behavior simulation with platform-specific patterns"""
        try:
            config = self.platform_configs.get(platform, {})
            scroll_behavior = config.get('scroll_behavior', 'minimal')
            
            # Initial random wait - humans don't act immediately
            await asyncio.sleep(random.uniform(3, 6))
            
            # Simulate realistic mouse movements with Bézier curves
            for _ in range(random.randint(4, 8)):
                start_x = random.randint(100, 1800)
                start_y = random.randint(100, 800)
                end_x = random.randint(100, 1800)
                end_y = random.randint(100, 800)
                
                # Create Bézier curve for natural movement
                control_x = (start_x + end_x) / 2 + random.randint(-200, 200)
                control_y = (start_y + end_y) / 2 + random.randint(-200, 200)
                
                steps = random.randint(20, 40)
                for i in range(steps):
                    t = i / steps
                    # Quadratic Bézier curve
                    x = (1-t)**2 * start_x + 2*(1-t)*t * control_x + t**2 * end_x
                    y = (1-t)**2 * start_y + 2*(1-t)*t * control_y + t**2 * end_y
                    
                    await page.mouse.move(x, y)
                    await asyncio.sleep(random.uniform(0.005, 0.015))
                
                # Random pause at destination
                await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # Platform-specific scrolling behavior
            if scroll_behavior == 'ultra_gentle':
                # Ultra-gentle scrolling for Etsy (maximum stealth)
                scroll_positions = [100, 250, 150, 400, 300, 500, 350, 200]
                for pos in scroll_positions:
                    await page.evaluate(f"""
                        window.scrollTo({{
                            top: {pos},
                            behavior: 'smooth'
                        }});
                    """)
                    await asyncio.sleep(random.uniform(2, 4))
                    
                    # Simulate reading behavior
                    if random.random() > 0.6:
                        await asyncio.sleep(random.uniform(1, 3))
                        
            elif scroll_behavior == 'targeted':
                # Enhanced targeted scrolling for Walmart
                scroll_actions = [
                    {'top': 200, 'delay': random.uniform(1.5, 2.5)},
                    {'top': 500, 'delay': random.uniform(2, 3)},
                    {'top': 300, 'delay': random.uniform(1, 2)},
                    {'top': 700, 'delay': random.uniform(2, 3.5)},
                    {'top': 400, 'delay': random.uniform(1.5, 2)}
                ]
                
                for action in scroll_actions:
                    await page.evaluate(f"""
                        window.scrollTo({{
                            top: {action['top']},
                            behavior: 'smooth'
                        }});
                    """)
                    await asyncio.sleep(action['delay'])
                    
            elif scroll_behavior == 'gentle':
                # Gentle scrolling for other platforms
                for scroll_pos in [150, 350, 200, 450, 250]:
                    await page.evaluate(f"window.scrollTo({{top: {scroll_pos}, behavior: 'smooth'}})")
                    await asyncio.sleep(random.uniform(1.5, 2.5))
                    
            elif scroll_behavior == 'minimal':
                # Minimal scrolling
                await page.evaluate("window.scrollTo({top: 200, behavior: 'smooth'})")
                await asyncio.sleep(random.uniform(2, 3))
            
            # Random additional interactions
            if random.random() > 0.7:
                # Simulate hovering over elements
                try:
                    elements = await page.query_selector_all('button, a, img')
                    if elements:
                        random_element = random.choice(elements[:10])  # Only first 10 to avoid ads
                        await random_element.hover()
                        await asyncio.sleep(random.uniform(0.5, 1))
                except:
                    pass
            
            # Final realistic pause
            await asyncio.sleep(random.uniform(1, 2))
                
        except Exception as e:
            print(f"Error simulating human interaction: {e}")
    
    async def wait_for_content_load(self, page, platform: str):
        """Enhanced content loading detection with platform-specific optimizations"""
        try:
            config = self.platform_configs.get(platform, {})
            wait_time = config.get('wait_time', 5000)
            
            # Multi-stage loading detection
            try:
                await page.wait_for_load_state('domcontentloaded', timeout=wait_time // 2)
                await asyncio.sleep(2)
                await page.wait_for_load_state('networkidle', timeout=wait_time // 2)
            except:
                try:
                    await page.wait_for_load_state('load', timeout=wait_time)
                except:
                    pass
            
            # Platform-specific waiting strategies
            if platform == 'walmart':
                # Enhanced Walmart loading detection
                selectors_to_wait = [
                    '[data-seo-id="hero-price"]',
                    '[data-testid="price-wrap"]',
                    '[itemprop="price"]',
                    '[data-automation-id="product-price"]'
                ]
                
                for selector in selectors_to_wait:
                    try:
                        await page.wait_for_selector(selector, timeout=3000)
                        print(f"✅ Walmart: Found price selector {selector}")
                        break
                    except:
                        continue
                
                # Extra wait for dynamic pricing
                await asyncio.sleep(random.uniform(4, 6))
                
            elif platform == 'etsy':
                # Enhanced Etsy loading with maximum patience
                try:
                    await page.wait_for_selector('[data-testid="price"]', timeout=8000)
                except:
                    try:
                        await page.wait_for_selector('[data-buy-box-region="price"]', timeout=5000)
                    except:
                        pass
                # Extra stealth wait
                await asyncio.sleep(random.uniform(3, 5))
                
            elif platform == 'amazon':
                try:
                    await page.wait_for_selector('.a-price', timeout=4000)
                except:
                    pass
                await asyncio.sleep(2)
            
            # General JavaScript execution wait
            await page.wait_for_timeout(random.randint(2000, 4000))
            
            return True
        except Exception as e:
            print(f"Error waiting for content load: {e}")
            return True
    
    async def extract_walmart_price_enhanced(self, page) -> Optional[float]:
        """Enhanced Walmart price extraction with your specific selector priority"""
        try:
            print("🎯 Enhanced Walmart price extraction starting...")
            
            # Your priority selector first
            priority_selectors = [
                'span.inline-flex.flex-column span[itemprop="price"][data-seo-id="hero-price"]',
                'span[itemprop="price"][data-seo-id="hero-price"][data-fs-element="price"]',
                'span[itemprop="price"][data-seo-id="hero-price"]'
            ]
            
            # Try priority selectors first
            for i, selector in enumerate(priority_selectors):
                try:
                    elements = await page.query_selector_all(selector)
                    print(f"Priority selector {i+1}: {selector} found {len(elements)} elements")
                    
                    for element in elements:
                        price_text = await element.text_content()
                        if price_text:
                            price = await self.extract_price_from_text(price_text, 'walmart')
                            if price and 0.01 <= price <= 99999:
                                print(f"✅ WALMART PRIORITY: Found price ${price:.2f} with selector: {selector}")
                                return price
                except Exception as e:
                    print(f"Priority selector {selector} failed: {e}")
                    continue
            
            # If priority selectors fail, try standard selectors
            print("🔄 Priority selectors failed, trying standard Walmart selectors...")
            standard_selectors = [
                'div[data-testid="price-wrap"] span[itemprop="price"]',
                'span[data-automation-id="buybox-price"]',
                'div[data-testid="add-to-cart-price"] span[itemprop="price"]',
                'span[data-automation-id="product-price"]',
                'span[itemprop="price"]',
                'div.price-current span',
                '.price.display-inline-block span'
            ]
            
            for i, selector in enumerate(standard_selectors):
                try:
                    elements = await page.query_selector_all(selector)
                    print(f"Standard selector {i+1}: {selector} found {len(elements)} elements")
                    
                    for element in elements:
                        # Check if element is in main product area (not recommendations)
                        parent_html = await page.evaluate('''
                            (element) => {
                                let parent = element.closest('[data-testid="product-page"]') || 
                                           element.closest('main') ||
                                           element.closest('[data-automation-id="product-title"]');
                                return parent ? parent.innerHTML.substring(0, 1000) : '';
                            }
                        ''', element)
                        
                        if any(exclude in parent_html.lower() for exclude in ['recommendation', 'similar', 'sponsored', 'related']):
                            continue
                        
                        price_text = await element.text_content()
                        if price_text:
                            price = await self.extract_price_from_text(price_text, 'walmart')
                            if price and 0.01 <= price <= 99999:
                                print(f"✅ WALMART STANDARD: Found price ${price:.2f} with selector: {selector}")
                                return price
                except Exception as e:
                    print(f"Standard selector {selector} failed: {e}")
                    continue
            
            print("❌ All Walmart price selectors failed")
            return None
            
        except Exception as e:
            print(f"Error in Walmart price extraction: {e}")
            return None
    
    async def extract_accurate_price(self, page, platform: str, product_title: str = None) -> Optional[float]:
        """Ultra-accurate price extraction with enhanced platform-specific logic"""
        try:
            print(f"🔍 Extracting price for {platform}...")
            
            # Use enhanced Walmart extraction
            if platform == 'walmart':
                return await self.extract_walmart_price_enhanced(page)
            
            config = self.platform_configs.get(platform, {})
            price_selectors = config.get('price_selectors', [])
            exclude_selectors = config.get('exclude_selectors', [])
            
            print(f"Using {len(price_selectors)} selectors for {platform}")
            
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
                            
                            # Also check for price in data attributes
                            price_attr = None
                            try:
                                price_attr = await element.get_attribute('content')
                                if not price_attr:
                                    price_attr = await element.get_attribute('data-price')
                            except:
                                pass
                            
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
                                    print(f"Found valid price: {self.format_price(price, platform)} from text: '{price_text.strip()}'")
                            
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
                                    print(f"Found valid price: {self.format_price(price, platform)} from attribute: '{price_attr}'")
                                    
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
    
    def format_price(self, price: float, platform: str) -> str:
        """Format price display based on platform"""
        if platform == 'roblox':
            return f"{int(price)} Robux"
        else:
            return f"${price:.2f}"
    
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
                # Enhanced currency extraction for other platforms
                currency_patterns = [
                    r'\$(\d{1,4}(?:\.\d{1,2})?)',  # $123.45
                    r'USD\s*(\d{1,4}(?:\.\d{1,2})?)',  # USD 123.45
                    r'(\d{1,4}(?:\.\d{1,2})?)\s*\)',  # 123.45$
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
            main_prices = [p for p in prices if any(keyword in p.get('selector', '') for keyword in ['hero-price', 'buybox', 'add-to-cart'])]
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
        """Main scraping method with ultra-stealth and enhanced accuracy"""
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
                    '--disable-speech-api',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-features=TranslateUI',
                    '--disable-component-extensions-with-background-pages',
                    '--disable-default-apps',
                    '--disable-extensions',
                    '--disable-features=Translate',
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
                
                # Enhanced navigation with multiple fallback strategies
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
                await self.simulate_human_interaction(page, platform)
                
                # Extract product title for context
                title = await self.extract_product_title(page, platform)
                if not title:
                    print(f"⚠️ Could not extract title for {platform}")
                    title = f"Product from {platform.title()}"
                
                # Extract price with enhanced accuracy
                price = await self.extract_accurate_price(page, platform, title)
                
                if price:
                    formatted_price = self.format_price(price, platform)
                    print(f"✅ SUCCESS: {platform.upper()} - {title[:50]}... - {formatted_price}")
                    return title, price
                else:
                    print(f"❌ FAILED: Could not extract price for {platform}")
                    
                    # Debug: Save page content for analysis (only in development)
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


# Enhanced error handling and retry mechanism
class ScrapingRetryManager:
    """Manages retries and error handling for scraping operations with enhanced backoff"""
    
    def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
    
    async def execute_with_retry(self, scraper_func, *args, **kwargs):
        """Execute scraping function with enhanced retry logic"""
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


# Enhanced test function
async def test_enhanced_scraper():
    """Test the enhanced scraper with problematic URLs"""
    scraper = EnhancedMultiPlatformScraper()
    
    # Test URLs including your specific Walmart URL
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
            formatted_price = scraper.format_price(price, platform)
            print(f"✅ SUCCESS: {title} - {formatted_price}")
        else:
            print("❌ FAILED to scrape")
        
        # Wait between tests
        print("⏳ Waiting 10 seconds before next test...")
        await asyncio.sleep(10)


# Main execution
if __name__ == "__main__":
    print("🚀 Enhanced Multi-Platform Scraper - ULTRA STEALTH MODE")
    print("🎯 Enhanced Walmart Detection with Priority Selectors")
    print("🛡️ Maximum Etsy Bot Evasion")
    print("=" * 60)
    
    # Test the scraper
    asyncio.run(test_enhanced_scraper())