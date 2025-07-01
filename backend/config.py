# backend/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # Database
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or 'storenvy_tracker.db'
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Scheduler settings
    CHECK_INTERVAL_HOURS = int(os.environ.get('CHECK_INTERVAL_HOURS', 12))
    
    # Scraping settings
    HEADLESS_BROWSER = os.environ.get('HEADLESS_BROWSER', 'True').lower() == 'true'
    REQUEST_DELAY_SECONDS = int(os.environ.get('REQUEST_DELAY_SECONDS', 3))

