# backend/scheduler_service.py - UPDATED WITH FLIGHT-SPECIFIC INTERVALS
import asyncio
import json
import time
import signal
import sys
import threading
from pathlib import Path
from datetime import datetime, timedelta
import schedule
import logging

from tracker import StorenvyPriceTracker
from stock_tracker import StockPriceTracker

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PersistentSchedulerService:
    def __init__(self):
        self.running = False
        self.product_tracker = StorenvyPriceTracker()
        self.stock_tracker = StockPriceTracker()
        self.email_config_file = Path("email_config.json")
        self.email_config = {}
        self.product_thread = None
        self.stock_thread = None
        self.flight_thread = None
        
        # Load email config
        self.load_email_config()
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def load_email_config(self):
        """Load email configuration from file."""
        if self.email_config_file.exists():
            try:
                with open(self.email_config_file, 'r') as f:
                    self.email_config = json.load(f)
                logger.info("Email configuration loaded")
            except Exception as e:
                logger.error(f"Failed to load email config: {e}")
                self.email_config = {}
        else:
            logger.info("No email configuration found")
            self.email_config = {}
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
        sys.exit(0)
    
    def product_scheduler_worker(self):
        """Worker for e-commerce product price checking every 6 hours."""
        # Schedule product checks every 6 hours
        schedule.every(6).hours.do(self.check_ecommerce_products_job)
        
        # Also run immediately on startup
        logger.info("🚀 E-commerce product scheduler started - will check every 6 hours")
        self.check_ecommerce_products_job()
        
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        
        logger.info("📦 E-commerce product scheduler stopped")
    
    def flight_scheduler_worker(self):
        """Worker for flight price checking every 30 minutes."""
        # Schedule flight checks every 30 minutes
        schedule.every(30).minutes.do(self.check_flight_prices_job)
        
        # Also run immediately on startup
        logger.info("🚀 Flight scheduler started - will check every 30 minutes")
        self.check_flight_prices_job()
        
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        
        logger.info("✈️ Flight scheduler stopped")
    
    def stock_scheduler_worker(self):
        """Worker for stock price checking every 5 minutes."""
        # Schedule stock checks every 5 minutes
        schedule.every(5).minutes.do(self.check_stocks_job)
        
        # Also run immediately on startup
        logger.info("🚀 Stock scheduler started - will check every 5 minutes")
        self.check_stocks_job()
        
        while self.running:
            schedule.run_pending()
            time.sleep(30)  # Check every 30 seconds for more precision
        
        logger.info("📈 Stock scheduler stopped")
    
    def check_ecommerce_products_job(self):
        """Job to check e-commerce product prices (excludes flights)."""
        try:
            logger.info("📦 Starting e-commerce product price check...")
            
            # Reload email config in case it changed
            self.load_email_config()
            
            # Run async function in event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.product_tracker.check_ecommerce_products_only(self.email_config))
            loop.close()
            
            logger.info("✅ E-commerce product price check completed")
            
        except Exception as e:
            logger.error(f"❌ Error in e-commerce product price check: {e}")
    
    def check_flight_prices_job(self):
        """Job to check flight prices only."""
        try:
            logger.info("✈️ Starting flight price check...")
            
            # Reload email config in case it changed
            self.load_email_config()
            
            # Run async function in event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.product_tracker.check_flight_products_only(self.email_config))
            loop.close()
            
            logger.info("✅ Flight price check completed")
            
        except Exception as e:
            logger.error(f"❌ Error in flight price check: {e}")
    
    def check_stocks_job(self):
        """Job to check stock prices."""
        try:
            logger.info("📈 Starting stock price check...")
            
            # Reload email config in case it changed
            self.load_email_config()
            
            # Run async function in event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.stock_tracker.check_all_stock_alerts(self.email_config))
            loop.close()
            
            logger.info("✅ Stock price check completed")
            
        except Exception as e:
            logger.error(f"❌ Error in stock price check: {e}")
    
    def start(self):
        """Start the persistent scheduler service."""
        if self.running:
            logger.warning("Scheduler service is already running")
            return
        
        self.running = True
        logger.info("🚀 Starting PriceTracker Scheduler Service...")
        logger.info("📦 E-commerce Products: Every 6 hours")
        logger.info("✈️ Flights: Every 30 minutes")
        logger.info("📈 Stocks: Every 5 minutes")
        
        # Start e-commerce product scheduler in separate thread
        self.product_thread = threading.Thread(
            target=self.product_scheduler_worker, 
            daemon=False,
            name="EcommerceProductScheduler"
        )
        
        # Start flight scheduler in separate thread
        self.flight_thread = threading.Thread(
            target=self.flight_scheduler_worker, 
            daemon=False,
            name="FlightScheduler"
        )
        
        # Start stock scheduler in separate thread
        self.stock_thread = threading.Thread(
            target=self.stock_scheduler_worker, 
            daemon=False,
            name="StockScheduler"
        )
        
        self.product_thread.start()
        self.flight_thread.start()
        self.stock_thread.start()
        
        logger.info("✅ Scheduler service started successfully")
    
    def stop(self):
        """Stop the scheduler service."""
        if not self.running:
            logger.warning("Scheduler service is not running")
            return
        
        logger.info("⏹️ Stopping scheduler service...")
        self.running = False
        
        # Clear all scheduled jobs
        schedule.clear()
        
        # Wait for threads to finish
        if self.product_thread and self.product_thread.is_alive():
            self.product_thread.join(timeout=5)
        
        if self.flight_thread and self.flight_thread.is_alive():
            self.flight_thread.join(timeout=5)
        
        if self.stock_thread and self.stock_thread.is_alive():
            self.stock_thread.join(timeout=5)
        
        logger.info("✅ Scheduler service stopped")
    
    def status(self):
        """Get the status of the scheduler service."""
        return {
            'running': self.running,
            'product_thread_alive': self.product_thread.is_alive() if self.product_thread else False,
            'flight_thread_alive': self.flight_thread.is_alive() if self.flight_thread else False,
            'stock_thread_alive': self.stock_thread.is_alive() if self.stock_thread else False,
            'email_configured': bool(self.email_config.get('enabled')),
            'ecommerce_interval': '6 hours',
            'flights_interval': '30 minutes',
            'stocks_interval': '5 minutes'
        }
    
    def run_forever(self):
        """Run the scheduler service forever (for standalone operation)."""
        self.start()
        
        try:
            # Keep the main thread alive
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received KeyboardInterrupt, shutting down...")
        finally:
            self.stop()


# Standalone script mode
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🛍️  PRICETRACKER SCHEDULER SERVICE")
    print("="*60)
    print("\n🚀 Starting persistent background service...")
    print("📦 E-commerce Products: Auto-check every 6 hours")
    print("✈️ Flights: Auto-check every 30 minutes")
    print("📈 Stocks: Auto-check every 5 minutes")
    print("\n💡 This service runs independently of the web app")
    print("⏹️  Press Ctrl+C to stop the service")
    print("="*60 + "\n")
    
    service = PersistentSchedulerService()
    service.run_forever()