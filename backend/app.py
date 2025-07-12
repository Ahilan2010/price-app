# backend/app.py - COMPLETE VERSION WITH MULTI-PLATFORM SUPPORT AND REAL-TIME UPDATES
from flask import Flask, jsonify, request, send_file, send_from_directory
from flask_cors import CORS
from tracker import StorenvyPriceTracker
from stock_tracker import StockPriceTracker
from scheduler_service import PersistentSchedulerService
import asyncio
import json
from pathlib import Path
import os

def validate_and_clean_url(url: str) -> str:
    """Validate and clean product URLs"""
    url = url.strip()
    
    # Ensure URL has protocol
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Remove tracking parameters for cleaner URLs
    if 'amazon.com' in url:
        # Extract ASIN for Amazon URLs
        import re
        asin_match = re.search(r'/dp/([A-Z0-9]{10})', url)
        if asin_match:
            domain = urlparse(url).netloc
            return f"https://{domain}/dp/{asin_match.group(1)}"
    
    return url

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize trackers
tracker = StorenvyPriceTracker()
stock_tracker = StockPriceTracker()

# Initialize scheduler service
scheduler_service = PersistentSchedulerService()

# Global variable to store email config
email_config_file = Path("email_config.json")
email_config = {}

if email_config_file.exists():
    with open(email_config_file, 'r') as f:
        email_config = json.load(f)

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

# PRODUCT API ROUTES
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
        
        # Validate that the URL is from a supported platform
        platform = tracker.scraper.detect_platform(url)
        if not platform:
            return jsonify({'error': 'Unsupported e-commerce platform. Please use a supported website.'}), 400
        
        tracker.add_product(url, target_price)
        return jsonify({'message': f'Product from {platform.title()} added successfully'}), 201
    except ValueError as ve:
        return jsonify({'error': str(ve)}), 400
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
    """Manually check all product prices with real-time response"""
    try:
        # Run the async function in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(tracker.check_all_products(email_config))
        
        # Return updated products for real-time frontend updates
        products = tracker.get_tracked_products()
        return jsonify({
            'message': 'Price check completed',
            'products': products,
            'timestamp': str(asyncio.get_event_loop().time() if hasattr(asyncio, 'get_event_loop') else 'now')
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# NEW ROUTE: Get supported platforms
@app.route('/api/platforms', methods=['GET'])
def get_platforms():
    """Get all supported e-commerce platforms"""
    platforms = tracker.get_supported_platforms()
    return jsonify(platforms)

# STOCK API ROUTES
@app.route('/api/stocks', methods=['GET'])
def get_stock_alerts():
    """Get all stock alerts"""
    alerts = stock_tracker.get_stock_alerts()
    return jsonify(alerts)

@app.route('/api/stocks', methods=['POST'])
def add_stock_alert():
    """Add a new stock alert"""
    data = request.json
    symbol = data.get('symbol', '').upper().strip()
    alert_type = data.get('alert_type')
    threshold = data.get('threshold')
    
    if not symbol or not alert_type or threshold is None:
        return jsonify({'error': 'Symbol, alert type, and threshold are required'}), 400
    
    # Validate alert type
    valid_alert_types = ['price_above', 'price_below', 'percent_up', 'percent_down']
    if alert_type not in valid_alert_types:
        return jsonify({'error': f'Invalid alert type. Must be one of: {valid_alert_types}'}), 400
    
    try:
        threshold = float(threshold)
        stock_tracker.add_stock_alert(symbol, alert_type, threshold)
        return jsonify({'message': f'Stock alert added for {symbol}'}), 201
    except ValueError:
        return jsonify({'error': 'Invalid threshold format'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stocks/<int:alert_id>', methods=['DELETE'])
def delete_stock_alert(alert_id):
    """Delete a stock alert"""
    try:
        stock_tracker.delete_stock_alert(alert_id)
        return jsonify({'message': 'Stock alert deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stocks/check', methods=['POST'])
def check_stock_prices():
    """Manually check all stock prices with real-time response"""
    try:
        # Run the async function in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(stock_tracker.check_all_stock_alerts(email_config))
        
        # Return updated alerts for real-time frontend updates
        alerts = stock_tracker.get_stock_alerts()
        return jsonify({
            'message': 'Stock price check completed',
            'alerts': alerts,
            'timestamp': str(asyncio.get_event_loop().time() if hasattr(asyncio, 'get_event_loop') else 'now')
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stocks/stats', methods=['GET'])
def get_stock_stats():
    """Get statistics about stock alerts"""
    stats = stock_tracker.get_stock_stats()
    return jsonify(stats)

@app.route('/api/stocks/reset-triggered', methods=['POST'])
def reset_triggered_stock_alerts():
    """Reset all triggered alerts (useful for daily reset)"""
    try:
        stock_tracker.reset_triggered_alerts()
        return jsonify({'message': 'All triggered alerts have been reset'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# EMAIL CONFIGURATION ROUTES
@app.route('/api/email-config', methods=['GET'])
def get_email_config():
    """Get current email configuration status"""
    return jsonify({
        'enabled': email_config.get('enabled', False),
        'configured': bool(email_config.get('smtp_server')),
        'smtp_server': email_config.get('smtp_server', ''),
        'smtp_port': email_config.get('smtp_port', 587),
        'from_email': email_config.get('from_email', ''),
        'to_email': email_config.get('to_email', '')
        # Note: We never return the password for security
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

# STATISTICS ROUTES
@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics about tracked products and stocks"""
    # Product stats
    products = tracker.get_tracked_products()
    
    total_products = len(products)
    products_below_target = sum(1 for p in products if p.get('last_price') and p['last_price'] <= p['target_price'])
    total_savings = sum(p['target_price'] - p['last_price'] for p in products 
                       if p.get('last_price') and p['last_price'] <= p['target_price'])
    
    # Stock stats
    stock_stats = stock_tracker.get_stock_stats()
    
    return jsonify({
        # Product stats (existing)
        'total_products': total_products,
        'products_below_target': products_below_target,
        'total_savings': round(total_savings, 2),
        
        # Stock stats (new)
        'total_stock_alerts': stock_stats['total_alerts'],
        'triggered_stock_alerts': stock_stats['triggered_alerts'],
        'monitoring_stock_alerts': stock_stats['monitoring_alerts']
    })

# SCHEDULER CONTROL ROUTES
@app.route('/api/scheduler/status', methods=['GET'])
def get_scheduler_status():
    """Get scheduler service status"""
    status = scheduler_service.status()
    return jsonify(status)

@app.route('/api/scheduler/start', methods=['POST'])
def start_scheduler():
    """Start the scheduler service"""
    try:
        scheduler_service.start()
        return jsonify({'message': 'Scheduler service started'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scheduler/stop', methods=['POST'])
def stop_scheduler():
    """Stop the scheduler service"""
    try:
        scheduler_service.stop()
        return jsonify({'message': 'Scheduler service stopped'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# NEW ROUTE: Real-time price update endpoint
@app.route('/api/products/<int:product_id>/price', methods=['GET'])
def get_product_current_price(product_id):
    """Get current price for a specific product (for real-time updates)"""
    try:
        products = tracker.get_tracked_products()
        product = next((p for p in products if p['id'] == product_id), None)
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        response_data = {
            'id': product['id'],
            'current_price': product['last_price'],
            'target_price': product['target_price'],
            'last_checked': product['last_checked'],
            'status': product['status']
        }
        
        # Include metadata for flights
        if product.get('platform') == 'flights' and product.get('metadata'):
            response_data['metadata'] = product['metadata']
        
        return jsonify(response_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🛍️  PRICETRACKER WEB APPLICATION")
    print("="*60)
    print("\n🚀 Web server starting...")
    print("🌐 Interface: http://localhost:5000")
    print("📦 Products: Manual + Background service")
    print("📈 Stocks: Manual + Background service")
    print("🌍 Now supporting 7 major e-commerce platforms!")
    print("\n💡 For persistent background checking:")
    print("   Run: python scheduler_service.py")
    print("\n⏹️  Press Ctrl+C to stop the web server")
    print("="*60 + "\n")
    
    try:
        app.run(debug=True, port=5000, host='0.0.0.0')
    finally:
        # Stop scheduler when app shuts down
        scheduler_service.stop()