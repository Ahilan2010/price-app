# backend/multi_platform_scraper.py - FIXED VERSION WITH NO ERRORS
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
                    # Kayak specific
                    'div.e2GB-price-text',
                    # Booking.com specific  
                    'div.FlightCardPrice-module__priceContainer___nXXv2',
                    # Priceline specific
                    'div.Text-sc-1xtb652-0.koHeTu',
                    # Momondo specific
                    'div.e2GB-price-text',
                    # General fallbacks
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
                r'US\s*\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)',  # US $135.00
                r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)',       # $1,234.56
                r'(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)\s*\$',       # 1,234.56$
                r'(\d{1,3}(?:,\d{3})*\.\d{2})',                   # 1,234.56
                r'(\d{1,3}(?:,\d{3})*)',                          # 1,234
                r'(\d+\.\d{2})',                                  # 123.45
                r'(\d+)',                                         # 123
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
                r'(\d{1,3}(?:,\d{3})*)',  # 1,000 format
                r'(\d+)',                 # Simple digits
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
                # Kayak format: /flights/HOU-CFU/2025-07-11/2025-07-14
                match = re.search(r'/flights/([A-Z]{3})-([A-Z]{3})/(\d{4}-\d{2}-\d{2})/(\d{4}-\d{2}-\d{2})', url)
                if match:
                    from_code, to_code, dep_date, ret_date = match.groups()
                    return f"Kayak: {from_code} → {to_code} ({dep_date} to {ret_date})"
                
                # One way format: /flights/HOU-CFU/2025-07-11
                match = re.search(r'/flights/([A-Z]{3})-([A-Z]{3})/(\d{4}-\d{2}-\d{2})', url)
                if match:
                    from_code, to_code, dep_date = match.groups()
                    return f"Kayak: {from_code} → {to_code} ({dep_date})"
            
            elif 'booking.com' in url:
                # Booking.com format: from=HOU&to=CFU&depart=2025-07-11&return=2025-07-14
                from_match = re.search(r'from=([A-Z]{3})', url)
                to_match = re.search(r'to=([A-Z]{3})', url)
                dep_match = re.search(r'depart=(\d{4}-\d{2}-\d{2})', url)
                ret_match = re.search(r'return=(\d{4}-\d{2}-\d{2})', url)
                
                if from_match and to_match and dep_match:
                    from_code = from_match.group(1)
                    to_code = to_match.group(1)
                    dep_date = dep_match.group(1)
                    
                    if ret_match:
                        ret_date = ret_match.group(1)
                        return f"Booking.com: {from_code} → {to_code} ({dep_date} to {ret_date})"
                    else:
                        return f"Booking.com: {from_code} → {to_code} ({dep_date})"
            
            elif 'priceline.com' in url:
                # Priceline format: /flights/search/HOU-CFU/2025-07-11/2025-07-14
                match = re.search(r'/flights/search/([A-Z]{3})-([A-Z]{3})/(\d{4}-\d{2}-\d{2})/(\d{4}-\d{2}-\d{2})', url)
                if match:
                    from_code, to_code, dep_date, ret_date = match.groups()
                    return f"Priceline: {from_code} → {to_code} ({dep_date} to {ret_date})"
                
                # One way format
                match = re.search(r'/flights/search/([A-Z]{3})-([A-Z]{3})/(\d{4}-\d{2}-\d{2})', url)
                if match:
                    from_code, to_code, dep_date = match.groups()
                    return f"Priceline: {from_code} → {to_code} ({dep_date})"
            
            elif 'momondo.com' in url:
                # Momondo format: /flight-search/HOU-CFU/2025-07-11/2025-07-14
                match = re.search(r'/flight-search/([A-Z]{3})-([A-Z]{3})/(\d{4}-\d{2}-\d{2})/(\d{4}-\d{2}-\d{2})', url)
                if match:
                    from_code, to_code, dep_date, ret_date = match.groups()
                    return f"Momondo: {from_code} → {to_code} ({dep_date} to {ret_date})"
                
                # One way format
                match = re.search(r'/flight-search/([A-Z]{3})-([A-Z]{3})/(\d{4}-\d{2}-\d{2})', url)
                if match:
                    from_code, to_code, dep_date = match.groups()
                    return f"Momondo: {from_code} → {to_code} ({dep_date})"
            
            # Generic fallback - try to extract any airport codes and dates
            airport_match = re.search(r'([A-Z]{3})-([A-Z]{3})', url)
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', url)
            
            if airport_match:
                from_code, to_code = airport_match.groups()
                if date_match:
                    dep_date = date_match.group(1)
                    return f"Flight: {from_code} → {to_code} ({dep_date})"
                else:
                    return f"Flight: {from_code} → {to_code}"
            
            # Last resort - use domain name
            domain = urlparse(url).netloc.replace('www.', '').replace('.com', '').title()
            return f"{domain} Flight Search"
            
        except Exception as e:
            print(f"Error parsing flight route from URL: {e}")
            return "Flight Search Result"
        """Extract flight information and price"""
        try:
            print("Extracting flight information...")
            await page.wait_for_timeout(6000)
            
            # Extract title
            title_selectors = [
                '.flight-info h3',
                '.itinerary-title',
                '.trip-summary',
                'h1.flight-header',
                'h2.flight-details',
                'h1', 'h2'
            ]
            
            flight_title = await self.extract_text_content(page, title_selectors)
            
            if not flight_title:
                flight_title = await page.evaluate('''
                    () => {
                        return document.title || 'Flight Search Result';
                    }
                ''')
            
            # Extract price
            price_selectors = [
                'span[data-testid="price"]',
                '.price-text',
                '.flight-price',
                'span.price',
                '.fare-price',
                'div[class*="price"] span',
                '.total-price'
            ]
            
            price = None
            for selector in price_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        price_text = await element.text_content()
                        if price_text and '$' in price_text:
                            price = await self.extract_price_from_text(price_text)
                            if price and price > 0:
                                break
                    if price and price > 0:
                        break
                except Exception:
                    continue
            
            if flight_title and price:
                print(f"Successfully extracted flight: {flight_title} - ${price:.2f}")
                return flight_title, price
            
            return None
        except Exception as e:
            print(f"Error extracting flight info: {e}")
            return None
    
    async def extract_etsy_price(self, page) -> Optional[float]:
        """Enhanced Etsy price extraction with menu detection"""
        try:
            print("Extracting Etsy price with menu detection...")
            
            # Wait longer for Etsy to fully load
            await page.wait_for_timeout(5000)
            
            # Scroll to the main product area to avoid menu items
            try:
                await page.evaluate('''
                    () => {
                        // Scroll to the main product section
                        const productSection = document.querySelector('[data-test-id="listing-page-title"]') ||
                                             document.querySelector('h1[data-testid="listing-page-title"]') ||
                                             document.querySelector('h1');
                        if (productSection) {
                            productSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        }
                    }
                ''')
                await page.wait_for_timeout(2000)
            except Exception:
                pass
            
            # Enhanced selectors with priority for main product price
            enhanced_selectors = [
                # Main product price (avoiding menu items)
                'p.wt-text-title-larger.wt-mr-xs-1',  # Target the specific class
                'div[data-test-id="listing-page-cart"] p.wt-text-title-larger',
                'div[data-testid="listing-page-cart"] p.wt-text-title-larger',
                'section[data-test-id="shop-section"] p.wt-text-title-larger',
                
                # Fallback selectors
                'p[data-testid="lp-price"] span.currency-value',
                'p[data-test-id="lp-price"] span.currency-value',
                'span[data-testid="currency-value"]',
                'p.wt-text-title-larger span.currency-value',
                'span.currency-value',
                'p.wt-text-title-larger'
            ]
            
            for i, selector in enumerate(enhanced_selectors):
                try:
                    elements = await page.query_selector_all(selector)
                    
                    for element in elements:
                        # Check if this element is in the main product area, not a menu
                        is_main_product = await page.evaluate('''
                            (element) => {
                                // Check if element is within main product area
                                const rect = element.getBoundingClientRect();
                                
                                // Skip elements that are too high up (likely menu items)
                                if (rect.top < 300) {
                                    return false;
                                }
                                
                                // Check if element is in a menu or navigation area
                                let parent = element.parentElement;
                                while (parent) {
                                    const className = parent.className || '';
                                    const id = parent.id || '';
                                    
                                    // Skip if in menu, navigation, or related products
                                    if (className.includes('menu') || 
                                        className.includes('nav') ||
                                        className.includes('related') ||
                                        className.includes('recommendation') ||
                                        id.includes('menu') ||
                                        id.includes('nav')) {
                                        return false;
                                    }
                                    parent = parent.parentElement;
                                }
                                
                                return true;
                            }
                        ''', element)
                        
                        if is_main_product:
                            price_text = await element.text_content()
                            if price_text:
                                print(f"Etsy main product price from selector #{i+1}: '{price_text}'")
                                price = await self.extract_price_from_text(price_text)
                                if price and price >= 1.0:  # Reasonable minimum for main products
                                    print(f"Validated Etsy main product price: ${price:.2f}")
                                    return price
                                
                except Exception as e:
                    print(f"Etsy selector #{i+1} failed ({selector}): {str(e)[:50]}")
                    continue
            
            # JavaScript fallback specifically for main product
            print("Trying Etsy JavaScript fallback for main product price...")
            try:
                main_price = await page.evaluate('''
                    () => {
                        // Look for the main product price, avoiding menu items
                        const priceSelectors = [
                            'p.wt-text-title-larger.wt-mr-xs-1',
                            'div[data-test-id="listing-page-cart"] p.wt-text-title-larger',
                            'div[data-testid="listing-page-cart"] p.wt-text-title-larger'
                        ];
                        
                        for (const selector of priceSelectors) {
                            const element = document.querySelector(selector);
                            if (element) {
                                const rect = element.getBoundingClientRect();
                                // Make sure it's not in the top menu area
                                if (rect.top > 300) {
                                    return element.textContent.trim();
                                }
                            }
                        }
                        
                        // Last resort: find all price elements and pick the most reasonable one
                        const allPrices = document.querySelectorAll('p.wt-text-title-larger, span.currency-value');
                        const prices = [];
                        
                        for (const el of allPrices) {
                            const text = el.textContent || '';
                            const rect = el.getBoundingClientRect();
                            
                            // Skip elements too high up (menu area)
                            if (rect.top < 300) continue;
                            
                            // Extract price
                            const match = text.match(/\\$([\\d,]+\\.?\\d*)/);
                            if (match) {
                                const price = parseFloat(match[1].replace(',', ''));
                                if (price >= 1.0) {  // Reasonable minimum
                                    prices.push({ price, text, element: el });
                                }
                            }
                        }
                        
                        // Return the first reasonable price found in main content area
                        if (prices.length > 0) {
                            // Sort by price (higher prices are more likely to be main products)
                            prices.sort((a, b) => b.price - a.price);
                            return prices[0].text;
                        }
                        
                        return null;
                    }
                ''')
                
                if main_price:
                    print(f"Etsy JavaScript found main product price: '{main_price}'")
                    price = await self.extract_price_from_text(main_price)
                    if price and price > 0:
                        return price
                        
            except Exception as e:
                print(f"Etsy JavaScript fallback failed: {e}")
            
            print("Etsy main product price extraction failed")
            return None
            
        except Exception as e:
            print(f"Error extracting Etsy price: {e}")
            return None
    
    async def extract_standard_product(self, page, platform: str, config: dict) -> Optional[Tuple[str, float]]:
        """Extract standard product information"""
        try:
            # Extract title
            title = await self.extract_text_content(page, config['title_selectors'])
            
            if not title:
                title = await page.evaluate('''
                    () => {
                        const selectors = ['h1', '[data-testid*="title"]', '[class*="title"]'];
                        for (const sel of selectors) {
                            const element = document.querySelector(sel);
                            if (element && element.textContent.trim()) {
                                return element.textContent.trim();
                            }
                        }
                        return document.title.split(' - ')[0] || document.title;
                    }
                ''')
            
            # Extract price
            price = None
            for selector in config['price_selectors']:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        price_text = await element.text_content()
                        if price_text:
                            price = await self.extract_price_from_text(price_text)
                            if price and price > 0:
                                break
                    if price and price > 0:
                        break
                except Exception:
                    continue
            
            if title and price:
                # Limit title length
                title = title[:200] if len(title) > 200 else title
                print(f"Successfully extracted {platform}: {title[:50]}... - ${price:.2f}")
                return title, price
            
            return None
        except Exception as e:
            print(f"Error extracting standard product: {e}")
            return None
    
    async def scrape_product(self, url: str) -> Optional[Tuple[str, float]]:
        """Main scraping function"""
        platform = self.detect_platform(url)
        
        if not platform:
            print(f"Unsupported platform for URL: {url}")
            return None
        
        config = self.platform_configs[platform]
        
        async with async_playwright() as p:
            browser = None
            try:
                # Launch browser
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-gpu'
                    ]
                )
                
                page = await self.setup_browser_page(browser, platform)
                
                print(f"Scraping {platform.title()}: {url[:60]}...")
                
                # Navigate to page
                await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                
                # Wait for page to load
                await page.wait_for_timeout(config['wait_time'])
                
                # Simulate human behavior
                await self.simulate_human_behavior(page)
                
                # Extract based on platform
                if platform == 'roblox':
                    return await self.extract_roblox_info(page)
                elif platform == 'flights':
                    return await self.extract_flight_info(page, url)
                elif platform == 'etsy':
                    # Special handling for Etsy
                    title = await self.extract_text_content(page, config['title_selectors'])
                    if not title:
                        title = await page.evaluate('''
                            () => {
                                const selectors = ['h1', '[data-testid*="title"]', '[class*="title"]'];
                                for (const sel of selectors) {
                                    const element = document.querySelector(sel);
                                    if (element && element.textContent.trim()) {
                                        return element.textContent.trim();
                                    }
                                }
                                return document.title.split(' - ')[0] || document.title;
                            }
                        ''')
                    
                    price = await self.extract_etsy_price(page)
                    
                    if title and price:
                        title = title[:200] if len(title) > 200 else title
                        print(f"Successfully extracted Etsy: {title[:50]}... - ${price:.2f}")
                        return title, price
                    return None
                else:
                    return await self.extract_standard_product(page, platform, config)
                
            except Exception as e:
                print(f"Error scraping {platform}: {str(e)}")
                return None
            finally:
                if browser:
                    await browser.close()
    
    def get_supported_platforms(self) -> Dict[str, Dict[str, str]]:
        """Get information about supported platforms"""
        return self.get_platform_info()
    
    @staticmethod
    def get_platform_info() -> Dict[str, Dict[str, str]]:
        """Get platform information for UI"""
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
                'tips': 'Use the catalog URL for UGC items. Prices shown in Robux.',
                'currency': 'robux'
            },
            'flights': {
                'name': 'Flight Tickets',
                'example_url': 'https://www.kayak.com/flights/NYC-LAX/2024-03-15',
                'icon': '✈️',
                'tips': 'Use flight search result URLs from Kayak, Booking.com, Priceline, or Momondo (Expedia removed)'
            }
        }


# Test function
async def test_scraper():
    """Test the scraper"""
    scraper = MultiPlatformScraper()
    
    print("Testing Multi-Platform Scraper")
    print("=" * 40)
    
    test_urls = [
        "https://www.amazon.com/dp/B08N5WRWNW",
        "https://www.etsy.com/listing/123456789/test"
    ]
    
    for url in test_urls:
        print(f"\nTesting: {url}")
        try:
            result = await scraper.scrape_product(url)
            if result:
                title, price = result
                print(f"Success: {title[:50]}... - ${price:.2f}")
            else:
                print("Failed to scrape")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_scraper())