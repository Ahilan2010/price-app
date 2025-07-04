# backend/multi_platform_scraper.py
import asyncio
import re
import random
from typing import Optional, Tuple, Dict
from urllib.parse import urlparse
from playwright.async_api import async_playwright
import time

class MultiPlatformScraper:
    """Universal e-commerce scraper supporting multiple platforms"""
    
    def __init__(self):
        # Platform-specific selectors and configurations
        self.platform_configs = {
            'amazon': {
                'domain_patterns': ['amazon.com', 'amazon.co', 'amazon.ca', 'amazon.in'],
                'title_selectors': [
                    'span#productTitle',
                    'h1#title span',
                    'h1.a-size-large',
                    '[data-automation-id="productTitle"]',
                    '.product-title-word-break'
                ],
                'price_selectors': [
                    'span.a-price-whole',
                    'span.a-price.a-text-price.a-size-medium.apexPriceToPay',
                    'span.a-price-range',
                    '.a-price.a-text-price.header-price',
                    'span.a-price.reinventPricePriceToPayPadding',
                    '[data-a-size="xl"] .a-price-whole',
                    '.a-price-whole'
                ],
                'wait_time': 3000,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            },
            'alibaba': {
                'domain_patterns': ['alibaba.com'],
                'title_selectors': [
                    'h1.module-pdp-title',
                    '.product-title',
                    'h1[class*="title"]',
                    '.detail-title',
                    '.product-name'
                ],
                'price_selectors': [
                    '.price-main',
                    '.price-now',
                    'span[class*="price"]',
                    '.trade-price',
                    '.price-value'
                ],
                'wait_time': 4000,
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            },
            'ebay': {
                'domain_patterns': ['ebay.com', 'ebay.co.uk', 'ebay.ca'],
                'title_selectors': [
                    'h1.it-ttl',
                    'h1.vi-is1-titleH1',
                    '.x-item-title__mainTitle',
                    'h1[class*="title"]',
                    '.it-ttl'
                ],
                'price_selectors': [
                    'span.notranslate',
                    '.x-price-primary',
                    'span[itemprop="price"]',
                    '.vi-VR-cvipPrice',
                    '.x-bin-price__value'
                ],
                'wait_time': 2500,
                'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            },
            'walmart': {
                'domain_patterns': ['walmart.com'],
                'title_selectors': [
                    'h1[itemprop="name"]',
                    'h1.prod-ProductTitle',
                    'h1.f3.b.lh-copy',
                    'h1[data-automation-id="productName"]',
                    '.prod-productTitle-buyBox'
                ],
                'price_selectors': [
                    'span[itemprop="price"]',
                    '.price-characteristic',
                    'span.price-now',
                    '[data-automation-id="productPrice"]',
                    '.price-group'
                ],
                'wait_time': 3500,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0'
            },
            'rakuten': {
                'domain_patterns': ['rakuten.com', 'rakuten.co.jp'],
                'title_selectors': [
                    'h1.product-name',
                    'h1[itemprop="name"]',
                    '.item-name',
                    'h1.b-h1-3',
                    '.product-title'
                ],
                'price_selectors': [
                    '.price-current',
                    'span[itemprop="price"]',
                    '.item-price',
                    '.product-price',
                    '.price-value'
                ],
                'wait_time': 3000,
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15'
            },
            'flipkart': {
                'domain_patterns': ['flipkart.com'],
                'title_selectors': [
                    'h1.yhB1nd',
                    'span.B_NuCI',
                    'h1[class*="title"]',
                    '.product-title',
                    'h1._9E25nV'
                ],
                'price_selectors': [
                    'div._30jeq3',
                    'div._16Jk6d',
                    'div[class*="price"]',
                    '._1vC4OE',
                    '.CEmiEU'
                ],
                'wait_time': 3500,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            'etsy': {
                'domain_patterns': ['etsy.com'],
                'title_selectors': [
                    'h1[data-buy-box-listing-title]',
                    'h1.wt-text-body-01',
                    'h1[class*="listing-title"]',
                    '.listing-page-title-component h1',
                    'h1.wt-break-word'
                ],
                'price_selectors': [
                    'p[data-buy-box-region="price"] .wt-text-title-larger',
                    '.wt-text-title-larger[data-selector="price"]',
                    'span.currency-value',
                    '[data-buy-box-region="price"]',
                    '.wt-mr-xs-1'
                ],
                'wait_time': 2500,
                'user_agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101'
            },
            'mercadolibre': {
                'domain_patterns': ['mercadolibre.com', 'mercadolivre.com'],
                'title_selectors': [
                    'h1.ui-pdp-title',
                    '.ui-pdp-header__title-container h1',
                    'h1[class*="title"]',
                    '.item-title__primary',
                    '.vip-title-main'
                ],
                'price_selectors': [
                    'span.andes-money-amount__fraction',
                    '.ui-pdp-price__second-line .price-tag-fraction',
                    'span[itemprop="price"]',
                    '.price-tag-amount',
                    '.price-tag'
                ],
                'wait_time': 3000,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0'
            },
            'shopee': {
                'domain_patterns': ['shopee.com', 'shopee.sg', 'shopee.my', 'shopee.ph'],
                'title_selectors': [
                    'div[data-sqe="name"]',
                    '.qaNIZv',
                    'h1._3ZV7fL',
                    '.product-name',
                    'div._2rQP1z'
                ],
                'price_selectors': [
                    'div[data-sqe="current-price"]',
                    '.pqTWkA',
                    'div._3n5NQx',
                    '.product-price',
                    'div.tyOBoQ'
                ],
                'wait_time': 4000,
                'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15'
            },
            'aliexpress': {
                'domain_patterns': ['aliexpress.com', 'aliexpress.us'],
                'title_selectors': [
                    'h1[data-pl="product-title"]',
                    'h1.product-title-text',
                    '.product-title',
                    'h1._1Cjt3',
                    '.hM5MHf'
                ],
                'price_selectors': [
                    'span.product-price-value',
                    '.uniform-banner-box-price',
                    'span[data-pl="product-price"]',
                    '.snow-price_SkuPrice__1et7f',
                    '.es--wrap--erdmPRe'
                ],
                'wait_time': 4500,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            'storenvy': {
                'domain_patterns': ['storenvy.com'],
                'title_selectors': [
                    'h1.product-name',
                    'h1.product_name',
                    'h1[itemprop="name"]',
                    '.product-header h1',
                    '.product_name',
                    'h1'
                ],
                'price_selectors': [
                    'div.price.vprice[itemprop="price"]',
                    'div.price.vprice',
                    'div[itemprop="price"]',
                    '.price.vprice',
                    'span.product-price',
                    '.product-price',
                    'span.price:not(.sale-price):not(.discount-price)'
                ],
                'wait_time': 3000,
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
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
        # Random mouse movements
        for _ in range(random.randint(2, 4)):
            x = random.randint(100, 800)
            y = random.randint(100, 600)
            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.1, 0.3))
        
        # Random scroll
        await page.evaluate(f"window.scrollBy(0, {random.randint(100, 300)})")
        await asyncio.sleep(random.uniform(0.5, 1.0))
    
    async def scrape_product(self, url: str) -> Optional[Tuple[str, float]]:
        """Scrape product title and price from any supported platform"""
        platform = self.detect_platform(url)
        
        if not platform:
            print(f"Unsupported platform for URL: {url}")
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
                    '--disable-gpu'
                ]
            )
            
            # Create context with random viewport and user agent
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
                    'Upgrade-Insecure-Requests': '1'
                }
            )
            
            # Add cookies to appear more legitimate
            await context.add_cookies([
                {"name": "session_id", "value": str(random.randint(1000000, 9999999)), "domain": f".{platform}.com", "path": "/"}
            ])
            
            page = await context.new_page()
            
            # Randomize navigation
            await page.set_extra_http_headers({
                'Referer': f'https://www.google.com/search?q={platform}+shopping'
            })
            
            try:
                # Add random delay before navigation
                await asyncio.sleep(random.uniform(0.5, 2.0))
                
                # Navigate to the URL
                await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                
                # Wait for the page to load with platform-specific wait time
                await page.wait_for_timeout(config['wait_time'])
                
                # Simulate human behavior
                await self.human_like_behavior(page)
                
                # Extract title
                title = "Unknown Product"
                for selector in config['title_selectors']:
                    try:
                        element = await page.wait_for_selector(selector, timeout=5000)
                        if element:
                            title_text = await element.text_content()
                            if title_text and len(title_text.strip()) > 0:
                                title = title_text.strip()
                                print(f"Found title for {platform}: {title[:50]}...")
                                break
                    except Exception:
                        continue
                
                # Extract price
                price = None
                for selector in config['price_selectors']:
                    try:
                        element = await page.wait_for_selector(selector, timeout=5000)
                        if element:
                            price_text = await element.text_content()
                            if price_text:
                                # Clean price text
                                price_text = price_text.strip()
                                # Remove currency symbols and extract number
                                price_text = re.sub(r'[^\d.,]', '', price_text)
                                price_text = price_text.replace(',', '')
                                
                                # Find the first valid number
                                price_match = re.search(r'(\d+(?:\.\d{1,2})?)', price_text)
                                if price_match:
                                    price = float(price_match.group(1))
                                    if price > 0:
                                        print(f"Found price for {platform}: ${price}")
                                        break
                    except Exception:
                        continue
                
                # Special handling for certain platforms
                if platform == 'amazon' and price is None:
                    # Try JavaScript evaluation for dynamic prices
                    try:
                        price_text = await page.evaluate('''
                            () => {
                                const priceElement = document.querySelector('.a-price-whole') || 
                                                   document.querySelector('.a-price-range') ||
                                                   document.querySelector('[data-a-size="xl"] .a-price');
                                return priceElement ? priceElement.textContent : null;
                            }
                        ''')
                        if price_text:
                            price_match = re.search(r'(\d+(?:\.\d{1,2})?)', price_text.replace(',', ''))
                            if price_match:
                                price = float(price_match.group(1))
                    except Exception:
                        pass
                
                if price is None:
                    print(f"Could not extract price for {platform}")
                    return None
                
                # Add final random delay
                await asyncio.sleep(random.uniform(1.0, 3.0))
                
                return title, price
                
            except Exception as e:
                print(f"Error scraping {platform}: {str(e)}")
                return None
            
            finally:
                await browser.close()
    
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
                'example_url': 'https://www.alibaba.com/product-detail/...',
                'icon': '🏭'
            },
            'ebay': {
                'name': 'eBay',
                'example_url': 'https://www.ebay.com/itm/123456789',
                'icon': '🏷️'
            },
            'walmart': {
                'name': 'Walmart',
                'example_url': 'https://www.walmart.com/ip/Product-Name/123456789',
                'icon': '🏪'
            },
            'rakuten': {
                'name': 'Rakuten',
                'example_url': 'https://www.rakuten.com/shop/store/product/...',
                'icon': '🎌'
            },
            'flipkart': {
                'name': 'Flipkart',
                'example_url': 'https://www.flipkart.com/product-name/p/itm...',
                'icon': '🛍️'
            },
            'etsy': {
                'name': 'Etsy',
                'example_url': 'https://www.etsy.com/listing/123456789/...',
                'icon': '🎨'
            },
            'mercadolibre': {
                'name': 'MercadoLibre',
                'example_url': 'https://www.mercadolibre.com/product-MLM-123456789',
                'icon': '🌎'
            },
            'shopee': {
                'name': 'Shopee',
                'example_url': 'https://shopee.com/product-i.123456.789012',
                'icon': '🛒'
            },
            'aliexpress': {
                'name': 'AliExpress',
                'example_url': 'https://www.aliexpress.com/item/123456789.html',
                'icon': '🌏'
            },
            'storenvy': {
                'name': 'Storenvy',
                'example_url': 'https://www.storenvy.com/products/123456-product-name',
                'icon': '🏬'
            }
        }


# Test function
async def test_scraper():
    """Test the multi-platform scraper"""
    scraper = MultiPlatformScraper()
    
    # Test URLs for different platforms
    test_urls = {
        'amazon': 'https://www.amazon.com/dp/B08N5WRWNW',
        'ebay': 'https://www.ebay.com/itm/123456789',
        'walmart': 'https://www.walmart.com/ip/test/123456',
        'etsy': 'https://www.etsy.com/listing/123456/test',
        'storenvy': 'https://www.storenvy.com/products/123456-test'
    }
    
    for platform, url in test_urls.items():
        print(f"\nTesting {platform}...")
        detected = scraper.detect_platform(url)
        print(f"Detected platform: {detected}")
        
        # Note: Actual scraping would require real URLs
        # This is just to test platform detection
    
    # Get platform info
    platform_info = MultiPlatformScraper.get_platform_info()
    print("\nSupported platforms:")
    for key, info in platform_info.items():
        print(f"{info['icon']} {info['name']}: {info['example_url']}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_scraper())