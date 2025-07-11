# backend/multi_platform_scraper.py - CLEAN VERSION
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
    """Multi-platform e-commerce scraper with proper error handling"""
    
    def __init__(self):
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
                'wait_time': 5000,
                'user_agents': [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
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
                    'p.wt-text-title-larger.wt-mr-xs-1',
                    'p.wt-text-title-larger span.currency-value',
                    'p[data-testid="lp-price"] span.currency-value',
                    'p[data-test-id="lp-price"] span.currency-value',
                    'span[data-testid="currency-value"]',
                    'span.currency-value',
                    'p.wt-text-title-larger'
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
                    'div.item-details-name-row h1',
                    'h1[data-testid="item-name"]',
                    'h1.item-name-container h1',
                    'h1.font-header-1',
                    '.item-name-container h1',
                    '.item-details-name h1',
                    'h1'
                ],
                'price_selectors': [
                    'span[data-testid="price-label"]',
                    'span.text-robux',
                    'span.robux',
                    'span[class*="robux"]',
                    '.price-robux',
                    'span.icon-robux + span',
                    'div[class*="price"] span',
                    'span[class*="Price"]'
                ],
                'wait_time': 5000,
                'user_agents': [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ],
                'currency': 'robux'
            },
            'flights': {
                'domain_patterns': ['kayak.com', 'booking.com', 'priceline.com', 'momondo.com'],
                'title_selectors': [
                    '.flight-info h3',
                    '.itinerary-title',
                    '.trip-summary',
                    'h1.flight-header',
                    'h2.flight-details',
                    '.flight-route',
                    '[data-testid="flight-summary"]'
                ],
                'price_selectors': [
                    'div.e2GB-price-text',
                    'div.FlightCardPrice-module__priceContainer___nXXv2',
                    'div.Text-sc-1xtb652-0.koHeTu',
                    'div.e2GB-price-text',
                    'span[data-testid="price"]',
                    '.price-text',
                    '.flight-price',
                    'span.price',
                    '.fare-price',
                    'div[class*="price"] span',
                    '.total-price',
                    '[data-testid="flight-price"]'
                ],
                'wait_time': 6000,
                'user_agents': [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                ]
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
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ])
        return random.choice(user_agents)
    
    async def setup_browser_page(self, browser, platform: str):
        """Set up browser page with stealth configuration"""
        try:
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
                    'Upgrade-Insecure-Requests': '1'
                }
            )
            
            page = await context.new_page()
            
            # Add stealth script
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
            """)
            
            return page
        except Exception as e:
            print(f"Error setting up browser page: {e}")
            raise
    
    async def simulate_human_behavior(self, page):
        """Simulate human-like behavior"""
        try:
            # Random wait
            await asyncio.sleep(random.uniform(1, 3))
            
            # Random mouse movements
            for _ in range(random.randint(2, 4)):
                x = random.randint(100, 1200)
                y = random.randint(100, 800)
                await page.mouse.move(x, y)
                await asyncio.sleep(random.uniform(0.1, 0.3))
            
            # Random scrolling
            scroll_positions = [200, 400, 600, 300, 100]
            for position in scroll_positions[:random.randint(2, 4)]:
                await page.evaluate(f"window.scrollTo({{top: {position}, behavior: 'smooth'}})")
                await asyncio.sleep(random.uniform(0.5, 1.2))
        except Exception as e:
            print(f"Error simulating human behavior: {e}")
    
    async def extract_text_content(self, page, selectors: List[str]) -> Optional[str]:
        """Extract text content using multiple selectors"""
        for i, selector in enumerate(selectors):
            try:
                element = await page.wait_for_selector(selector, timeout=3000)
                if element:
                    text = await element.text_content()
                    if text and text.strip():
                        print(f"Found content with selector #{i+1}: {selector}")
                        return text.strip()
            except Exception:
                continue
        return None
    
    async def extract_price_from_text(self, price_text: str) -> Optional[float]:
        """Extract price from text with improved regex"""
        if not price_text:
            return None
        
        try:
            print(f"Extracting price from: '{price_text[:100]}'")
            
            # Clean the text
            cleaned_text = re.sub(r'[^\d.,\-\s$€£¥₹]', ' ', price_text)
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
            
            # Price patterns (order matters)
            patterns = [
                r'US\s*\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)',
                r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)',
                r'(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)\s*\$',
                r'(\d{1,3}(?:,\d{3})*\.\d{2})',
                r'(\d{1,3}(?:,\d{3})*)',
                r'(\d+\.\d{2})',
                r'(\d+)',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, cleaned_text)
                if matches:
                    for match in matches:
                        try:
                            price_str = match.replace(',', '').strip()
                            price = float(price_str)
                            if 0.01 <= price <= 999999:
                                print(f"Extracted price: ${price:.2f}")
                                return price
                        except (ValueError, TypeError):
                            continue
            
            print(f"Could not extract price from: '{price_text[:100]}'")
            return None
        except Exception as e:
            print(f"Error extracting price: {e}")
            return None
    
    async def extract_robux_from_text(self, price_text: str) -> Optional[float]:
        """Extract Robux price from text"""
        if not price_text:
            return None
        
        try:
            print(f"Extracting Robux from: '{price_text[:100]}'")
            
            # Clean the text
            cleaned_text = re.sub(r'[^\d,.\-\s]', ' ', price_text)
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
            
            # Robux patterns
            patterns = [
                r'(\d{1,3}(?:,\d{3})*)',
                r'(\d+)',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, cleaned_text)
                if matches:
                    for match in matches:
                        try:
                            price_str = match.replace(',', '').strip()
                            price = float(price_str)
                            if 1 <= price <= 999999:
                                print(f"Extracted Robux: {price:.0f}")
                                return price
                        except (ValueError, TypeError):
                            continue
            
            print(f"Could not extract Robux from: '{price_text[:100]}'")
            return None
        except Exception as e:
            print(f"Error extracting Robux: {e}")
            return None
    
    async def extract_roblox_info(self, page) -> Optional[Tuple[str, float]]:
        """Extract Roblox item name and price"""
        try:
            print("Extracting Roblox UGC item info...")
            await page.wait_for_timeout(5000)
            
            # Extract name
            name_selectors = [
                'div.item-details-name-row h1',
                'h1[data-testid="item-name"]',
                'h1.item-name-container h1',
                'h1.font-header-1',
                'h1'
            ]
            
            item_name = await self.extract_text_content(page, name_selectors)
            
            if not item_name:
                # JavaScript fallback for name
                item_name = await page.evaluate('''
                    () => {
                        const nameRow = document.querySelector('.item-details-name-row h1');
                        if (nameRow && nameRow.textContent.trim()) {
                            return nameRow.textContent.trim();
                        }
                        
                        const selectors = ['h1[data-testid="item-name"]', '.item-name-container h1', 'h1'];
                        for (const sel of selectors) {
                            const element = document.querySelector(sel);
                            if (element && element.textContent.trim()) {
                                return element.textContent.trim();
                            }
                        }
                        return null;
                    }
                ''')
            
            # Extract price
            price_selectors = [
                'span[data-testid="price-label"]',
                'span.text-robux',
                'span.robux',
                'span[class*="robux"]',
                '.price-robux',
                'div[class*="price"] span'
            ]
            
            price = None
            for selector in price_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        price_text = await element.text_content()
                        if price_text and ('robux' in price_text.lower() or price_text.strip().isdigit()):
                            price = await self.extract_robux_from_text(price_text)
                            if price and price > 0:
                                break
                    if price and price > 0:
                        break
                except Exception:
                    continue
            
            if item_name and price:
                print(f"Successfully extracted Roblox item: {item_name} - {price:.0f} Robux")
                return item_name, price
            
            return None
        except Exception as e:
            print(f"Error extracting Roblox info: {e}")
            return None
    
    def parse_flight_route_from_url(self, url: str) -> str:
        """Parse flight route and dates from URL to create meaningful title"""
        try:
            # Detect which flight site and parse accordingly
            if 'kayak.com' in url:
                match = re.search(r'/flights/([A-Z]{3})-([A-Z]{3})/(\d{4}-\d{2}-\d{2})/(\d{4}-\d{2}-\d{2})', url)
                if match:
                    from_code, to_code, dep_date, ret_date = match.groups()
                    return f"Kayak: {from_code} → {to_code} ({dep_date} to {ret_date})"