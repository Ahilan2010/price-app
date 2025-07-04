# backend/multi_platform_scraper.py - Updated with Manual Inspection Selectors (2024)
import asyncio
import re
import random
from typing import Optional, Tuple, Dict
from urllib.parse import urlparse
from playwright.async_api import async_playwright
import time

class MultiPlatformScraper:
    """Universal e-commerce scraper supporting 7 major platforms with manually verified selectors"""
    
    def __init__(self):
        # Platform-specific selectors based on manual inspection (January 2024)
        self.platform_configs = {
            'amazon': {
                'domain_patterns': ['amazon.com', 'amazon.co', 'amazon.ca', 'amazon.in', 'amazon.de', 'amazon.fr'],
                'title_selectors': [
                    # Based on manual inspection - Amazon uses these exact selectors
                    'span#productTitle.a-size-large.product-title-word-break',
                    'span#productTitle',
                    'h1#title span',
                    'h1.a-size-large span',
                    '.product-title-word-break',
                    # Fallback selectors
                    'h1#title',
                    'h1[id*="title"]',
                    'h1'
                ],
                'price_selectors': [
                    # Based on manual inspection - Amazon price structure
                    'span.a-price-whole',
                    '.a-price-whole',
                    'span.a-price-range',
                    '.a-price.a-text-price.a-size-medium.apexPriceToPay .a-offscreen',
                    '.a-price .a-offscreen',
                    'span[class*="a-price"]',
                    # Fallback price selectors
                    '[class*="price"]'
                ],
                'wait_time': 3000,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            },
            'alibaba': {
                'domain_patterns': ['alibaba.com'],
                'title_selectors': [
                    # Based on manual inspection - Alibaba h1 with title attribute
                    'h1[title]',
                    'h1[data-spm-anchor-id]',
                    'h1',
                    '.product-title h1',
                    '.pdp-product-name h1',
                    # Fallback selectors
                    '[class*="title"]',
                    'h1[class*="title"]'
                ],
                'price_selectors': [
                    # Based on manual inspection - Alibaba strong with specific classes
                    'strong.id-me-1.id-text-2xl.id-font-bold',
                    'strong[class*="id-text"]',
                    'strong[data-spm-anchor-id]',
                    'strong[class*="font-bold"]',
                    '.price-main',
                    '.price-current',
                    # Fallback price selectors
                    'strong',
                    '[class*="price"]'
                ],
                'wait_time': 5000,
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            },
            'ebay': {
                'domain_patterns': ['ebay.com', 'ebay.co.uk', 'ebay.ca', 'ebay.de', 'ebay.fr'],
                'title_selectors': [
                    # Based on manual inspection - eBay span with ux-textspans classes
                    'span.ux-textspans.ux-textspans--BOLD',
                    'span.ux-textspans--BOLD',
                    'span.ux-textspans',
                    'h1.it-ttl',
                    'h1[data-testid="x-item-title-label"]',
                    # Fallback selectors
                    'h1',
                    '[class*="title"]'
                ],
                'price_selectors': [
                    # Based on manual inspection - eBay span with ux-textspans for price
                    'span.ux-textspans',
                    'span[class*="ux-textspans"]',
                    'span.notranslate',
                    '.x-price-primary',
                    'span[itemprop="price"]',
                    # Fallback price selectors
                    '[class*="price"]',
                    'span[class*="price"]'
                ],
                'wait_time': 2500,
                'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            },
            'walmart': {
                'domain_patterns': ['walmart.com'],
                'title_selectors': [
                    # Based on manual inspection - Walmart h1 with specific attributes
                    'h1[data-pcss-show="true"][id="main-title"]',
                    'h1#main-title',
                    'h1[data-seo-id="hero-carousel-image"]',
                    'h1[itemprop="name"]',
                    'h1[data-fs-element="name"]',
                    'h1.lh-copy.dark-gray',
                    # Fallback selectors
                    'h1',
                    '[data-automation-id="product-title"]'
                ],
                'price_selectors': [
                    # Based on manual inspection - Walmart span with itemprop price
                    'span[itemprop="price"][data-seo-id="hero-price"]',
                    'span[itemprop="price"]',
                    'span[data-seo-id="hero-price"]',
                    'span[data-fs-element="price"]',
                    '.price-characteristic',
                    # Fallback price selectors
                    '[class*="price"]',
                    'span[class*="price"]'
                ],
                'wait_time': 3500,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0'
            },
            'flipkart': {
                'domain_patterns': ['flipkart.com'],
                'title_selectors': [
                    # Based on manual inspection - Flipkart span with VU-ZEz class
                    'span.VU-ZEz',
                    'span[class*="VU-"]',
                    'h1.yhB1nd',
                    'span.B_NuCI',
                    'h1._9E25nV',
                    # Fallback selectors
                    'h1',
                    '[class*="title"]'
                ],
                'price_selectors': [
                    # Based on manual inspection - Flipkart div with Nx9bqj CxhGGd classes
                    'div.Nx9bqj.CxhGGd',
                    'div[class*="Nx9bqj"]',
                    'div[class*="CxhGGd"]',
                    'div._30jeq3',
                    'div._16Jk6d',
                    # Fallback price selectors
                    'div[class*="price"]',
                    '[class*="price"]'
                ],
                'wait_time': 3500,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            },
            'etsy': {
                'domain_patterns': ['etsy.com'],
                'title_selectors': [
                    # Based on manual inspection - Etsy h1 with data-buy-box-listing-title
                    'h1[data-buy-box-listing-title="true"]',
                    'h1[data-buy-box-listing-title]',
                    'h1.wt-line-height-tight.wt-break-word.wt-text-body',
                    'h1.wt-break-word',
                    'h1.wt-text-body-01',
                    # Fallback selectors
                    'h1',
                    '[class*="listing-title"]'
                ],
                'price_selectors': [
                    # Based on manual inspection - Etsy p with wt-text-title-larger classes
                    'p.wt-text-title-larger.wt-mr-xs-1.wt-text-black',
                    'p.wt-text-title-larger',
                    'p[class*="wt-text-title-larger"]',
                    'p[data-buy-box-region="price"]',
                    '.wt-text-title-larger',
                    # Fallback price selectors
                    '[class*="price"]',
                    'p[class*="price"]'
                ],
                'wait_time': 2500,
                'user_agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0'
            },
            'storenvy': {
                'domain_patterns': ['storenvy.com'],
                'title_selectors': [
                    # Keeping original Storenvy selectors as requested
                    'h1.product-name',
                    'h1.product_name',
                    'h1[itemprop="name"]',
                    '.product-header h1',
                    '.product_name',
                    # Fallback selectors
                    'h1'
                ],
                'price_selectors': [
                    # Keeping original Storenvy selectors as requested
                    'div.price.vprice[itemprop="price"]',
                    'div.price.vprice',
                    'div[itemprop="price"]',
                    '.price.vprice',
                    'span.product-price',
                    '.product-price',
                    'span.price:not(.sale-price):not(.discount-price)',
                    # Fallback selectors
                    '.price'
                ],
                'wait_time': 3000,
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
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
    
    def get_random_user_agent(self) -> str:
        """Get a random user agent to appear more human-like"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'
        ]
        return random.choice(user_agents)
    
    async def human_like_behavior(self, page):
        """Simulate human-like behavior on the page"""
        try:
            # Random mouse movements
            for _ in range(random.randint(2, 4)):
                x = random.randint(100, 800)
                y = random.randint(100, 600)
                await page.mouse.move(x, y)
                await asyncio.sleep(random.uniform(0.1, 0.3))
            
            # Random scroll
            await page.evaluate(f"window.scrollBy(0, {random.randint(100, 300)})")
            await asyncio.sleep(random.uniform(0.5, 1.0))
        except Exception as e:
            print(f"⚠️ Human behavior simulation failed: {e}")
    
    async def extract_with_fallbacks(self, page, selectors: list, extract_type: str = "text") -> Optional[str]:
        """Extract content using multiple selector fallbacks"""
        for i, selector in enumerate(selectors):
            try:
                # Wait for selector with short timeout
                element = await page.wait_for_selector(selector, timeout=2000)
                if element:
                    if extract_type == "text":
                        content = await element.text_content()
                        if content and len(content.strip()) > 0:
                            print(f"✅ Found content with selector #{i+1}: {selector}")
                            return content.strip()
                    elif extract_type == "attribute":
                        content = await element.get_attribute("content")
                        if content:
                            print(f"✅ Found attribute content with selector #{i+1}: {selector}")
                            return content.strip()
            except Exception as e:
                print(f"⚠️ Selector #{i+1} failed ({selector}): {e}")
                continue
        
        return None
    
    async def extract_price_from_text(self, price_text: str) -> Optional[float]:
        """Extract numeric price from text using improved regex patterns"""
        if not price_text:
            return None
        
        print(f"🔍 Extracting price from text: '{price_text}'")
        
        # Remove currency symbols and clean text
        cleaned_text = re.sub(r'[^\d.,\-\s€$¥£₹]', '', price_text)
        print(f"🧹 Cleaned text: '{cleaned_text}'")
        
        # Find price patterns (handles various formats)
        price_patterns = [
            r'(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)',  # 1,234.56 or 123.45
            r'(\d+\.\d{1,2})',                      # 123.45
            r'(\d+,\d{1,2})',                       # 123,45 (European format)
            r'(\d+)'                                # 123 (whole numbers)
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, cleaned_text)
            if matches:
                try:
                    # Take the first valid match
                    price_str = matches[0].replace(',', '')
                    price = float(price_str)
                    if price > 0:
                        print(f"💰 Extracted price: ${price}")
                        return price
                except (ValueError, IndexError):
                    continue
        
        print(f"❌ Could not extract price from: '{price_text}'")
        return None
    
    async def scrape_product(self, url: str) -> Optional[Tuple[str, float]]:
        """Enhanced scrape product with manually verified selectors"""
        platform = self.detect_platform(url)
        
        if not platform:
            print(f"❌ Unsupported platform for URL: {url}")
            return None
        
        config = self.platform_configs[platform]
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-accelerated-2d-canvas',
                    '--disable-gpu',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding'
                ]
            )
            
            # Create context with platform-specific user agent
            context = await browser.new_context(
                user_agent=config.get('user_agent', self.get_random_user_agent()),
                viewport={
                    'width': random.randint(1200, 1920),
                    'height': random.randint(800, 1080)
                },
                locale='en-US',
                timezone_id='America/New_York',
                extra_http_headers={
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none'
                }
            )
            
            page = await context.new_page()
            
            try:
                print(f"🔍 Scraping {platform.title()} product: {url[:60]}...")
                
                # Navigate to the URL
                await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                
                # Wait for the page to load with platform-specific wait time
                print(f"⏳ Waiting {config['wait_time']}ms for {platform} to load...")
                await page.wait_for_timeout(config['wait_time'])
                
                # Simulate human behavior
                await self.human_like_behavior(page)
                
                # Extract title using manually verified selectors
                print(f"📝 Extracting title for {platform}...")
                title = await self.extract_with_fallbacks(page, config['title_selectors'])
                
                if not title:
                    # Try JavaScript extraction as last resort for title
                    print(f"🔧 Trying JavaScript fallback for title...")
                    title = await page.evaluate('''
                        () => {
                            const titleElement = document.querySelector('h1') || 
                                                document.querySelector('[class*="title"]') ||
                                                document.querySelector('[data-testid*="title"]');
                            return titleElement ? titleElement.textContent.trim() : document.title.split(' - ')[0];
                        }
                    ''')
                
                # Extract price using manually verified selectors
                print(f"💰 Extracting price for {platform}...")
                price = None
                for i, selector in enumerate(config['price_selectors']):
                    try:
                        element = await page.wait_for_selector(selector, timeout=2000)
                        if element:
                            price_text = await element.text_content()
                            print(f"📄 Price text from selector #{i+1} ({selector}): '{price_text}'")
                            price = await self.extract_price_from_text(price_text)
                            if price and price > 0:
                                break
                    except Exception as e:
                        print(f"⚠️ Price selector #{i+1} failed ({selector}): {e}")
                        continue
                
                # JavaScript fallback for price extraction
                if not price:
                    print(f"🔧 Trying JavaScript fallback for price...")
                    try:
                        price_elements = await page.evaluate('''
                            () => {
                                const priceSelectors = [
                                    '[class*="price"]',
                                    '[itemprop="price"]',
                                    'span:contains("$")',
                                    'div:contains("$")',
                                    'strong',
                                    'span'
                                ];
                                
                                const results = [];
                                for (const selector of priceSelectors) {
                                    const elements = document.querySelectorAll(selector);
                                    for (const element of elements) {
                                        if (element.textContent && element.textContent.match(/[\d,\.\$€£¥₹]/)) {
                                            results.push(element.textContent.trim());
                                        }
                                    }
                                }
                                return results.slice(0, 5); // Return top 5 candidates
                            }
                        ''')
                        
                        print(f"🔍 JavaScript found price candidates: {price_elements}")
                        for price_text in price_elements:
                            price = await self.extract_price_from_text(price_text)
                            if price and price > 0:
                                break
                    except Exception as e:
                        print(f"⚠️ JavaScript price extraction failed: {e}")
                
                # Final validation
                if not title:
                    print(f"❌ Could not extract title for {platform}")
                    return None
                
                if not price:
                    print(f"❌ Could not extract price for {platform}")
                    return None
                
                print(f"✅ Successfully scraped {platform.title()}:")
                print(f"   📝 Title: {title[:50]}...")
                print(f"   💰 Price: ${price}")
                return title, price
                
            except Exception as e:
                print(f"❌ Error scraping {platform}: {str(e)}")
                return None
            
            finally:
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
            'alibaba': {
                'name': 'Alibaba',
                'example_url': 'https://www.alibaba.com/product-detail/Example_123456789.html',
                'icon': '🏭'
            },
            'ebay': {
                'name': 'eBay',
                'example_url': 'https://www.ebay.com/itm/123456789012',
                'icon': '🏷️'
            },
            'walmart': {
                'name': 'Walmart',
                'example_url': 'https://www.walmart.com/ip/Product-Name/123456789',
                'icon': '🏪'
            },
            'flipkart': {
                'name': 'Flipkart',
                'example_url': 'https://www.flipkart.com/product-name/p/itmf3qh7nkvfbhgu',
                'icon': '🛍️'
            },
            'etsy': {
                'name': 'Etsy',
                'example_url': 'https://www.etsy.com/listing/123456789/handmade-product-name',
                'icon': '🎨'
            },
            'storenvy': {
                'name': 'Storenvy',
                'example_url': 'https://store-name.storenvy.com/products/123456-product-name',
                'icon': '🏬'
            }
        }


# Test function to verify the updated scraper with manual selectors
async def test_manual_selectors():
    """Test the scraper with manually verified selectors"""
    scraper = MultiPlatformScraper()
    
    print("Testing Multi-Platform Scraper with Manual Selectors (2024)")
    print("=" * 60)
    
    # Test URLs based on your manual inspection
    test_urls = {
        'amazon': 'https://www.amazon.com/dp/B08N5WRWNW',  # Instant Pot example
        'alibaba': 'https://www.alibaba.com/product-detail/Used-Apple-iPhone-8-64GB-Storage_1601462168694.html',
        'ebay': 'https://www.ebay.com/itm/123456789012',  # LEGO example
        'walmart': 'https://www.walmart.com/ip/test/123456',  # Toaster example
        'flipkart': 'https://www.flipkart.com/test/p/test',  # Mattress example
        'etsy': 'https://www.etsy.com/listing/123456/test',  # Sweatshirt example
    }
    
    for platform, url in test_urls.items():
        print(f"\n🔍 Testing {platform}...")
        detected = scraper.detect_platform(url)
        print(f"✅ Detected platform: {detected}")
        
        # Uncomment to test with real URLs:
        # result = await scraper.scrape_product(url)
        # if result:
        #     title, price = result
        #     print(f"✅ Success!")
        # else:
        #     print("❌ Failed to scrape")
    
    # Get platform info
    platform_info = scraper.get_platform_info()
    print(f"\n📊 Supported platforms ({len(platform_info)}):")
    for key, info in platform_info.items():
        print(f"   {info['icon']} {info['name']}")

    print(f"\n🎯 Key features of this manual selector version:")
    print(f"   • Based on actual manual inspection of each website")
    print(f"   • Removed complex platforms (Rakuten, MercadoLibre, Shopee, AliExpress)")
    print(f"   • Kept original Storenvy selectors as requested")
    print(f"   • Enhanced logging to show which selectors work")
    print(f"   • Improved price extraction with better regex patterns")
    print(f"   • Platform-specific wait times and user agents")


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_manual_selectors())