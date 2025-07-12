# backend/improved_flight_scraper.py - Enhanced Flight Scraping with Better Price Detection
import asyncio
import re
import random
import json
from typing import Optional, Tuple, Dict, List
from urllib.parse import urlparse, parse_qs
from playwright.async_api import async_playwright
import time
from datetime import datetime


class ImprovedFlightScraper:
    """Enhanced flight scraper with better price detection and anti-bot measures"""
    
    def __init__(self):
        self.flight_configs = {
            'kayak': {
                'domain_patterns': ['kayak.com'],
                'price_selectors': [
                    # Updated 2024 Kayak selectors
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
                    # Alternative selectors for different Kayak layouts
                    'div[class*="FlightsTicket"] span[class*="price"]',
                    'a[class*="FlightsTicket"] span.price-text',
                    'div.flight-card .price-text',
                    '[data-testid="flight-card"] .price-text'
                ],
                'wait_selectors': [
                    'div[data-resultid]',
                    'div.resultWrapper',
                    '.result-price',
                    'div[class*="FlightsTicket"]'
                ],
                'wait_time': 12000,
                'scroll_time': 8000
            },
            'booking': {
                'domain_patterns': ['booking.com'],
                'price_selectors': [
                    'div[data-testid="flight-card-segment"] .bui-price-display__value',
                    '.bui-price-display__value',
                    '[data-testid="price"] span',
                    '.flight-result-price'
                ],
                'wait_selectors': [
                    '[data-testid="flight-card-segment"]',
                    '.flight-result'
                ],
                'wait_time': 10000,
                'scroll_time': 5000
            },
            'priceline': {
                'domain_patterns': ['priceline.com'],
                'price_selectors': [
                    '.price-amount',
                    '.flight-price .price',
                    '[data-test-id="price"]',
                    '.fare-price'
                ],
                'wait_selectors': [
                    '.flight-result',
                    '.fare-display'
                ],
                'wait_time': 10000,
                'scroll_time': 5000
            },
            'momondo': {
                'domain_patterns': ['momondo.com'],
                'price_selectors': [
                    '.price-text',
                    '[data-testid="price"]',
                    '.fare-price'
                ],
                'wait_selectors': [
                    '.flight-result',
                    '[data-testid="flight-result"]'
                ],
                'wait_time': 10000,
                'scroll_time': 5000
            },
            'expedia': {
                'domain_patterns': ['expedia.com'],
                'price_selectors': [
                    '.price-amount',
                    '.flight-price',
                    '[data-test-id="price-summary"]'
                ],
                'wait_selectors': [
                    '.flight-module',
                    '.results-item'
                ],
                'wait_time': 10000,
                'scroll_time': 5000
            }
        }
    
    def detect_flight_platform(self, url: str) -> Optional[str]:
        """Detect which flight platform the URL belongs to"""
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            
            for platform, config in self.flight_configs.items():
                for pattern in config['domain_patterns']:
                    if pattern in domain:
                        return platform
            return None
        except Exception as e:
            print(f"Error detecting flight platform: {e}")
            return None
    
    async def setup_stealth_browser(self, platform: str):
        """Set up browser with enhanced stealth configuration"""
        try:
            # Enhanced user agents for 2024
            user_agents = [
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0'
            ]
            
            user_agent = random.choice(user_agents)
            
            context = await self.browser.new_context(
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
                    'Sec-Fetch-Site': 'none',
                    'Cache-Control': 'max-age=0'
                }
            )
            
            page = await context.new_page()
            
            # Enhanced stealth script for flight sites
            await page.add_init_script("""
                // Remove webdriver property
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
                
                // Mock permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
                
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
            print(f"Error setting up stealth browser: {e}")
            raise
    
    async def simulate_human_behavior(self, page, platform: str):
        """Enhanced human behavior simulation for flight sites"""
        try:
            config = self.flight_configs.get(platform, {})
            
            # Random initial wait
            await asyncio.sleep(random.uniform(2, 4))
            
            # Simulate reading the page
            for _ in range(random.randint(3, 6)):
                x = random.randint(200, 1500)
                y = random.randint(200, 800)
                await page.mouse.move(x, y)
                await asyncio.sleep(random.uniform(0.2, 0.5))
            
            # Scroll to load dynamic content (critical for flight sites)
            scroll_steps = random.randint(3, 6)
            for i in range(scroll_steps):
                scroll_y = 300 * (i + 1) + random.randint(-50, 50)
                await page.evaluate(f"window.scrollTo({{top: {scroll_y}, behavior: 'smooth'}})")
                await asyncio.sleep(random.uniform(1, 2))
            
            # Wait for content to load after scrolling
            scroll_time = config.get('scroll_time', 5000)
            await asyncio.sleep(scroll_time / 1000)
            
            # Move mouse over potential flight results
            await page.mouse.move(random.randint(400, 1200), random.randint(300, 700))
            await asyncio.sleep(random.uniform(0.5, 1))
            
        except Exception as e:
            print(f"Error simulating human behavior: {e}")
    
    async def wait_for_flight_results(self, page, platform: str):
        """Wait for flight results to load completely"""
        try:
            config = self.flight_configs.get(platform, {})
            wait_selectors = config.get('wait_selectors', [])
            wait_time = config.get('wait_time', 10000)
            
            print(f"Waiting for flight results to load for {platform}...")
            
            # Try each wait selector
            for selector in wait_selectors:
                try:
                    await page.wait_for_selector(selector, timeout=wait_time)
                    print(f"Found flight results with selector: {selector}")
                    break
                except Exception:
                    continue
            else:
                print("No specific flight result selectors found, waiting for general load...")
            
            # Additional wait for JavaScript to finish
            await asyncio.sleep(3)
            
            # Check if we can see any price elements
            price_selectors = config.get('price_selectors', [])
            for selector in price_selectors[:3]:  # Check first 3 selectors
                try:
                    element = await page.query_selector(selector)
                    if element:
                        print(f"Price elements detected with selector: {selector}")
                        return True
                except Exception:
                    continue
            
            print("Flight results may not have loaded completely")
            return False
            
        except Exception as e:
            print(f"Error waiting for flight results: {e}")
            return False
    
    async def extract_flight_prices(self, page, platform: str) -> List[float]:
        """Extract all available flight prices from the page"""
        try:
            config = self.flight_configs.get(platform, {})
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
                                price = await self.extract_price_from_text(price_text)
                                if price and 10 <= price <= 50000:  # Reasonable flight price range
                                    all_prices.append(price)
                                    print(f"Extracted price: ${price} from text: '{price_text.strip()}'")
                        except Exception as e:
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
                print(f"Price range: ${min(unique_prices)} - ${max(unique_prices)}")
            
            return unique_prices
            
        except Exception as e:
            print(f"Error extracting flight prices: {e}")
            return []
    
    async def extract_price_from_text(self, price_text: str) -> Optional[float]:
        """Enhanced price extraction with better regex patterns"""
        if not price_text:
            return None
        
        try:
            # Clean the text
            cleaned_text = price_text.strip().replace(',', '').replace(' ', '')
            
            # Enhanced price patterns for different formats
            patterns = [
                r'\$(\d{1,5}(?:\.\d{1,2})?)',  # $123.45
                r'USD\s*(\d{1,5}(?:\.\d{1,2})?)',  # USD 123.45
                r'(\d{1,5}(?:\.\d{1,2})?)\s*\$',  # 123.45$
                r'(\d{1,5}(?:\.\d{1,2})?)\s*USD',  # 123.45 USD
                r'(\d{1,5}(?:\.\d{1,2})?)',  # 123.45 (plain number)
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, cleaned_text, re.IGNORECASE)
                if matches:
                    for match in matches:
                        try:
                            price = float(match)
                            if 10 <= price <= 50000:  # Reasonable flight price range
                                return price
                        except (ValueError, TypeError):
                            continue
            
            return None
        except Exception as e:
            print(f"Error extracting price from '{price_text}': {e}")
            return None
    
    def parse_flight_route_from_url(self, url: str) -> str:
        """Enhanced flight route parsing"""
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)
            
            if 'kayak.com' in domain:
                # Enhanced Kayak URL parsing
                kayak_match = re.search(r'/flights/([A-Z]{3})-([A-Z]{3})/(\d{4}-\d{2}-\d{2})(?:/(\d{4}-\d{2}-\d{2}))?', path)
                if kayak_match:
                    from_code, to_code, dep_date, ret_date = kayak_match.groups()
                    if ret_date:
                        return f"✈️ {from_code} → {to_code} | {dep_date} to {ret_date}"
                    else:
                        return f"✈️ {from_code} → {to_code} | {dep_date} (One-way)"
                
                # Try query parameters
                origin = query_params.get('origin', [''])[0]
                destination = query_params.get('destination', [''])[0]
                if origin and destination:
                    return f"✈️ {origin} → {destination}"
                
                return "✈️ Kayak Flight Search"
            
            # Add parsing for other sites...
            return "✈️ Flight Search"
            
        except Exception as e:
            print(f"Error parsing flight URL: {e}")
            return "✈️ Flight Search"
    
    async def scrape_flight(self, url: str) -> Optional[Tuple[str, float]]:
        """Main flight scraping method with enhanced reliability"""
        platform = self.detect_flight_platform(url)
        if not platform:
            print(f"Unsupported flight platform for URL: {url}")
            return None
        
        print(f"Scraping {platform} flight: {url}")
        
        async with async_playwright() as p:
            self.browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-gpu',
                    '--disable-extensions',
                    '--disable-plugins',
                    '--disable-images',  # Faster loading
                    '--disable-javascript-harmony-shipping',
                    '--memory-pressure-off',
                    '--max_old_space_size=4096'
                ]
            )
            
            try:
                page = await self.setup_stealth_browser(platform)
                
                print(f"Navigating to: {url}")
                response = await page.goto(url, 
                                         wait_until='domcontentloaded', 
                                         timeout=30000)
                
                if not response or response.status >= 400:
                    print(f"Failed to load page, status: {response.status if response else 'None'}")
                    return None
                
                # Simulate human behavior and wait for results
                await self.simulate_human_behavior(page, platform)
                
                # Wait for flight results to load
                results_loaded = await self.wait_for_flight_results(page, platform)
                if not results_loaded:
                    print("Flight results may not have loaded properly")
                
                # Extract all available prices
                prices = await self.extract_flight_prices(page, platform)
                
                if prices:
                    # Use the lowest price found
                    lowest_price = min(prices)
                    title = self.parse_flight_route_from_url(url)
                    
                    print(f"Successfully scraped {platform}: {title} - ${lowest_price:.2f}")
                    print(f"Found {len(prices)} total prices, selected lowest: ${lowest_price:.2f}")
                    
                    return title, lowest_price
                else:
                    print(f"No valid prices found for {platform}")
                    
                    # Debug: Save page content for analysis
                    try:
                        content = await page.content()
                        with open(f'debug_{platform}_{int(time.time())}.html', 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"Saved debug HTML for {platform}")
                    except Exception:
                        pass
                    
                    return None
                
            except Exception as e:
                print(f"Error scraping {platform}: {str(e)}")
                return None
            finally:
                await self.browser.close()


# Test function
async def test_improved_flight_scraper():
    """Test the improved flight scraper"""
    scraper = ImprovedFlightScraper()
    
    test_urls = [
        "https://www.kayak.com/flights/LAX-NYC/2024-03-15/2024-03-22",
        "https://www.kayak.com/flights/SFO-BOS/2024-04-10",
    ]
    
    for url in test_urls:
        print(f"\n{'='*60}")
        print(f"Testing: {url}")
        print('='*60)
        
        result = await scraper.scrape_flight(url)
        if result:
            title, price = result
            print(f"✅ SUCCESS: {title} - ${price:.2f}")
        else:
            print("❌ FAILED to scrape")


if __name__ == "__main__":
    asyncio.run(test_improved_flight_scraper())