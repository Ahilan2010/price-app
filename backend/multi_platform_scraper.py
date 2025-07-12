# backend/multi_platform_scraper.py - UPDATED VERSION WITH IMPROVED FLIGHT SCRAPING
import asyncio
import re
import random
import json
from typing import Optional, Tuple, Dict, List
from urllib.parse import urlparse, parse_qs
from playwright.async_api import async_playwright
import time
from datetime import datetime


class MultiPlatformScraper:
    """Multi-platform e-commerce scraper with improved flight tracking"""
    
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
                'domain_patterns': ['kayak.com', 'booking.com', 'priceline.com', 'momondo.com', 'expedia.com'],
                'price_selectors': [
                    # Updated 2024 Kayak selectors - MOST CURRENT
                    'div[data-resultid] span.price-text',
                    'div[data-resultid] .price-text', 
                    'div.resultWrapper span.price-text',
                    'div.price-text',
                    'span.price-text',
                    '[data-testid="price-text"]',
                    'div[class*="price"] span[role="text"]',
                    'div.bottom span.price-text',
                    'div.above-button span.price-text',
                    '.result-price .price-text',
                    '.booking-link .price-text',
                    
                    # Alternative Kayak selectors
                    'div[class*="FlightsTicket"] span[class*="price"]',
                    'a[class*="FlightsTicket"] span.price-text',
                    'div.flight-card .price-text',
                    '[data-testid="flight-card"] .price-text',
                    
                    # Other flight sites
                    'div[data-testid="flight-card-segment"] .bui-price-display__value',
                    '.bui-price-display__value',
                    '.price-amount',
                    '.flight-price .price',
                    '[data-test-id="price"]',
                    '.fare-price',
                    '.flight-result-price'
                ],
                'wait_selectors': [
                    'div[data-resultid]',
                    'div.resultWrapper', 
                    '.result-price',
                    'div[class*="FlightsTicket"]',
                    '[data-testid="flight-card-segment"]',
                    '.flight-result'
                ],
                'wait_time': 15000,  # Longer wait for flights
                'scroll_time': 8000,
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
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none'
                }
            )
            
            page = await context.new_page()
            
            # Enhanced stealth script for flight sites
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
                
                // Mock chrome runtime
                window.chrome = {
                    runtime: {}
                };
                
                // Remove automation indicators
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            """)
            
            return page
        except Exception as e:
            print(f"Error setting up browser page: {e}")
            raise
    
    async def simulate_human_behavior(self, page, platform: str):
        """Enhanced human behavior simulation"""
        try:
            config = self.platform_configs.get(platform, {})
            
            # Random wait
            await asyncio.sleep(random.uniform(1, 3))
            
            # Random mouse movements
            for _ in range(random.randint(2, 4)):
                x = random.randint(100, 1200)
                y = random.randint(100, 800)
                await page.mouse.move(x, y)
                await asyncio.sleep(random.uniform(0.1, 0.3))
            
            # Enhanced scrolling for flight sites
            if platform == 'flights':
                # More aggressive scrolling to load all content
                scroll_steps = random.randint(4, 8)
                for i in range(scroll_steps):
                    scroll_y = 400 * (i + 1) + random.randint(-100, 100)
                    await page.evaluate(f"window.scrollTo({{top: {scroll_y}, behavior: 'smooth'}})")
                    await asyncio.sleep(random.uniform(1, 2.5))
                
                # Wait for scroll time
                scroll_time = config.get('scroll_time', 5000)
                await asyncio.sleep(scroll_time / 1000)
            else:
                # Standard scrolling for other platforms
                scroll_positions = [200, 400, 600, 300, 100]
                for position in scroll_positions[:random.randint(2, 4)]:
                    await page.evaluate(f"window.scrollTo({{top: {position}, behavior: 'smooth'}})")
                    await asyncio.sleep(random.uniform(0.5, 1.2))
        except Exception as e:
            print(f"Error simulating human behavior: {e}")
    
    async def wait_for_content_load(self, page, platform: str):
        """Wait for platform-specific content to load"""
        try:
            config = self.platform_configs.get(platform, {})
            wait_selectors = config.get('wait_selectors', [])
            wait_time = config.get('wait_time', 10000)
            
            if platform == 'flights':
                print("Waiting for flight results to load...")
                
                # Try each wait selector
                for selector in wait_selectors:
                    try:
                        await page.wait_for_selector(selector, timeout=wait_time)
                        print(f"Found flight content with selector: {selector}")
                        break
                    except Exception:
                        continue
                else:
                    print("No specific flight selectors found, using general wait...")
                
                # Additional wait for JavaScript to finish
                await asyncio.sleep(3)
                
                # Check if we can see any price elements
                price_selectors = config.get('price_selectors', [])
                for selector in price_selectors[:5]:  # Check first 5 selectors
                    try:
                        element = await page.query_selector(selector)
                        if element:
                            print(f"Price elements detected with selector: {selector}")
                            return True
                    except Exception:
                        continue
                
                print("Flight results may not have loaded completely")
                return False
            else:
                # Standard wait for other platforms
                await page.wait_for_timeout(wait_time)
                return True
                
        except Exception as e:
            print(f"Error waiting for content load: {e}")
            return True  # Continue anyway
    
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
    
    async def extract_all_prices(self, page, platform: str) -> List[float]:
        """Extract all available prices from the page"""
        try:
            config = self.platform_configs.get(platform, {})
            price_selectors = config.get('price_selectors', [])
            
            all_prices = []
            
            print(f"Extracting prices for {platform} using {len(price_selectors)} selectors...")
            
            for i, selector in enumerate(price_selectors):
                try:
                    elements = await page.query_selector_all(selector)
                    print(f"Selector {i+1} ({selector}): Found {len(elements)} elements")
                    
                    for element in elements:
                        try:
                            price_text = await element.text_content()
                            if price_text:
                                if platform == 'roblox':
                                    price = await self.extract_robux_from_text(price_text)
                                else:
                                    price = await self.extract_price_from_text(price_text)
                                
                                if price and self.is_valid_price(price, platform):
                                    all_prices.append(price)
                                    print(f"Extracted price: {price} from text: '{price_text.strip()}'")
                        except Exception:
                            continue
                    
                    # If we found prices with this selector, we can stop
                    if all_prices:
                        print(f"Successfully extracted {len(all_prices)} prices with selector: {selector}")
                        break
                        
                except Exception as e:
                    print(f"Selector {selector} failed: {e}")
                    continue
            
            # Remove duplicates and sort
            unique_prices = list(set(all_prices))
            unique_prices.sort()
            
            print(f"Total unique prices found: {len(unique_prices)}")
            if unique_prices:
                if platform == 'roblox':
                    print(f"Price range: {min(unique_prices)} - {max(unique_prices)} Robux")
                else:
                    print(f"Price range: ${min(unique_prices)} - ${max(unique_prices)}")
            
            return unique_prices
            
        except Exception as e:
            print(f"Error extracting prices: {e}")
            return []
    
    def is_valid_price(self, price: float, platform: str) -> bool:
        """Check if price is within valid range for platform"""
        if platform == 'roblox':
            return 1 <= price <= 999999
        elif platform == 'flights':
            return 10 <= price <= 50000
        else:
            return 0.01 <= price <= 999999
    
    async def extract_price_from_text(self, price_text: str) -> Optional[float]:
        """Extract price from text with improved regex"""
        if not price_text:
            return None
        
        try:
            print(f"Extracting price from: '{price_text[:100]}'")
            
            # Clean the text
            cleaned_text = re.sub(r'[^\d.,\-\s$€£¥₹]', ' ', price_text)
            cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
            
            # Enhanced price patterns
            patterns = [
                r'US\s*\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)',
                r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)',
                r'(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)\s*\)',
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
    
    def parse_flight_route_from_url(self, url: str) -> str:
        """Enhanced flight route and dates parsing from URL"""
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            
            print(f"Parsing flight info from URL: {url}")
            
            if 'kayak.com' in domain:
                # Extract from Kayak URL path or query parameters
                path = parsed_url.path
                query_params = parse_qs(parsed_url.query)
                
                # Try path parsing first (e.g., /flights/LAX-NYC/2024-03-15/2024-03-22)
                kayak_match = re.search(r'/flights/([A-Z]{3})-([A-Z]{3})/(\d{4}-\d{2}-\d{2})(?:/(\d{4}-\d{2}-\d{2}))?', path)
                if kayak_match:
                    from_code, to_code, dep_date, ret_date = kayak_match.groups()
                    if ret_date:
                        return f"✈️ {from_code} → {to_code} | {dep_date} to {ret_date}"
                    else:
                        return f"✈️ {from_code} → {to_code} | {dep_date} (One-way)"
                
                # Try query parameter parsing
                if 'origin' in query_params and 'destination' in query_params:
                    origin = query_params['origin'][0] if query_params['origin'] else 'Unknown'
                    destination = query_params['destination'][0] if query_params['destination'] else 'Unknown'
                    dep_date = query_params.get('depart_date', [''])[0]
                    ret_date = query_params.get('return_date', [''])[0]
                    
                    if dep_date and ret_date:
                        return f"✈️ {origin} → {destination} | {dep_date} to {ret_date}"
                    elif dep_date:
                        return f"✈️ {origin} → {destination} | {dep_date} (One-way)"
                    else:
                        return f"✈️ {origin} → {destination}"
                
                return "✈️ Kayak Flight Search"
            
            elif 'booking.com' in domain:
                query_params = parse_qs(parsed_url.query)
                if 'ss' in query_params:  # departure city
                    ss = query_params['ss'][0]
                    checkin = query_params.get('checkin', [''])[0]
                    checkout = query_params.get('checkout', [''])[0]
                    
                    if checkin and checkout:
                        return f"✈️ {ss} Flight | {checkin} to {checkout}"
                    else:
                        return f"✈️ {ss} Flight Search"
                
                return "✈️ Booking.com Flight Search"
            
            elif 'priceline.com' in domain:
                # Extract from Priceline query parameters
                query_params = parse_qs(parsed_url.query)
                origin = query_params.get('from', [''])[0]
                destination = query_params.get('to', [''])[0]
                dep_date = query_params.get('departure', [''])[0]
                ret_date = query_params.get('return', [''])[0]
                
                if origin and destination:
                    if dep_date and ret_date:
                        return f"✈️ {origin} → {destination} | {dep_date} to {ret_date}"
                    elif dep_date:
                        return f"✈️ {origin} → {destination} | {dep_date} (One-way)"
                    else:
                        return f"✈️ {origin} → {destination}"
                
                return "✈️ Priceline Flight Search"
            
            elif 'momondo.com' in domain:
                # Extract from Momondo URL structure
                path = parsed_url.path
                momondo_match = re.search(r'/flight-search/([A-Z]{3})-([A-Z]{3})/(\d{4}-\d{2}-\d{2})(?:/(\d{4}-\d{2}-\d{2}))?', path)
                if momondo_match:
                    from_code, to_code, dep_date, ret_date = momondo_match.groups()
                    if ret_date:
                        return f"✈️ {from_code} → {to_code} | {dep_date} to {ret_date}"
                    else:
                        return f"✈️ {from_code} → {to_code} | {dep_date} (One-way)"
                
                return "✈️ Momondo Flight Search"
            
            elif 'expedia.com' in domain:
                # Extract from Expedia query parameters
                query_params = parse_qs(parsed_url.query)
                flight_1 = query_params.get('flight-1', [''])[0]
                dep_date = query_params.get('d1', [''])[0]
                ret_date = query_params.get('d2', [''])[0]
                
                if flight_1:
                    flight_match = re.search(r'([A-Z]{3}),([A-Z]{3})', flight_1)
                    if flight_match:
                        from_code, to_code = flight_match.groups()
                        if dep_date and ret_date:
                            return f"✈️ {from_code} → {to_code} | {dep_date} to {ret_date}"
                        elif dep_date:
                            return f"✈️ {from_code} → {to_code} | {dep_date} (One-way)"
                        else:
                            return f"✈️ {from_code} → {to_code}"
                
                return "✈️ Expedia Flight Search"
            
            return "✈️ Flight Search"
            
        except Exception as e:
            print(f"Error parsing flight URL: {e}")
            return "✈️ Flight Search"
    
    async def scrape_flight_with_enhanced_detection(self, page, url: str) -> Optional[Tuple[str, float]]:
        """Enhanced flight scraping with improved price detection"""
        try:
            print("Enhanced flight scraping starting...")
            
            # Parse title from URL
            title = self.parse_flight_route_from_url(url)
            
            # Wait for content to load
            await self.wait_for_content_load(page, 'flights')
            
            # Extract all available prices
            prices = await self.extract_all_prices(page, 'flights')
            
            if prices:
                # Use the lowest price found
                lowest_price = min(prices)
                print(f"Successfully scraped flight: {title} - ${lowest_price:.2f}")
                print(f"Found {len(prices)} total prices, selected lowest: ${lowest_price:.2f}")
                return title, lowest_price
            else:
                print(f"No valid prices found for flight")
                
                # Debug: Save page content for analysis
                try:
                    content = await page.content()
                    with open(f'debug_flight_{int(time.time())}.html', 'w', encoding='utf-8') as f:
                        f.write(content)
                    print("Saved debug HTML for flight")
                except Exception:
                    pass
                
                return None
                
        except Exception as e:
            print(f"Error in enhanced flight scraping: {e}")
            return None
    
    async def scrape_product(self, url: str) -> Optional[Tuple[str, float]]:
        """Main scraping method that detects platform and scrapes accordingly"""
        platform = self.detect_platform(url)
        if not platform:
            print(f"Unsupported platform for URL: {url}")
            return None
        
        print(f"Detected platform: {platform}")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--disable-gpu',
                    '--disable-extensions',
                    '--disable-plugins',
                    '--memory-pressure-off'
                ]
            )
            
            try:
                page = await self.setup_browser_page(browser, platform)
                config = self.platform_configs[platform]
                
                print(f"Navigating to: {url}")
                response = await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                
                if not response or response.status >= 400:
                    print(f"Failed to load page, status: {response.status if response else 'None'}")
                    return None
                
                await page.wait_for_timeout(config['wait_time'])
                
                # Simulate human behavior for anti-bot bypass
                await self.simulate_human_behavior(page, platform)
                
                # Special handling for Roblox
                if platform == 'roblox':
                    result = await self.extract_roblox_info(page)
                    if result:
                        return result
                
                # Special handling for flights with enhanced scraping
                elif platform == 'flights':
                    result = await self.scrape_flight_with_enhanced_detection(page, url)
                    if result:
                        return result
                
                # Standard e-commerce platforms
                else:
                    # Extract title
                    title = await self.extract_text_content(page, config['title_selectors'])
                    if not title:
                        print(f"Could not extract title for {platform}")
                        title = f"Product from {platform.title()}"
                    
                    # Extract price
                    prices = await self.extract_all_prices(page, platform)
                    if prices:
                        price = min(prices)  # Use lowest price
                        print(f"Successfully scraped: {title[:50]}... - ${price:.2f}")
                        return title, price
                
                print(f"Failed to extract complete product info for {url}")
                return None
                
            except Exception as e:
                print(f"Error scraping {url}: {str(e)}")
                return None
            finally:
                await browser.close()
    
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
            
            # Extract price using the enhanced method
            prices = await self.extract_all_prices(page, 'roblox')
            
            if item_name and prices:
                price = min(prices)  # Use lowest price
                print(f"Successfully extracted Roblox item: {item_name} - {price:.0f} Robux")
                return item_name, price
            
            return None
        except Exception as e:
            print(f"Error extracting Roblox info: {e}")
            return None
    
    @staticmethod
    def get_platform_info() -> Dict[str, Dict[str, str]]:
        """Get information about supported platforms"""
        return {
            'amazon': {'name': 'Amazon', 'icon': '🛒'},
            'ebay': {'name': 'eBay', 'icon': '🏷️'},
            'etsy': {'name': 'Etsy', 'icon': '🎨'},
            'walmart': {'name': 'Walmart', 'icon': '🏪'},
            'storenvy': {'name': 'Storenvy', 'icon': '🏬'},
            'roblox': {'name': 'Roblox', 'icon': '🎮'},
            'flights': {'name': 'Flights', 'icon': '✈️'}
        }


# Test function
async def test_updated_scraper():
    """Test the updated scraper with various URLs"""
    scraper = MultiPlatformScraper()
    
    test_urls = [
        "https://www.amazon.com/dp/B08N5WRWNW",
        "https://www.etsy.com/listing/123456789/test-product",
        "https://www.roblox.com/catalog/123456789/test-item",
        "https://www.kayak.com/flights/LAX-NYC/2024-03-15/2024-03-22"
    ]
    
    for url in test_urls:
        print(f"\n{'='*60}")
        print(f"Testing: {url}")
        print('='*60)
        
        result = await scraper.scrape_product(url)
        if result:
            title, price = result
            print(f"✅ SUCCESS: {title} - ${price:.2f}")
        else:
            print("❌ FAILED to scrape")


if __name__ == "__main__":
    asyncio.run(test_updated_scraper())