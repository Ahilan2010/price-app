# backend/app.py - FIXED VERSION WITH PROPER AUTH
from flask import Flask, jsonify, request, send_file, send_from_directory, session
from flask_cors import CORS
from tracker import StorenvyPriceTracker
from stock_tracker import StockPriceTracker
from scheduler_service import PersistentSchedulerService
import asyncio
import json
from pathlib import Path
import os
import hashlib
import sqlite3
from datetime import datetime
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # Generate a secure secret key
CORS(app, supports_credentials=True)  # Enable CORS with credentials

# Initialize trackers
tracker = StorenvyPriceTracker()
stock_tracker = StockPriceTracker()

# Initialize scheduler service
scheduler_service = PersistentSchedulerService()

# Initialize auth database
def init_auth_db():
    """Initialize authentication database"""
    conn = sqlite3.connect('storenvy_tracker.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT,
            smtp_password TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

init_auth_db()

# Helper function for password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

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

@app.route('/images/<path:filename>')
def image_files(filename):
    """Serve images from the frontend images directory"""
    frontend_images = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'images')
    return send_from_directory(frontend_images, filename)

# AUTH ROUTES
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """Create a new user account"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        smtp_password = data.get('smtp_password', '').strip()
        
        if not email or not password or not first_name:
            return jsonify({'error': 'Email, password, and first name are required'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        conn = sqlite3.connect('storenvy_tracker.db')
        cursor = conn.cursor()
        
        try:
            # Check if user already exists
            cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
            if cursor.fetchone():
                return jsonify({'error': 'User with this email already exists'}), 409
            
            # Create new user
            password_hash = hash_password(password)
            cursor.execute('''
                INSERT INTO users (email, password_hash, first_name, last_name, smtp_password)
                VALUES (?, ?, ?, ?, ?)
            ''', (email, password_hash, first_name, last_name, smtp_password))
            
            user_id = cursor.lastrowid
            conn.commit()
            
            # Set session
            session['user_id'] = user_id
            session['user_email'] = email
            session['user_name'] = first_name
            
            # Auto-start scheduler for new user
            if not scheduler_service.is_running():
                scheduler_service.start()
            
            return jsonify({
                'message': 'Account created successfully',
                'user': {
                    'id': user_id,
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name
                }
            }), 201
            
        except Exception as e:
            conn.rollback()
            print(f"Database error during signup: {e}")
            return jsonify({'error': 'Database error occurred'}), 500
        finally:
            conn.close()
            
    except Exception as e:
        print(f"Signup error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        conn = sqlite3.connect('storenvy_tracker.db')
        cursor = conn.cursor()
        
        try:
            password_hash = hash_password(password)
            cursor.execute('''
                SELECT id, email, first_name, last_name, smtp_password 
                FROM users 
                WHERE email = ? AND password_hash = ?
            ''', (email, password_hash))
            
            user = cursor.fetchone()
            
            if not user:
                return jsonify({'error': 'Invalid email or password'}), 401
            
            # Set session
            session['user_id'] = user[0]
            session['user_email'] = user[1]
            session['user_name'] = user[2]
            
            # Auto-start scheduler on login
            if not scheduler_service.is_running():
                scheduler_service.start()
            
            return jsonify({
                'message': 'Login successful',
                'user': {
                    'id': user[0],
                    'email': user[1],
                    'first_name': user[2],
                    'last_name': user[3],
                    'has_smtp': bool(user[4])
                }
            }), 200
            
        except Exception as e:
            print(f"Database error during login: {e}")
            return jsonify({'error': 'Database error occurred'}), 500
        finally:
            conn.close()
            
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout user"""
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/auth/session', methods=['GET'])
def check_session():
    """Check if user is logged in"""
    if 'user_id' in session:
        return jsonify({
            'logged_in': True,
            'user': {
                'id': session['user_id'],
                'email': session['user_email'],
                'first_name': session['user_name']
            }
        }), 200
    return jsonify({'logged_in': False}), 200

@app.route('/api/auth/update-smtp', methods=['POST'])
def update_smtp():
    """Update user's SMTP password"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        smtp_password = data.get('smtp_password', '').strip()
        
        if not smtp_password:
            return jsonify({'error': 'SMTP password is required'}), 400
        
        conn = sqlite3.connect('storenvy_tracker.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE users SET smtp_password = ? WHERE id = ?
            ''', (smtp_password, session['user_id']))
            
            conn.commit()
            return jsonify({'message': 'SMTP password updated successfully'}), 200
            
        except Exception as e:
            conn.rollback()
            print(f"Database error updating SMTP: {e}")
            return jsonify({'error': 'Database error occurred'}), 500
        finally:
            conn.close()
            
    except Exception as e:
        print(f"Update SMTP error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

# Helper to get user email config
def get_user_email_config():
    """Get email configuration for the logged-in user"""
    if 'user_id' not in session:
        return None
    
    conn = sqlite3.connect('storenvy_tracker.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT email, smtp_password FROM users WHERE id = ?
        ''', (session['user_id'],))
        
        user = cursor.fetchone()
        if user and user[1]:  # Has SMTP password
            return {
                'enabled': True,
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'from_email': user[0],
                'password': user[1],
                'to_email': user[0]
            }
        return None
        
    finally:
        conn.close()

# PRODUCT API ROUTES
@app.route('/api/products', methods=['GET'])
def get_products():
    """Get all tracked products"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    products = tracker.get_tracked_products(session['user_id'])
    return jsonify(products)

@app.route('/api/products', methods=['POST'])
def add_product():
    """Add a new product to track"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        url = data.get('url', '').strip()
        target_price = data.get('target_price')
        
        if not url or target_price is None:
            return jsonify({'error': 'URL and target price are required'}), 400
        
        try:
            target_price = float(target_price)
            if target_price <= 0:
                return jsonify({'error': 'Target price must be greater than 0'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid target price format'}), 400
        
        # Validate that the URL is from a supported platform
        platform = tracker.scraper.detect_platform(url)
        if not platform:
            return jsonify({'error': 'Unsupported platform. Please use Amazon, eBay, Etsy, Walmart, Storenvy, or Roblox.'}), 400
        
        tracker.add_product(url, target_price, session['user_id'])
        
        # Auto-start scheduler when first product is added
        if not scheduler_service.is_running():
            scheduler_service.start()
        
        return jsonify({'message': f'Product from {platform.title()} added successfully'}), 201
        
    except Exception as e:
        print(f"Add product error: {e}")
        return jsonify({'error': 'Failed to add product'}), 500

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a tracked product"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        tracker.delete_product(product_id, session['user_id'])
        return jsonify({'message': 'Product deleted successfully'}), 200
    except Exception as e:
        print(f"Delete product error: {e}")
        return jsonify({'error': 'Failed to delete product'}), 500

# STOCK API ROUTES
@app.route('/api/stocks', methods=['GET'])
def get_stock_alerts():
    """Get all stock alerts"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    alerts = stock_tracker.get_stock_alerts(session['user_id'])
    return jsonify(alerts)

@app.route('/api/stocks', methods=['POST'])
def add_stock_alert():
    """Add a new stock alert"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        symbol = data.get('symbol', '').upper().strip()
        alert_type = data.get('alert_type', '').strip()
        threshold = data.get('threshold')
        
        if not symbol or not alert_type or threshold is None:
            return jsonify({'error': 'Symbol, alert type, and threshold are required'}), 400
        
        # Validate alert type
        valid_alert_types = ['price_above', 'price_below', 'percent_up', 'percent_down']
        if alert_type not in valid_alert_types:
            return jsonify({'error': f'Invalid alert type. Must be one of: {valid_alert_types}'}), 400
        
        try:
            threshold = float(threshold)
            if threshold <= 0:
                return jsonify({'error': 'Threshold must be greater than 0'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid threshold format'}), 400
        
        stock_tracker.add_stock_alert(symbol, alert_type, threshold, session['user_id'])
        
        # Auto-start scheduler when first alert is added
        if not scheduler_service.is_running():
            scheduler_service.start()
        
        return jsonify({'message': f'Stock alert added for {symbol}'}), 201
        
    except Exception as e:
        print(f"Add stock alert error: {e}")
        return jsonify({'error': 'Failed to add stock alert'}), 500

@app.route('/api/stocks/<int:alert_id>', methods=['DELETE'])
def delete_stock_alert(alert_id):
    """Delete a stock alert"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        stock_tracker.delete_stock_alert(alert_id, session['user_id'])
        return jsonify({'message': 'Stock alert deleted successfully'}), 200
    except Exception as e:
        print(f"Delete stock alert error: {e}")
        return jsonify({'error': 'Failed to delete stock alert'}), 500

# STATISTICS ROUTES
@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get statistics about tracked products and stocks"""
    if 'user_id' not in session:
        return jsonify({
            'total_products': 0,
            'products_below_target': 0,
            'total_savings': 0,
            'total_stock_alerts': 0,
            'triggered_stock_alerts': 0,
            'monitoring_stock_alerts': 0
        })

    
    try:
        # Product stats
        products = tracker.get_tracked_products(session['user_id'])
        
        total_products = len(products)
        products_below_target = sum(1 for p in products if p.get('last_price') and p['last_price'] <= p['target_price'])
        total_savings = sum(p['target_price'] - p['last_price'] for p in products 
                           if p.get('last_price') and p['last_price'] <= p['target_price'])
        
        # Stock stats
        stock_stats = stock_tracker.get_stock_stats(session['user_id'])
        
        return jsonify({
            'total_products': total_products,
            'products_below_target': products_below_target,
            'total_savings': round(total_savings, 2),
            'total_stock_alerts': stock_stats['total_alerts'],
            'triggered_stock_alerts': stock_stats['triggered_alerts'],
            'monitoring_stock_alerts': stock_stats['monitoring_alerts']
        })
        
    except Exception as e:
        print(f"Stats error: {e}")
        return jsonify({
            'total_products': 0,
            'products_below_target': 0,
            'total_savings': 0,
            'total_stock_alerts': 0,
            'triggered_stock_alerts': 0,
            'monitoring_stock_alerts': 0
        })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🛍️  PRICETRACKER - PROFESSIONAL PRICE MONITORING")
    print("="*60)
    print("\n🚀 Web server starting...")
    print("🌐 Interface: http://localhost:5000")
    print("📦 E-commerce Products: Auto-check every 6 hours")
    print("🎮 Roblox Items: Auto-check every 6 hours")
    print("📈 Stocks: Auto-check every 5 minutes")
    print("\n⏹️  Press Ctrl+C to stop the web server")
    print("="*60 + "\n")
    
    try:
        app.run(debug=True, port=5000, host='0.0.0.0')
    finally:
        # Stop scheduler when app shuts down
        scheduler_service.stop()