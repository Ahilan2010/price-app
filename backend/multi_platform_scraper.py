# backend/multi_platform_scraper.py - FIXED FLIGHT TRACKING VERSION
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
    """Multi-platform e-commerce scraper with fixed flight tracking"""
    
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
                    # Kayak updated selectors - targeting the ACTUAL cheapest available price
                    'div[data-testid="cheapest-total-price"]',
                    'div[data-testid="result-price"] span[role="text"]',
                    'div.r99X-price-text',
                    'div.r99X span[role="text"]',
                    'span[data-testid="price-text"]',
                    'div[data-testid="price"] span',
                    # Fallback selectors for other sites
                    'div.e2GB-price-text',
                    'div.FlightCardPrice-module__priceContainer___nXXv2',
                    'div.Text-sc-1xtb652-0.koHeTu',
                    'span[data-testid="price"]',
                    '.price-text',
                    '.flight-price',
                    'span.price',
                    '.fare-price',
                    'div[class*="price"] span',
                    '.total-price',
                    '[data-testid="flight-price"]',
                    # Additional Kayak selectors
                    'div[class*="price-display"]',
                    'span[class*="price-text"]'
                ],
                'wait_time': 8000,  # Increased wait time for flights
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
    
    async def scrape_flight_with_enhanced_selectors(self, page, url: str) -> Optional[Tuple[str, float]]:
        """Enhanced flight scraping with better price detection"""
        try:
            print("Enhanced flight scraping starting...")
            
            # Parse title from URL
            title = self.parse_flight_route_from_url(url)
            
            # Wait longer for flight pages to load completely
            await page.wait_for_timeout(10000)
            
            # Try to find the lowest available price
            price = None
            domain = urlparse(url).netloc.lower()
            
            if 'kayak.com' in domain:
                print("Scraping Kayak with enhanced selectors...")
                
                # Enhanced Kayak price extraction
                kayak_price_selectors = [
                    # Primary cheapest price selectors
                    'div[data-testid="cheapest-total-price"]',
                    'div[data-testid="result-price"] span[role="text"]',
                    'div[aria-label*="price"] span[role="text"]',
                    'div[data-testid="price-text"]',
                    'span[data-testid="price-text"]',
                    
                    # Result list price selectors
                    'div.r99X-price-text',
                    'div.r99X span[role="text"]',
                    'div[class*="price-display"] span',
                    'span[class*="price-text"]',
                    
                    # Fallback selectors
                    'div.e2GB-price-text',
                    'div[data-testid="price"] span',
                    'span[data-testid="price"]',
                    '.price-text',
                    'div[class*="price"] span[role="text"]',
                    
                    # Additional selectors for different Kayak layouts
                    'div[data-testid="result-item"] span[role="text"]',
                    'div[class*="result-price"] span',
                    'span[aria-label*="price"]'
                ]
                
                # Try each selector and collect all prices
                all_prices = []
                
                for selector in kayak_price_selectors:
                    try:
                        elements = await page.query_selector_all(selector)
                        print(f"Found {len(elements)} elements with selector: {selector}")
                        
                        for element in elements:
                            price_text = await element.text_content()
                            if price_text:
                                extracted_price = await self.extract_price_from_text(price_text)
                                if extracted_price and extracted_price > 10:  # Reasonable minimum
                                    all_prices.append(extracted_price)
                                    print(f"Found price: ${extracted_price} from selector: {selector}")
                        
                        if all_prices:
                            break  # Found prices, use them
                            
                    except Exception as e:
                        print(f"Selector {selector} failed: {e}")
                        continue
                
                # If we found multiple prices, take the lowest available one
                if all_prices:
                    price = min(all_prices)
                    print(f"Selected lowest price from {len(all_prices)} options: ${price}")
                else:
                    print("No valid prices found on Kayak")
                
            else:
                # For other flight sites, use the existing selectors
                config = self.platform_configs['flights']
                price_text = await self.extract_text_content(page, config['price_selectors'])
                
                if price_text:
                    price = await self.extract_price_from_text(price_text)
            
            if price:
                print(f"Successfully scraped flight: {title} - ${price:.2f}")
                return title, price
            else:
                print(f"Failed to extract price for flight: {title}")
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
                    '--disable-gpu'
                ]
            )
            
            try:
                page = await self.setup_browser_page(browser, platform)
                config = self.platform_configs[platform]
                
                print(f"Navigating to: {url}")
                await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                await page.wait_for_timeout(config['wait_time'])
                
                # Simulate human behavior for anti-bot bypass
                await self.simulate_human_behavior(page)
                
                # Special handling for Roblox
                if platform == 'roblox':
                    result = await self.extract_roblox_info(page)
                    if result:
                        return result
                
                # Special handling for flights with enhanced scraping
                elif platform == 'flights':
                    result = await self.scrape_flight_with_enhanced_selectors(page, url)
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
                    price_text = await self.extract_text_content(page, config['price_selectors'])
                    if price_text:
                        price = await self.extract_price_from_text(price_text)
                        if price:
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
async def test_scraper():
    """Test the scraper with various URLs"""
    scraper = MultiPlatformScraper()
    
    test_urls = [
        "https://www.amazon.com/dp/B08N5WRWNW",
        "https://www.etsy.com/listing/123456789/test-product",
        "https://www.roblox.com/catalog/123456789/test-item",
        "https://www.kayak.com/flights/LAX-NYC/2024-03-15/2024-03-22"
    ]
    
    for url in test_urls:
        print(f"\nTesting: {url}")
        result = await scraper.scrape_product(url)
        if result:
            title, price = result
            print(f"Success: {title} - ${price:.2f}")
        else:
            print("Failed to scrape")


if __name__ == "__main__":
    asyncio.run(test_scraper())