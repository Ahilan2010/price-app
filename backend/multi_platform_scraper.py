# backend/multi_platform_scraper.py - SIMPLIFIED VERSION
import asyncio
import re
import random
from typing import Optional, Tuple, Dict
from urllib.parse import urlparse
from playwright.async_api import async_playwright
import time

class MultiPlatformScraper:
    """Simplified e-commerce scraper supporting reliable platforms"""
    
    def __init__(self):
        # Platform-specific selectors (only keeping working platforms)
        self.platform_configs = {
            'amazon': {
                'domain_patterns': ['amazon.com', 'amazon.co', 'amazon.ca', 'amazon.in'],
                'title_selectors': [
                    'span#productTitle',
                    'h1#title span',
                    'h1.a-size-large span',
                    'h1[id*="title"]'
                ],
                'price_selectors': [
                    'span.a-price-whole',
                    '.a-price-whole',
                    '.a-price .a-offscreen',
                    'span[class*="a-price"]'
                ],
                'wait_time': 4000,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            },
            'ebay': {
                'domain_patterns': ['ebay.com', 'ebay.co.uk', 'ebay.ca'],
                'title_selectors': [
                    'h1[id*="x-item-title"]',
                    'h1.it-ttl',
                    'span.ux-textspans--BOLD',
                    'h1'
                ],
                'price_selectors': [
                    'span.ux-textspans',
                    'span.notranslate',
                    '.x-price-primary',
                    'span[itemprop="price"]'
                ],
                'wait_time': 3000,
                'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            },
            'etsy': {
                'domain_patterns': ['etsy.com'],
                'title_selectors': [
                    'h1[data-buy-box-listing-title="true"]',
                    'h1[data-buy-box-listing-title]',
                    'h1.wt-break-word',
                    'h1'
                ],
                'price_selectors': [
                    'p.wt-text-title-larger',
                    'p[data-buy-box-region="price"]',
                    '.wt-text-title-larger',
                    'p[class*="price"]'
                ],
                'wait_time': 2500,
                'user_agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0'
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
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        return random.choice(user_agents)
    
    async def human_like_behavior(self, page):
        """Simulate human-like behavior on the page"""
        try:
            # Random mouse movements
            for _ in range(random.randint(1, 3)):
                x = random.randint(100, 800)
                y = random.randint(100, 600)
                await page.mouse.move(x, y)
                await asyncio.sleep(random.uniform(0.1, 0.2))
            
            # Random scroll
            await page.evaluate(f"window.scrollBy(0, {random.randint(100, 300)})")
            await asyncio.sleep(random.uniform(0.3, 0.8))
        except Exception as e:
            print(f"⚠️ Human behavior simulation failed: {e}")
    
    async def extract_with_fallbacks(self, page, selectors: list) -> Optional[str]:
        """Extract content using multiple selector fallbacks"""
        for i, selector in enumerate(selectors):
            try:
                element = await page.wait_for_selector(selector, timeout=3000)
                if element:
                    content = await element.text_content()
                    if content and len(content.strip()) > 0:
                        print(f"✅ Found content with selector #{i+1}: {selector}")
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
        cleaned_text = re.sub(r'[^\d.,\-\s]', '', price_text)
        print(f"🧹 Cleaned text: '{cleaned_text}'")
        
        # Find price patterns
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
        """Enhanced scrape product with better error handling"""
        platform = self.detect_platform(url)
        
        if not platform:
            print(f"❌ Unsupported platform for URL: {url}")
            return None
        
        config = self.platform_configs[platform]
        
        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--disable-web-security',
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-gpu',
                        '--user-agent=' + config.get('user_agent', self.get_random_user_agent())
                    ]
                )
                
                context = await browser.new_context(
                    viewport={'width': 1366, 'height': 768},
                    locale='en-US'
                )
                
                page = await context.new_page()
                
                print(f"🔍 Scraping {platform.title()} product: {url[:60]}...")
                
                # Navigate to the URL with longer timeout
                await page.goto(url, wait_until='domcontentloaded', timeout=45000)
                
                # Wait for the page to load
                print(f"⏳ Waiting {config['wait_time']}ms for {platform} to load...")
                await page.wait_for_timeout(config['wait_time'])
                
                # Simulate human behavior
                await self.human_like_behavior(page)
                
                # Extract title
                print(f"📝 Extracting title for {platform}...")
                title = await self.extract_with_fallbacks(page, config['title_selectors'])
                
                if not title:
                    # JavaScript fallback for title
                    print(f"🔧 Trying JavaScript fallback for title...")
                    title = await page.evaluate('''
                        () => {
                            const titleElement = document.querySelector('h1') || 
                                                document.querySelector('[class*="title"]');
                            return titleElement ? titleElement.textContent.trim() : document.title.split(' - ')[0];
                        }
                    ''')
                
                # Extract price
                print(f"💰 Extracting price for {platform}...")
                price = None
                for i, selector in enumerate(config['price_selectors']):
                    try:
                        element = await page.wait_for_selector(selector, timeout=3000)
                        if element:
                            price_text = await element.text_content()
                            print(f"📄 Price text from selector #{i+1}: '{price_text}'")
                            price = await self.extract_price_from_text(price_text)
                            if price and price > 0:
                                break
                    except Exception as e:
                        print(f"⚠️ Price selector #{i+1} failed: {e}")
                        continue
                
                # JavaScript fallback for price
                if not price:
                    print(f"🔧 Trying JavaScript fallback for price...")
                    try:
                        price_elements = await page.evaluate('''
                            () => {
                                const priceSelectors = [
                                    '[class*="price"]',
                                    '[itemprop="price"]',
                                    'span',
                                    'div'
                                ];
                                
                                const results = [];
                                for (const selector of priceSelectors) {
                                    const elements = document.querySelectorAll(selector);
                                    for (const element of elements) {
                                        const text = element.textContent.trim();
                                        if (text && text.match(/[\d,\.\$€£¥₹]/)) {
                                            results.push(text);
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
            'storenvy': {
                'name': 'Storenvy',
                'example_url': 'https://store-name.storenvy.com/products/123456-product-name',
                'icon': '🏬'
            }
        }


# Test function
async def test_simplified_scraper():
    """Test function to verify the simplified scraper works"""
    scraper = MultiPlatformScraper()
    
    print("Testing Simplified Multi-Platform Scraper")
    print("=" * 50)
    
    # Get platform info
    platform_info = scraper.get_platform_info()
    print(f"\n📊 Supported platforms ({len(platform_info)}):")
    for key, info in platform_info.items():
        print(f"   {info['icon']} {info['name']}")
    
    print(f"\n🎯 Simplified version features:")
    print(f"   • Only reliable platforms (Amazon, eBay, Etsy, Storenvy)")
    print(f"   • Better error handling and timeouts")
    print(f"   • More human-like behavior simulation")
    print(f"   • Improved price extraction")

if __name__ == "__main__":
    asyncio.run(test_simplified_scraper())