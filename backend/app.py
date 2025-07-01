# backend/app.py
from flask import Flask, jsonify, request, send_file, send_from_directory
from flask_cors import CORS
from tracker import StorenvyPriceTracker
import asyncio
import json
from pathlib import Path
import threading
import schedule
import time
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize tracker
tracker = StorenvyPriceTracker()

# Global variable to store email config
email_config_file = Path("email_config.json")
email_config = {}

if email_config_file.exists():
    with open(email_config_file, 'r') as f:
        email_config = json.load(f)

# Background scheduler
scheduler_running = False
scheduler_thread = None

# SERVE THE FRONTEND
@app.route('/')
def index():
    # Go up one directory from backend to find frontend folder
    frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'index.html')
    return send_file(frontend_path)

@app.route('/css/<path:filename>')
def css_files(filename):
    frontend_css = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'css')
    return send_from_directory(frontend_css, filename)

@app.route('/js/<path:filename>')
def js_files(filename):
    frontend_js = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'js')
    return send_from_directory(frontend_js, filename)

# API ROUTES
@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all tracked products"""
    products = tracker.get_tracked_products()
    return jsonify(products)

@app.route('/api/products', methods=['POST'])
def add_product():
    """Add a new product to track"""
    data = request.json
    url = data.get('url')
    target_price = data.get('target_price')
    
    if not url or target_price is None:
        return jsonify({'error': 'URL and target price are required'}), 400
    
    try:
        target_price = float(target_price)
        tracker.add_product(url, target_price)
        return jsonify({'message': 'Product added successfully'}), 201
    except ValueError:
        return jsonify({'error': 'Invalid price format'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a tracked product"""
    try:
        tracker.delete_product(product_id)
        return jsonify({'message': 'Product deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/check-prices', methods=['POST'])
def check_prices():
    """Manually check all product prices"""
    try:
        # Run the async function in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(tracker.check_all_products(email_config))
        
        # Return updated products
        products = tracker.get_tracked_products()
        return jsonify({
            'message': 'Price check completed',
            'products': products
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/email-config', methods=['GET'])
def get_email_config():
    """Get current email configuration status"""
    return jsonify({
        'enabled': email_config.get('enabled', False),
        'configured': bool(email_config.get('smtp_server'))
    })

@app.route('/api/email-config', methods=['POST'])
def update_email_config():
    """Update email configuration"""
    global email_config
    data = request.json
    
    email_config = {
        'enabled': data.get('enabled', False),
        'smtp_server': data.get('smtp_server', ''),
        'smtp_port': int(data.get('smtp_port', 587)),
        'from_email': data.get('from_email', ''),
        'password': data.get('password', ''),
        'to_email': data.get('to_email', '')
    }
    
    # Save to file
    with open(email_config_file, 'w') as f:
        json.dump(email_config, f)
    
    return jsonify({'message': 'Email configuration updated'}), 200

@app.route('/api/scheduler/status', methods=['GET'])
def get_scheduler_status():
    """Get scheduler status"""
    return jsonify({
        'running': scheduler_running,
        'interval_hours': 12
    })

@app.route('/api/scheduler/start', methods=['POST'])
def start_scheduler():
    """Start automatic price checking"""
    global scheduler_running, scheduler_thread
    
    if scheduler_running:
        return jsonify({'message': 'Scheduler already running'}), 200
    
    scheduler_running = True
    
    def run_scheduler():
        schedule.every(12).hours.do(
            lambda: asyncio.run(tracker.check_all_products(email_config))
        )
        
        while scheduler_running:
            schedule.run_pending()
            time.sleep(60)
    
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.start()
    
    return jsonify({'message': 'Scheduler started'}), 200

@app.route('/api/scheduler/stop', methods=['POST'])
def stop_scheduler():
    """Stop automatic price checking"""
    global scheduler_running
    
    scheduler_running = False
    return jsonify({'message': 'Scheduler stopped'}), 200

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics about tracked products"""
    products = tracker.get_tracked_products()
    
    total_products = len(products)
    products_below_target = sum(1 for p in products if p.get('last_price') and p['last_price'] <= p['target_price'])
    total_savings = sum(p['target_price'] - p['last_price'] for p in products 
                       if p.get('last_price') and p['last_price'] <= p['target_price'])
    
    return jsonify({
        'total_products': total_products,
        'products_below_target': products_below_target,
        'total_savings': round(total_savings, 2)
    })

if __name__ == '__main__':
    print("\n" + "="*50)
    print("STORENVY PRICE TRACKER")
    print("="*50)
    print("\nBackend server starting...")
    print("\nOnce started, open your browser to:")
    print("→ http://localhost:5000")
    print("\nPress Ctrl+C to stop the server")
    print("="*50 + "\n")
    
    app.run(debug=True, port=5000, host='0.0.0.0')