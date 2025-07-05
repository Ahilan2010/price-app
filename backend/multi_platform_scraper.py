# backend/multi_platform_scraper.py - IMPROVED VERSION WITH BETTER RELIABILITY
import asyncio
import re
import random
from typing import Optional, Tuple, Dict
from urllib.parse import urlparse
from playwright.async_api import async_playwright
import time

class MultiPlatformScraper:
    """Enhanced e-commerce scraper with improved reliability for major platforms"""
    
    def __init__(self):
        # Enhanced platform-specific selectors with better reliability
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
                    'span.a-price-whole',
                    '.a-price-whole',
                    'span.a-price.a-text-price.a-size-medium.apexPriceToPay .a-offscreen',
                    '.a-price .a-offscreen',
                    'span[class*="a-price-range"]',
                    '.a-price-current .a-offscreen',
                    'span.a-price.a-text-price.apexPriceToPay .a-offscreen',
                    '.price .a-offscreen',
                    '#priceblock_dealprice',
                    '#priceblock_ourprice',
                    '.a-size-medium.a-color-price'
                ],
                'wait_time': 5000,
                'user_agents': [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
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
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ]
            },
            'etsy': {
                'domain_patterns': ['etsy.com'],
                'title_selectors': [
                    'h1[data-test-id="listing-page-title"]',
                    'h1[data-buy-box-listing-title="true"]',
                    'h1[data-buy-box-listing-title]',
                    'h1.wt-break-word',
                    'h1'
                ],
                'price_selectors': [
                    'p[data-test-id="lp-price"] span.currency-value',
                    'p.wt-text-title-larger',
                    'p[data-buy-box-region="price"]',
                    '.wt-text-title-larger',
                    'p[class*="price"]',
                    '.currency-value'
                ],
                'wait_time': 3000,
                'user_agents': [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ]
            },
            'walmart': {
                'domain_patterns': ['walmart.com'],
                'title_selectors': [
                    'h1[data-automation-id="product-title"]',
                    'h1.prod-ProductTitle',
                    'h1[data-testid="product-title"]',
                    '.prod-ProductTitle h1',
                    'h1'
                ],
                'price_selectors': [
                    'span[data-automation-id="product-price"]',
                    'span.price-current',
                    '.price-current .price-num',
                    'span.visuallyhidden[aria-label*="current price"]',
                    '.price .price-num',
                    '[data-testid="price-current"]'
                ],
                'wait_time': 4000,
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
            }
        }
    
    def detect_platform(self, url: str) -> Optional[str]:
        """Detect which e-commerce platform the URL belongs to"""
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
    
    async def stealth_browser_setup(self, browser):
        """Enhanced stealth setup to avoid detection"""
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='America/New_York',
            # Add extra headers to look more legitimate
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
        
        # Remove webdriver property and other detection methods
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
            
            // Mock plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            
            // Mock languages
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en'],
            });
            
            // Override permissions
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
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
            if platform == 'amazon':
                # Try to hover over product image or similar elements
                try:
                    await page.hover('#landingImage', timeout=2000)
                except:
                    pass
            elif platform == 'ebay':
                # Scroll to price section
                try:
                    await page.evaluate("document.querySelector('.price')?.scrollIntoView()")
                except:
                    pass
            
            # Final random wait
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
        except Exception as e:
            print(f"⚠️ Human behavior simulation failed: {e}")
    
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
                            if (text.match(/\$\d+/) && element.offsetParent !== null) {
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
    
    async def scrape_product(self, url: str) -> Optional[Tuple[str, float]]:
        """Enhanced product scraping with better error handling and stealth"""
        platform = self.detect_platform(url)
        
        if not platform:
            print(f"❌ Unsupported platform for URL: {url}")
            return None
        
        config = self.platform_configs[platform]
        user_agent = self.get_random_user_agent(platform)
        
        async with async_playwright() as p:
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
                        '--disable-ipc-flooding-protection',
                        f'--user-agent={user_agent}'
                    ]
                )
                
                page = await self.stealth_browser_setup(browser)
                
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
                
                # Extract price with enhanced methods
                print(f"💰 Extracting price for {platform}...")
                price = None
                
                # Try each price selector
                for i, selector in enumerate(config['price_selectors']):
                    try:
                        elements = await page.query_selector_all(selector)
                        for element in elements:
                            price_text = await element.text_content()
                            if price_text:
                                print(f"📄 Price text from selector #{i+1}: '{price_text[:50]}'")
                                price = await self.extract_price_from_text(price_text)
                                if price and price > 0:
                                    break
                        if price and price > 0:
                            break
                    except Exception as e:
                        print(f"⚠️ Price selector #{i+1} failed: {str(e)[:50]}")
                        continue
                
                # Enhanced JavaScript fallback for price
                if not price:
                    print(f"🔧 Trying enhanced JavaScript fallback for price...")
                    try:
                        price_candidates = await page.evaluate('''
                            () => {
                                const results = [];
                                const elements = document.querySelectorAll('*');
                                
                                for (const element of elements) {
                                    const text = element.textContent || '';
                                    const innerHTML = element.innerHTML || '';
                                    
                                    // Look for price patterns in text content
                                    if (text.match(/[\$€£¥₹]\s*\d+/) || text.match(/\d+[\$€£¥₹]/) || 
                                        text.match(/price/i) || text.match(/cost/i)) {
                                        if (element.offsetParent !== null) { // visible element
                                            results.push(text.trim());
                                        }
                                    }
                                }
                                
                                return results.slice(0, 10); // Return top 10 candidates
                            }
                        ''')
                        
                        print(f"🔍 JavaScript found price candidates: {price_candidates[:3]}")
                        for price_text in price_candidates:
                            price = await self.extract_price_from_text(price_text)
                            if price and price > 0:
                                break
                    except Exception as e:
                        print(f"⚠️ Enhanced JavaScript price extraction failed: {e}")
                
                # Final validation
                if not title:
                    print(f"❌ Could not extract title for {platform}")
                    return None
                
                if not price:
                    print(f"❌ Could not extract price for {platform}")
                    return None
                
                # Clean up title
                title = title[:200]  # Limit title length
                
                print(f"✅ Successfully scraped {platform.title()}:")
                print(f"   📝 Title: {title[:50]}...")
                print(f"   💰 Price: ${price:.2f}")
                return title, price
                
            except Exception as e:
                print(f"❌ Error scraping {platform}: {str(e)}")
                return None
            
            finally:
                if 'browser' in locals():
                    await browser.close()
    
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
                'icon': '🛒'
            },
            'ebay': {
                'name': 'eBay',
                'example_url': 'https://www.ebay.com/itm/123456789012',
                'icon': '🏷️'
            },
            'etsy': {
                'name': 'Etsy',
                'example_url': 'https://www.etsy.com/listing/123456789/handmade-product-name',
                'icon': '🎨'
            },
            'walmart': {
                'name': 'Walmart',
                'example_url': 'https://www.walmart.com/ip/Product-Name/123456789',
                'icon': '🏪'
            },
            'storenvy': {
                'name': 'Storenvy',
                'example_url': 'https://store-name.storenvy.com/products/123456-product-name',
                'icon': '🏬'
            }
        }


# Test function
async def test_improved_scraper():
    """Test function to verify the improved scraper works"""
    scraper = MultiPlatformScraper()
    
    print("Testing Improved Multi-Platform Scraper")
    print("=" * 50)
    
    # Test URLs for different platforms
    test_urls = [
        "https://www.amazon.com/dp/B08N5WRWNW",  # Amazon Echo
        "https://www.ebay.com/itm/123456789012",  # Generic eBay item
    ]
    
    for url in test_urls:
        print(f"\n🎯 Testing URL: {url}")
        result = await scraper.scrape_product(url)
        if result:
            title, price = result
            print(f"✅ Success: {title[:50]}... - ${price:.2f}")
        else:
            print(f"❌ Failed to scrape")

if __name__ == "__main__":
    asyncio.run(test_improved_scraper())