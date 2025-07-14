# backend/multi_platform_scraper.py - ENHANCED STEALTH VERSION WITHOUT FLIGHTS
import asyncio
import re
import random
import json
from typing import Optional, Tuple, Dict, List
from urllib.parse import urlparse
from playwright.async_api import async_playwright
import time
from datetime import datetime


class MultiPlatformScraper:
    """Enhanced multi-platform e-commerce scraper with advanced stealth capabilities"""
    
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
                    'div#title_feature_div span',
                    'div#titleSection h1 span'
                ],
                'price_selectors': [
                    'span.a-price.a-text-price.a-size-medium.apexPriceToPay span.a-offscreen',
                    'span.a-price.a-text-price.apexPriceToPay span.a-offscreen',
                    'span.a-price-current span.a-offscreen',
                    'span.a-price.aok-align-center.reinventPricePriceToPayMargin span.a-offscreen',
                    'span.a-price.a-size-medium.a-color-price span.a-offscreen',
                    'div[data-feature-name="apex_desktop"] span.a-price-whole',
                    'span.a-price-range span.a-offscreen',
                    '#priceblock_dealprice',
                    '#priceblock_ourprice',
                    '.a-price .a-offscreen'
                ],
                'wait_time': 5000,
                'user_agents': [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
                ]
            },
            'ebay': {
                'domain_patterns': ['ebay.com', 'ebay.co.uk', 'ebay.ca', 'ebay.de', 'ebay.fr'],
                'title_selectors': [
                    'h1.x-item-title__mainTitle span.ux-textspans--BOLD',
                    'h1[data-testid="x-item-title-textual"]',
                    'h1.it-ttl',
                    'div.vi-swc-lsp h1',
                    'h1.x-item-title-mainTitle span',
                    '.x-item-title__mainTitle span'
                ],
                'price_selectors': [
                    'div.x-price-primary span.ux-textspans',
                    'span.ux-textspans.ux-textspans--DISPLAY.ux-textspans--BOLD',
                    'div.mainPrice span.notranslate',
                    '#prcIsum',
                    'span[itemprop="price"]',
                    '.x-price-primary span[data-testid="x-price-primary"]'
                ],
                'wait_time': 4000,
                'user_agents': [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
                ]
            },
            'etsy': {
                'domain_patterns': ['etsy.com'],
                'title_selectors': [
                    'h1[data-buy-box-listing-title]',
                    'h1.wt-text-body-01',
                    'h1[data-listing-page-title-component]',
                    'div[data-region="listing-title"] h1'
                ],
                'price_selectors': [
                    'div[data-buy-box-region="price"] p[data-selector="price-only"]',
                    'p.wt-text-title-larger span.currency-value',
                    'div[data-selector="listing-page-cart"] span.currency-value',
                    'span.wt-text-title-largest'
                ],
                'wait_time': 4000,
                'user_agents': [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
                ]
            },
            'walmart': {
                'domain_patterns': ['walmart.com'],
                'title_selectors': [
                    'h1[itemprop="name"]',
                    'h1.prod-ProductTitle',
                    'h1[data-automation="product-title"]',
                    'main h1'
                ],
                'price_selectors': [
                    'span[itemprop="price"]',
                    'span[data-automation="buybox-price"]',
                    'div[data-testid="add-to-cart-price"] span',
                    'span.price.display-inline-block.arrange-fit'
                ],
                'wait_time': 5000,
                'user_agents': [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
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
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
                ]
            },
            'roblox': {
                'domain_patterns': ['roblox.com'],
                'title_selectors': [
                    'h1.item-name-container',
                    'div.item-name-container h1',
                    '[data-testid="item-details-name"]',
                    'div.item-details-name-container h1',
                    'h1.text-display-1'
                ],
                'price_selectors': [
                    'span.text-robux-lg',
                    'span.icon-robux-price-container',
                    '[data-testid="item-details-price"] .text-robux',
                    'div.price-container span.text-robux',
                    'span.text-label[class*="robux"]'
                ],
                'wait_time': 5000,
                'user_agents': [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
                ],
                'currency': 'robux'
            }
        }
    
    def detect_platform(self, url: str) -> Optional[str]:
        """Detect which platform the URL belongs to"""
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
    
    def get_random_user_agent(self, platform: str) -> str:
        """Get a random user agent for the platform"""
        config = self.platform_configs.get(platform, {})
        user_agents = config.get('user_agents', [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        ])
        return random.choice(user_agents)
    
    async def setup_stealth_browser(self, browser, platform: str):
        """Set up browser page with advanced stealth configuration"""
        try:
            user_agent = self.get_random_user_agent(platform)
            
            # Enhanced context options for stealth
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                screen={'width': 1920, 'height': 1080},
                locale='en-US',
                timezone_id='America/New_York',
                user_agent=user_agent,
                has_touch=False,
                is_mobile=False,
                java_script_enabled=True,
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
                    'Cache-Control': 'max-age=0'
                },
                # Enhanced permissions
                permissions=['geolocation'],
                geolocation={'latitude': 40.7128, 'longitude': -74.0060},
                color_scheme='light',
                reduced_motion='no-preference',
                forced_colors='none'
            )
            
            page = await context.new_page()
            
            # Advanced stealth scripts
            await page.add_init_script("""
                // Enhanced stealth mode
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Mock plugins with realistic data
                Object.defineProperty(navigator, 'plugins', {
                    get: () => {
                        return [
                            {
                                0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format"},
                                description: "Portable Document Format",
                                filename: "internal-pdf-viewer",
                                length: 1,
                                name: "Chrome PDF Plugin"
                            },
                            {
                                0: {type: "application/pdf", suffixes: "pdf", description: "Portable Document Format"},
                                description: "Portable Document Format", 
                                filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                                length: 1,
                                name: "Chrome PDF Viewer"
                            }
                        ];
                    }
                });
                
                // Mock languages properly
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
                
                // Mock permissions correctly
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
                
                // Mock chrome object
                window.chrome = {
                    runtime: {
                        id: "fake-extension-id",
                        connect: () => {},
                        sendMessage: () => {}
                    },
                    loadTimes: () => {},
                    csi: () => {}
                };
                
                // Override the instanceof check for CanvasRenderingContext2D
                const originalToString = Object.prototype.toString;
                Object.prototype.toString = function() {
                    if (this instanceof CanvasRenderingContext2D) {
                        return '[object CanvasRenderingContext2D]';
                    }
                    return originalToString.call(this);
                };
                
                // Remove Playwright/Puppeteer traces
                delete window.__playwright;
                delete window.__puppeteer;
                delete window._phantom;
                delete window._selenium;
                delete window.callPhantom;
                delete window.callSelenium;
                delete window._Selenium_IDE_Recorder;
                
                // Remove CDP traces
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            """)
            
            # Additional script for WebGL vendor spoofing
            await page.add_init_script("""
                const getParameter = WebGLRenderingContext.prototype.getParameter;
                WebGLRenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) {
                        return 'Intel Inc.';
                    }
                    if (parameter === 37446) {
                        return 'Intel Iris OpenGL Engine';
                    }
                    return getParameter.apply(this, arguments);
                };
                
                const getParameter2 = WebGL2RenderingContext.prototype.getParameter;
                WebGL2RenderingContext.prototype.getParameter = function(parameter) {
                    if (parameter === 37445) {
                        return 'Intel Inc.';
                    }
                    if (parameter === 37446) {
                        return 'Intel Iris OpenGL Engine';
                    }
                    return getParameter2.apply(this, arguments);
                };
            """)
            
            return page
        except Exception as e:
            print(f"Error setting up stealth browser: {e}")
            raise
    
    async def simulate_human_behavior(self, page, platform: str):
        """Enhanced human behavior simulation"""
        try:
            # Random initial wait
            await asyncio.sleep(random.uniform(1.5, 3))
            
            # Smooth random mouse movements
            for _ in range(random.randint(2, 4)):
                x1 = random.randint(100, 1200)
                y1 = random.randint(100, 800)
                x2 = random.randint(100, 1200)
                y2 = random.randint(100, 800)
                
                # Create smooth movement path
                steps = random.randint(10, 20)
                for i in range(steps):
                    t = i / steps
                    x = x1 + (x2 - x1) * t
                    y = y1 + (y2 - y1) * t
                    await page.mouse.move(x, y)
                    await asyncio.sleep(random.uniform(0.01, 0.03))
                
                await asyncio.sleep(random.uniform(0.2, 0.5))
            
            # Natural scrolling pattern
            current_position = 0
            scroll_targets = [300, 600, 400, 800, 200]
            
            for target in scroll_targets[:random.randint(2, 4)]:
                # Smooth scroll animation
                steps = random.randint(15, 25)
                for i in range(steps):
                    t = i / steps
                    # Easing function for natural movement
                    eased_t = t * t * (3.0 - 2.0 * t)
                    position = current_position + (target - current_position) * eased_t
                    await page.evaluate(f"window.scrollTo({{top: {position}, behavior: 'auto'}})")
                    await asyncio.sleep(random.uniform(0.01, 0.02))
                
                current_position = target
                await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # Random hover over elements
            if random.random() > 0.5:
                await page.mouse.move(
                    random.randint(400, 800),
                    random.randint(200, 600)
                )
                await asyncio.sleep(random.uniform(0.2, 0.4))
                
        except Exception as e:
            print(f"Error simulating human behavior: {e}")
    
    async def wait_for_content_load(self, page, platform: str):
        """Wait for platform-specific content to load"""
        try:
            config = self.platform_configs.get(platform, {})
            wait_time = config.get('wait_time', 5000)
            
            # Wait for page to be fully loaded
            await page.wait_for_load_state('networkidle', timeout=wait_time)
            
            # Additional platform-specific waits
            if platform == 'amazon':
                try:
                    await page.wait_for_selector('span#productTitle', timeout=3000)
                except:
                    pass
            elif platform == 'roblox':
                try:
                    await page.wait_for_selector('.item-name-container', timeout=3000)
                except:
                    pass
            
            # General wait
            await page.wait_for_timeout(1000)
            return True
            
        except Exception as e:
            print(f"Error waiting for content load: {e}")
            return True
    
    async def extract_text_content(self, page, selectors: List[str]) -> Optional[str]:
        """Extract text content using multiple selectors with improved error handling"""
        for i, selector in enumerate(selectors):
            try:
                # Try different methods to get the element
                element = await page.query_selector(selector)
                if element:
                    # Try multiple methods to get text
                    text = None
                    try:
                        text = await element.text_content()
                    except:
                        try:
                            text = await element.inner_text()
                        except:
                            try:
                                text = await page.evaluate(f'(el) => el.textContent', element)
                            except:
                                pass
                    
                    if text and text.strip():
                        print(f"Found content with selector #{i+1}: {selector}")
                        return text.strip()
            except Exception as e:
                continue
        return None
    
    async def extract_price_from_text(self, price_text: str) -> Optional[float]:
        """Extract price from text with improved regex"""
        if not price_text:
            return None
        
        try:
            # Clean the text
            cleaned_text = re.sub(r'[^\d.,\-\s$€£¥₹]', ' ', price_text)
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
            
            # Enhanced price patterns
            patterns = [
                r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)',
                r'(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)\s*\$',
                r'(\d{1,3}(?:,\d{3})*\.\d{2})',
                r'(\d{1,3}(?:,\d{3})*)',
                r'(\d+\.\d{2})',
                r'(\d+)'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, cleaned_text)
                if matches:
                    for match in matches:
                        try:
                            price_str = match.replace(',', '').strip()
                            price = float(price_str)
                            if 0.01 <= price <= 999999:
                                return price
                        except (ValueError, TypeError):
                            continue
            
            return None
        except Exception as e:
            print(f"Error extracting price: {e}")
            return None
    
    async def extract_robux_from_text(self, price_text: str) -> Optional[float]:
        """Extract Robux price from text"""
        if not price_text:
            return None
        
        try:
            # Clean the text
            cleaned_text = re.sub(r'[^\d,]', '', price_text)
            
            if cleaned_text:
                price_str = cleaned_text.replace(',', '')
                price = float(price_str)
                if 1 <= price <= 999999:
                    return price
            
            return None
        except Exception as e:
            print(f"Error extracting Robux: {e}")
            return None
    
    async def scrape_product(self, url: str) -> Optional[Tuple[str, float]]:
        """Main scraping method with enhanced stealth"""
        platform = self.detect_platform(url)
        if not platform:
            print(f"Unsupported platform for URL: {url}")
            return None
        
        print(f"Detected platform: {platform}")
        
        async with async_playwright() as p:
            # Enhanced browser launch options
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--disable-site-isolation-trials',
                    '--disable-web-security',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--no-sandbox',
                    '--disable-gpu',
                    '--disable-setuid-sandbox',
                    '--disable-dev-tools',
                    f'--user-agent={self.get_random_user_agent(platform)}'
                ]
            )
            
            try:
                page = await self.setup_stealth_browser(browser, platform)
                config = self.platform_configs[platform]
                
                print(f"Navigating to: {url}")
                
                # Navigate with timeout and error handling
                try:
                    response = await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                    
                    if response and response.status >= 400:
                        print(f"Page returned status {response.status}")
                        # Try again with a different approach
                        await page.goto(url, wait_until='load', timeout=30000)
                except Exception as e:
                    print(f"Navigation error: {e}, retrying...")
                    await page.goto(url, wait_until='networkidle', timeout=30000)
                
                # Wait for content to load
                await self.wait_for_content_load(page, platform)
                
                # Simulate human behavior
                await self.simulate_human_behavior(page, platform)
                
                # Extract title
                title = await self.extract_text_content(page, config['title_selectors'])
                if not title:
                    print(f"Could not extract title for {platform}")
                    title = f"Product from {platform.title()}"
                
                # Extract price
                price = None
                for price_selector in config['price_selectors']:
                    try:
                        price_element = await page.query_selector(price_selector)
                        if price_element:
                            price_text = await price_element.text_content()
                            if price_text:
                                if platform == 'roblox':
                                    price = await self.extract_robux_from_text(price_text)
                                else:
                                    price = await self.extract_price_from_text(price_text)
                                
                                if price:
                                    break
                    except Exception:
                        continue
                
                if price:
                    if platform == 'roblox':
                        print(f"Successfully scraped: {title[:50]}... - {int(price)} Robux")
                    else:
                        print(f"Successfully scraped: {title[:50]}... - ${price:.2f}")
                    return title, price
                else:
                    print(f"Failed to extract price for {url}")
                    return None
                
            except Exception as e:
                print(f"Error scraping {url}: {str(e)}")
                return None
            finally:
                await browser.close()
    
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


# Test function
async def test_scraper():
    """Test the enhanced scraper"""
    scraper = MultiPlatformScraper()
    
    test_urls = [
        "https://www.amazon.com/dp/B08N5WRWNW",
        "https://www.etsy.com/listing/123456789/test-product",
        "https://www.roblox.com/catalog/123456789/test-item",
    ]
    
    for url in test_urls:
        print(f"\n{'='*60}")
        print(f"Testing: {url}")
        print('='*60)
        
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


if __name__ == "__main__":
    asyncio.run(test_scraper())