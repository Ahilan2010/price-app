# backend/service_app.py
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app import app

if __name__ == '__main__':
    # Set up logging for launchd
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("Starting Storenvy Price Tracker Service...")
    
    # Run without debug mode for production
    app.run(
        debug=False,
        port=5000,
        host='0.0.0.0',
        use_reloader=False  # Important: disable reloader for service
    )

