// ===== CONTINUE WITH THE REST OF THE FUNCTIONS =====

function showAddProductModal() {
    document.getElementById('addProductModal').classList.add('show');
    document.getElementById('platformSelect').focus();
}

function closeAddProductModal() {
    document.getElementById('addProductModal').classList.remove('show');
    document.getElementById('addProductForm').reset();
    document.getElementById('productUrl').disabled = true;
    document.getElementById('productUrl').placeholder = 'Select a platform first...';
    document.getElementById('urlHint').textContent = '';
    document.getElementById('platformInfo').style.display = 'none';
}

function updateUrlPlaceholder() {
    const platformSelect = document.getElementById('platformSelect');
    const urlInput = document.getElementById('productUrl');
    const urlHint = document.getElementById('urlHint');
    const platformInfo = document.getElementById('platformInfo');
    const platformTips = document.getElementById('platformTips');
    
    const selectedPlatform = platformSelect.value;
    
    if (selectedPlatform && platformConfigs[selectedPlatform]) {
        const config = platformConfigs[selectedPlatform];
        urlInput.placeholder = config.exampleUrl;
        urlHint.textContent = `Example: ${config.exampleUrl}`;
        platformTips.textContent = config.tips;
        platformInfo.style.display = 'block';
        urlInput.disabled = false;
        urlInput.value = '';
    } else {
        urlInput.placeholder = 'Select a platform first...';
        urlHint.textContent = '';
        platformInfo.style.display = 'none';
        urlInput.disabled = true;
    }
}

async function addProduct(event) {
    event.preventDefault();
    
    const platform = document.getElementById('platformSelect').value;
    const url = document.getElementById('productUrl').value.trim();
    const targetPrice = parseFloat(document.getElementById('targetPrice').value);
    
    if (!platform) {
        showToast('Please select an e-commerce platform', 'error');
        return;
    }
    
    if (!url || !targetPrice || targetPrice <= 0) {
        showToast('Please enter a valid URL and target price', 'error');
        return;
    }
    
    if (!validatePlatformUrl(url, platform)) {
        showToast(`This URL doesn't appear to be from ${platformConfigs[platform].name}. Please check the URL and platform selection.`, 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/products`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ url, target_price: targetPrice })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            const platformName = platformConfigs[platform].name;
            showToast(`✅ ${platformName} product added successfully! Automatic monitoring has started.`);
            closeAddProductModal();
            loadProducts();
            loadStats();
        } else {
            showToast(data.error || 'Failed to add product', 'error');
        }
    } catch (error) {
        showToast('Network error: Failed to add product', 'error');
        console.error('Error adding product:', error);
    }
}

async function deleteProduct(productId) {
    if (!confirm('Are you sure you want to stop tracking this product?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/products/${productId}`, {
            method: 'DELETE',
            credentials: 'include',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (response.ok) {
            showToast('Product removed from tracking');
            loadProducts();
            loadStats();
        } else {
            const data = await response.json();
            showToast(data.error || 'Failed to remove product', 'error');
        }
    } catch (error) {
        showToast('Network error: Failed to remove product', 'error');
        console.error('Error deleting product:', error);
    }
}

// ===== ROBLOX MANAGEMENT =====
async function loadRobloxItems() {
    try {
        const response = await fetch(`${API_URL}/products`, {
            credentials: 'include',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                showAuth();
                return;
            }
            throw new Error('Failed to load Roblox items');
        }
        
        const allProducts = await response.json();
        
        // Filter for Roblox items only
        const robloxItems = allProducts.filter(product => product.platform === 'roblox');
        
        const robloxList = document.getElementById('robloxList');
        const emptyState = document.getElementById('robloxEmptyState');
        
        if (robloxItems.length === 0) {
            robloxList.style.display = 'none';
            emptyState.style.display = 'block';
        } else {
            robloxList.style.display = 'grid';
            emptyState.style.display = 'none';
            
            robloxList.innerHTML = robloxItems.map(item => `
                <div class="card" data-platform="roblox" id="roblox-${item.id}">
                    <div class="platform-badge">
                        <span>🎮</span>
                        <span style="font-weight: 500;">Roblox UGC</span>
                    </div>
                    <h3 class="card-title">${item.title || 'Loading item details...'}</h3>
                    <p class="card-subtitle">${truncateUrl(item.url)}</p>
                    
                    <div class="price-info">
                        <div class="price-item">
                            <span class="price-label">Current Price</span>
                            <span class="price-value robux" id="roblox-price-${item.id}">
                                ${item.last_price ? `${Math.round(item.last_price)} R : '--'}
                            </span>
                        </div>
                        <div class="price-item">
                            <span class="price-label">Target Price</span>
                            <span class="price-value robux">${Math.round(item.target_price)} R$</span>
                        </div>
                    </div>
                    
                    <div id="roblox-status-${item.id}">
                        ${renderProductStatus(item, 'roblox')}
                    </div>
                    
                    <div class="card-actions">
                        <a href="${item.url}" target="_blank" class="btn btn-primary btn-icon">
                            <i class="fas fa-external-link-alt"></i> View Item
                        </a>
                        <button onclick="deleteRobloxItem(${item.id})" class="btn btn-secondary btn-icon">
                            <i class="fas fa-trash"></i> Remove
                        </button>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        showToast('Failed to load Roblox items', 'error');
        console.error('Error loading Roblox items:', error);
    }
}

function showAddRobloxModal() {
    document.getElementById('addRobloxModal').classList.add('show');
    document.getElementById('robloxUrl').focus();
}

function closeAddRobloxModal() {
    document.getElementById('addRobloxModal').classList.remove('show');
    document.getElementById('addRobloxForm').reset();
}

async function addRobloxItem(event) {
    event.preventDefault();
    
    const url = document.getElementById('robloxUrl').value.trim();
    const targetPrice = parseInt(document.getElementById('robloxTargetPrice').value);
    
    if (!url || !targetPrice || targetPrice <= 0) {
        showToast('Please enter a valid Roblox URL and target price in Robux', 'error');
        return;
    }
    
    if (!validatePlatformUrl(url, 'roblox')) {
        showToast('This URL doesn\'t appear to be from Roblox. Please check the URL.', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/products`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ url, target_price: targetPrice })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('🎮 Roblox UGC item added successfully! Automatic monitoring has started.');
            closeAddRobloxModal();
            loadRobloxItems();
            loadStats();
        } else {
            showToast(data.error || 'Failed to add Roblox item', 'error');
        }
    } catch (error) {
        showToast('Network error: Failed to add Roblox item', 'error');
        console.error('Error adding Roblox item:', error);
    }
}

async function deleteRobloxItem(itemId) {
    if (!confirm('Are you sure you want to stop tracking this Roblox item?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/products/${itemId}`, {
            method: 'DELETE',
            credentials: 'include',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (response.ok) {
            showToast('Roblox item removed from tracking');
            loadRobloxItems();
            loadStats();
        } else {
            const data = await response.json();
            showToast(data.error || 'Failed to remove Roblox item', 'error');
        }
    } catch (error) {
        showToast('Network error: Failed to remove Roblox item', 'error');
        console.error('Error deleting Roblox item:', error);
    }
}

// ===== STOCK MANAGEMENT =====
async function loadStockAlerts() {
    try {
        const response = await fetch(`${API_URL}/stocks`, {
            credentials: 'include',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                showAuth();
                return;
            }
            throw new Error('Failed to load stock alerts');
        }
        
        const alerts = await response.json();
        
        const stocksList = document.getElementById('stocksList');
        const emptyState = document.getElementById('stocksEmptyState');
        
        if (alerts.length === 0) {
            stocksList.style.display = 'none';
            emptyState.style.display = 'block';
        } else {
            stocksList.style.display = 'grid';
            emptyState.style.display = 'none';
            
            stocksList.innerHTML = alerts.map(alert => `
                <div class="card" id="stock-${alert.id}">
                    <h3 class="card-title">
                        <i class="fas fa-chart-line"></i>
                        ${alert.company_name} (${alert.symbol})
                    </h3>
                    <p class="card-subtitle">${formatAlertDescription(alert)}</p>
                    
                    <div class="price-info">
                        <div class="price-item">
                            <span class="price-label">Current Price</span>
                            <span class="price-value" id="stock-price-${alert.id}">${alert.current_price ? alert.current_price.toFixed(2) : '--'}</span>
                        </div>
                        <div class="price-item">
                            <span class="price-label">Threshold</span>
                            <span class="price-value">${formatThreshold(alert)}</span>
                        </div>
                    </div>
                    
                    <div id="stock-status-${alert.id}">
                        ${renderStockStatus(alert)}
                    </div>
                    
                    <div class="card-actions">
                        <a href="https://finance.yahoo.com/quote/${alert.symbol}" target="_blank" class="btn btn-primary btn-icon">
                            <i class="fas fa-chart-line"></i> View Chart
                        </a>
                        <button onclick="deleteStockAlert(${alert.id})" class="btn btn-secondary btn-icon">
                            <i class="fas fa-trash"></i> Remove
                        </button>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        showToast('Failed to load stock alerts', 'error');
        console.error('Error loading stock alerts:', error);
    }
}

function formatAlertDescription(alert) {
    const alertDescriptions = {
        'price_above': `Alert when price rises above ${alert.threshold}`,
        'price_below': `Alert when price drops below ${alert.threshold}`,
        'percent_up': `Alert when price increases by ${alert.threshold}%`,
        'percent_down': `Alert when price decreases by ${alert.threshold}%`
    };
    return alertDescriptions[alert.alert_type] || 'Custom alert';
}

function formatThreshold(alert) {
    if (alert.alert_type.includes('percent')) {
        return `${alert.threshold}%`;
    }
    return `${alert.threshold.toFixed(2)}`;
}

function renderStockStatus(alert) {
    if (alert.is_triggered) {
        return `
            <div class="status-badge status-triggered">
                <i class="fas fa-bell"></i>
                Alert Triggered!
            </div>
        `;
    }
    
    if (!alert.current_price) {
        return `
            <div class="status-badge status-waiting">
                <i class="fas fa-clock"></i>
                Waiting for Data
            </div>
        `;
    }
    
    return `
        <div class="status-badge status-waiting">
            <i class="fas fa-eye"></i>
            Monitoring
        </div>
    `;
}

function showAddStockModal() {
    document.getElementById('addStockModal').classList.add('show');
    document.getElementById('stockSymbol').focus();
}

function closeAddStockModal() {
    document.getElementById('addStockModal').classList.remove('show');
    document.getElementById('addStockForm').reset();
    updateThresholdLabel();
}

function updateThresholdLabel() {
    const alertType = document.getElementById('alertType').value;
    const label = document.getElementById('thresholdLabel');
    const input = document.getElementById('alertThreshold');
    
    const labelConfig = {
        'price_above': { text: '💰 Price Threshold ($)', placeholder: '210.00', step: '0.01' },
        'price_below': { text: '💰 Price Threshold ($)', placeholder: '180.00', step: '0.01' },
        'percent_up': { text: '📈 Percentage Threshold (%)', placeholder: '5.0', step: '0.1' },
        'percent_down': { text: '📉 Percentage Threshold (%)', placeholder: '5.0', step: '0.1' }
    };
    
    const config = labelConfig[alertType] || { text: '🎯 Threshold', placeholder: '', step: '0.01' };
    
    label.innerHTML = config.text;
    input.placeholder = config.placeholder;
    input.step = config.step;
}

async function addStockAlert(event) {
    event.preventDefault();
    
    const symbol = document.getElementById('stockSymbol').value.toUpperCase().trim();
    const alertType = document.getElementById('alertType').value;
    const threshold = parseFloat(document.getElementById('alertThreshold').value);
    
    if (!symbol || !alertType || !threshold || threshold <= 0) {
        showToast('Please fill in all fields with valid values', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/stocks`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ 
                symbol: symbol, 
                alert_type: alertType, 
                threshold: threshold 
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast(`🚨 Stock alert created for ${symbol}! Automatic monitoring will notify you when conditions are met.`);
            closeAddStockModal();
            loadStock// frontend/js/app.js - FIXED VERSION WITH PROPER AUTHENTICATION
// TagTracker JavaScript - Complete Implementation with Auth

const API_URL = window.location.origin + '/api';  // Dynamic API URL based on current host

// User state
let currentUser = null;

// Platform configurations
const platformConfigs = {
    amazon: {
        name: 'Amazon',
        exampleUrl: 'https://www.amazon.com/dp/B08N5WRWNW',
        tips: 'Use the product URL from the address bar. Amazon URLs typically contain /dp/ or /gp/product/',
        icon: '🛒'
    },
    ebay: {
        name: 'eBay',
        exampleUrl: 'https://www.ebay.com/itm/123456789012',
        tips: 'Use the item URL that contains /itm/ followed by the item number',
        icon: '🏷️'
    },
    etsy: {
        name: 'Etsy',
        exampleUrl: 'https://www.etsy.com/listing/123456789/handmade-product-name',
        tips: 'Copy the listing URL that contains /listing/ followed by the listing ID',
        icon: '🎨'
    },
    walmart: {
        name: 'Walmart',
        exampleUrl: 'https://www.walmart.com/ip/Product-Name/123456789',
        tips: 'Walmart URLs contain /ip/ followed by the product name and ID',
        icon: '🏪'
    },
    storenvy: {
        name: 'Storenvy',
        exampleUrl: 'https://store-name.storenvy.com/products/123456-product-name',
        tips: 'Copy the full product URL from the product page',
        icon: '🏬'
    }
};

// Auto-refresh state
let autoRefreshInterval = null;

// ===== BACKEND CONNECTIVITY CHECK =====
async function checkBackendConnection() {
    try {
        console.log('Checking backend connection at:', API_URL);
        const response = await fetch(`${API_URL}/auth/session`, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        });
        
        console.log('Backend check response status:', response.status);
        
        if (!response.ok) {
            console.error('Backend returned non-OK status:', response.status);
            return false;
        }
        
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            console.error('Backend is not returning JSON, might be a 404 or server error');
            const responseText = await response.text();
            console.error('Response body:', responseText.substring(0, 200));
            showToast('Backend server issue: Please make sure you are running "python backend/app.py" and the server is accessible.', 'error');
            return false;
        }
        
        return true;
    } catch (error) {
        console.error('Backend connection failed:', error);
        showToast('Cannot connect to backend. Please start the Flask server with: python backend/app.py', 'error');
        return false;
    }
}

// ===== AUTH FUNCTIONS =====
async function checkSession() {
    try {
        // First check if backend is reachable
        const backendOk = await checkBackendConnection();
        if (!backendOk) {
            showAuth();
            return;
        }
        
        const response = await fetch(`${API_URL}/auth/session`, {
            credentials: 'include',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            console.error('Session check failed with status:', response.status);
            showAuth();
            return;
        }

        const data = await response.json();
        
        if (data.logged_in) {
            currentUser = data.user;
            console.log('User logged in:', currentUser);
            showApp();
        } else {
            console.log('User not logged in');
            showAuth();
        }
    } catch (error) {
        console.error('Session check failed:', error);
        showAuth();
    }
}

function showAuth() {
    document.getElementById('authContainer').style.display = 'flex';
    document.getElementById('appContainer').style.display = 'none';
    stopAutoRefresh();
}

function showApp() {
    document.getElementById('authContainer').style.display = 'none';
    document.getElementById('appContainer').style.display = 'block';
    
    // Update user name
    if (currentUser) {
        document.getElementById('userName').textContent = currentUser.first_name;
        document.getElementById('accountName').textContent = `${currentUser.first_name} ${currentUser.last_name || ''}`.trim();
        document.getElementById('accountEmail').textContent = currentUser.email;
    }
    
    // Load initial data
    loadProducts();
    loadStats();
    
    // Start auto-refresh
    startAutoRefresh();
}

function showLoginForm() {
    document.getElementById('loginForm').style.display = 'block';
    document.getElementById('signupForm').style.display = 'none';
    document.getElementById('loginEmail').focus();
}

function showSignupForm() {
    document.getElementById('signupForm').style.display = 'block';
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('signupFirstName').focus();
}

async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;
    
    // Validate fields
    if (!email || !password) {
        showToast('Please enter both email and password', 'error');
        return;
    }
    
    console.log('Attempting login for email:', email);
    
    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ email, password })
        });
        
        console.log('Login response status:', response.status);
        
        // Check if response is actually JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const responseText = await response.text();
            console.error('Non-JSON response received:', responseText.substring(0, 200));
            showToast('Server error: Backend is not responding with JSON. Please check if the Flask server is running correctly.', 'error');
            return;
        }
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = data.user;
            showToast('Welcome back, ' + currentUser.first_name + '!');
            showApp();
            document.getElementById('loginForm').querySelector('form').reset();
        } else {
            console.error('Login error response:', data);
            showToast(data.error || 'Login failed', 'error');
        }
    } catch (error) {
        console.error('Network error during login:', error);
        if (error.message.includes('JSON')) {
            showToast('Backend server error: Received HTML instead of JSON. Please ensure the Flask backend server is running properly on port 5000.', 'error');
        } else if (error.message.includes('fetch')) {
            showToast('Cannot connect to backend server. Please make sure the Flask app is running: python backend/app.py', 'error');
        } else {
            showToast(`Network error: ${error.message}`, 'error');
        }
    }
}

async function handleSignup(event) {
    event.preventDefault();
    
    const data = {
        first_name: document.getElementById('signupFirstName').value.trim(),
        last_name: document.getElementById('signupLastName').value.trim(),
        email: document.getElementById('signupEmail').value.trim(),
        password: document.getElementById('signupPassword').value,
        smtp_password: document.getElementById('signupSmtpPassword').value.trim()
    };
    
    // Validate required fields
    if (!data.first_name || !data.email || !data.password) {
        showToast('Please fill in all required fields', 'error');
        return;
    }
    
    if (data.password.length < 6) {
        showToast('Password must be at least 6 characters long', 'error');
        return;
    }
    
    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(data.email)) {
        showToast('Please enter a valid email address', 'error');
        return;
    }
    
    console.log('Attempting signup with data:', { ...data, password: '[HIDDEN]', smtp_password: '[HIDDEN]' });
    
    try {
        const response = await fetch(`${API_URL}/auth/signup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify(data)
        });
        
        console.log('Signup response status:', response.status);
        
        // Check if response is actually JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const responseText = await response.text();
            console.error('Non-JSON response received:', responseText.substring(0, 200));
            showToast('Server error: Backend is not responding with JSON. Please check if the Flask server is running correctly.', 'error');
            return;
        }
        
        const responseData = await response.json();
        
        if (response.ok) {
            currentUser = responseData.user;
            showToast('Welcome to PriceTracker, ' + currentUser.first_name + '!');
            showApp();
            document.getElementById('signupForm').querySelector('form').reset();
        } else {
            console.error('Signup error response:', responseData);
            showToast(responseData.error || 'Signup failed', 'error');
        }
    } catch (error) {
        console.error('Network error during signup:', error);
        if (error.message.includes('JSON')) {
            showToast('Backend server error: Received HTML instead of JSON. Please ensure the Flask backend server is running properly on port 5000.', 'error');
        } else if (error.message.includes('fetch')) {
            showToast('Cannot connect to backend server. Please make sure the Flask app is running: python backend/app.py', 'error');
        } else {
            showToast(`Network error: ${error.message}`, 'error');
        }
    }
}

async function handleLogout() {
    if (!confirm('Are you sure you want to sign out?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/auth/logout`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            currentUser = null;
            showAuth();
            showToast('Signed out successfully');
        }
    } catch (error) {
        showToast('Failed to sign out', 'error');
        console.error('Logout error:', error);
    }
}

// ===== PAGE MANAGEMENT =====
function showPage(pageId, navItem) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    // Show selected page
    document.getElementById(pageId).classList.add('active');
    
    // Update nav
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    navItem.classList.add('active');
    
    // Load page-specific data
    if (pageId === 'productsPage') {
        loadProducts();
        loadStats();
    } else if (pageId === 'robloxPage') {
        loadRobloxItems();
        loadStats();
    } else if (pageId === 'stocksPage') {
        loadStockAlerts();
        loadStats();
    } else if (pageId === 'settingsPage') {
        loadEmailConfig();
    }
}

// ===== AUTO-REFRESH FUNCTIONALITY =====
function startAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
    
    // Refresh data every 30 seconds
    autoRefreshInterval = setInterval(() => {
        loadStats();
        
        // Refresh current page data
        const activePage = document.querySelector('.page.active');
        if (activePage) {
            const pageId = activePage.id;
            if (pageId === 'productsPage') {
                loadProducts();
            } else if (pageId === 'robloxPage') {
                loadRobloxItems();
            } else if (pageId === 'stocksPage') {
                loadStockAlerts();
            }
        }
    }, 30000); // 30 seconds
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

// ===== TOAST NOTIFICATIONS =====
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}

// ===== UTILITY FUNCTIONS =====
function truncateUrl(url) {
    if (url.length <= 50) return url;
    return url.substring(0, 47) + '...';
}

function formatPrice(price, platform) {
    if (platform === 'roblox') {
        return `${Math.round(price)} R// frontend/js/app.js - FIXED VERSION WITH PROPER AUTHENTICATION
// TagTracker JavaScript - Complete Implementation with Auth

const API_URL = window.location.origin + '/api';  // Dynamic API URL based on current host

// User state
let currentUser = null;

// Platform configurations
const platformConfigs = {
    amazon: {
        name: 'Amazon',
        exampleUrl: 'https://www.amazon.com/dp/B08N5WRWNW',
        tips: 'Use the product URL from the address bar. Amazon URLs typically contain /dp/ or /gp/product/',
        icon: '🛒'
    },
    ebay: {
        name: 'eBay',
        exampleUrl: 'https://www.ebay.com/itm/123456789012',
        tips: 'Use the item URL that contains /itm/ followed by the item number',
        icon: '🏷️'
    },
    etsy: {
        name: 'Etsy',
        exampleUrl: 'https://www.etsy.com/listing/123456789/handmade-product-name',
        tips: 'Copy the listing URL that contains /listing/ followed by the listing ID',
        icon: '🎨'
    },
    walmart: {
        name: 'Walmart',
        exampleUrl: 'https://www.walmart.com/ip/Product-Name/123456789',
        tips: 'Walmart URLs contain /ip/ followed by the product name and ID',
        icon: '🏪'
    },
    storenvy: {
        name: 'Storenvy',
        exampleUrl: 'https://store-name.storenvy.com/products/123456-product-name',
        tips: 'Copy the full product URL from the product page',
        icon: '🏬'
    }
};

// Auto-refresh state
let autoRefreshInterval = null;

// ===== BACKEND CONNECTIVITY CHECK =====
async function checkBackendConnection() {
    try {
        console.log('Checking backend connection at:', API_URL);
        const response = await fetch(`${API_URL}/auth/session`, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        });
        
        console.log('Backend check response status:', response.status);
        
        if (!response.ok) {
            console.error('Backend returned non-OK status:', response.status);
            return false;
        }
        
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            console.error('Backend is not returning JSON, might be a 404 or server error');
            const responseText = await response.text();
            console.error('Response body:', responseText.substring(0, 200));
            showToast('Backend server issue: Please make sure you are running "python backend/app.py" and the server is accessible.', 'error');
            return false;
        }
        
        return true;
    } catch (error) {
        console.error('Backend connection failed:', error);
        showToast('Cannot connect to backend. Please start the Flask server with: python backend/app.py', 'error');
        return false;
    }
}

// ===== AUTH FUNCTIONS =====
async function checkSession() {
    try {
        // First check if backend is reachable
        const backendOk = await checkBackendConnection();
        if (!backendOk) {
            showAuth();
            return;
        }
        
        const response = await fetch(`${API_URL}/auth/session`, {
            credentials: 'include',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            console.error('Session check failed with status:', response.status);
            showAuth();
            return;
        }

        const data = await response.json();
        
        if (data.logged_in) {
            currentUser = data.user;
            console.log('User logged in:', currentUser);
            showApp();
        } else {
            console.log('User not logged in');
            showAuth();
        }
    } catch (error) {
        console.error('Session check failed:', error);
        showAuth();
    }
}

function showAuth() {
    document.getElementById('authContainer').style.display = 'flex';
    document.getElementById('appContainer').style.display = 'none';
    stopAutoRefresh();
}

function showApp() {
    document.getElementById('authContainer').style.display = 'none';
    document.getElementById('appContainer').style.display = 'block';
    
    // Update user name
    if (currentUser) {
        document.getElementById('userName').textContent = currentUser.first_name;
        document.getElementById('accountName').textContent = `${currentUser.first_name} ${currentUser.last_name || ''}`.trim();
        document.getElementById('accountEmail').textContent = currentUser.email;
    }
    
    // Load initial data
    loadProducts();
    loadStats();
    
    // Start auto-refresh
    startAutoRefresh();
}

function showLoginForm() {
    document.getElementById('loginForm').style.display = 'block';
    document.getElementById('signupForm').style.display = 'none';
    document.getElementById('loginEmail').focus();
}

function showSignupForm() {
    document.getElementById('signupForm').style.display = 'block';
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('signupFirstName').focus();
}

async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;
    
    // Validate fields
    if (!email || !password) {
        showToast('Please enter both email and password', 'error');
        return;
    }
    
    console.log('Attempting login for email:', email);
    
    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ email, password })
        });
        
        console.log('Login response status:', response.status);
        
;
    }
    return `${price.toFixed(2)}`;
}

function validatePlatformUrl(url, platform) {
    const domainPatterns = {
        amazon: /amazon\.(com|co\.uk|ca|de|fr|es|it|jp|in|com\.mx|com\.br)/i,
        ebay: /ebay\.(com|co\.uk|ca|de|fr|it|es|com\.au)/i,
        etsy: /etsy\.com/i,
        walmart: /walmart\.com/i,
        storenvy: /storenvy\.com/i,
        roblox: /roblox\.com/i
    };
    
    if (!platform || !domainPatterns[platform]) {
        return false;
    }
    
    return domainPatterns[platform].test(url);
}

// ===== SHARED FUNCTIONS =====
function renderProductStatus(product, platform = null) {
    if (!product.last_price) {
        return `
            <div class="status-badge status-waiting">
                <i class="fas fa-clock"></i>
                Not Checked Yet
            </div>
        `;
    }
    
    if (product.status === 'below_target') {
        const savings = product.target_price - product.last_price;
        let savingsText;
        let emoji;
        
        if (platform === 'roblox') {
            savingsText = `${Math.round(savings)} R// frontend/js/app.js - FIXED VERSION WITH PROPER AUTHENTICATION
// TagTracker JavaScript - Complete Implementation with Auth

const API_URL = window.location.origin + '/api';  // Dynamic API URL based on current host

// User state
let currentUser = null;

// Platform configurations
const platformConfigs = {
    amazon: {
        name: 'Amazon',
        exampleUrl: 'https://www.amazon.com/dp/B08N5WRWNW',
        tips: 'Use the product URL from the address bar. Amazon URLs typically contain /dp/ or /gp/product/',
        icon: '🛒'
    },
    ebay: {
        name: 'eBay',
        exampleUrl: 'https://www.ebay.com/itm/123456789012',
        tips: 'Use the item URL that contains /itm/ followed by the item number',
        icon: '🏷️'
    },
    etsy: {
        name: 'Etsy',
        exampleUrl: 'https://www.etsy.com/listing/123456789/handmade-product-name',
        tips: 'Copy the listing URL that contains /listing/ followed by the listing ID',
        icon: '🎨'
    },
    walmart: {
        name: 'Walmart',
        exampleUrl: 'https://www.walmart.com/ip/Product-Name/123456789',
        tips: 'Walmart URLs contain /ip/ followed by the product name and ID',
        icon: '🏪'
    },
    storenvy: {
        name: 'Storenvy',
        exampleUrl: 'https://store-name.storenvy.com/products/123456-product-name',
        tips: 'Copy the full product URL from the product page',
        icon: '🏬'
    }
};

// Auto-refresh state
let autoRefreshInterval = null;

// ===== BACKEND CONNECTIVITY CHECK =====
async function checkBackendConnection() {
    try {
        console.log('Checking backend connection at:', API_URL);
        const response = await fetch(`${API_URL}/auth/session`, {
            method: 'GET',
            credentials: 'include',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        });
        
        console.log('Backend check response status:', response.status);
        
        if (!response.ok) {
            console.error('Backend returned non-OK status:', response.status);
            return false;
        }
        
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            console.error('Backend is not returning JSON, might be a 404 or server error');
            const responseText = await response.text();
            console.error('Response body:', responseText.substring(0, 200));
            showToast('Backend server issue: Please make sure you are running "python backend/app.py" and the server is accessible.', 'error');
            return false;
        }
        
        return true;
    } catch (error) {
        console.error('Backend connection failed:', error);
        showToast('Cannot connect to backend. Please start the Flask server with: python backend/app.py', 'error');
        return false;
    }
}

// ===== AUTH FUNCTIONS =====
async function checkSession() {
    try {
        // First check if backend is reachable
        const backendOk = await checkBackendConnection();
        if (!backendOk) {
            showAuth();
            return;
        }
        
        const response = await fetch(`${API_URL}/auth/session`, {
            credentials: 'include',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            console.error('Session check failed with status:', response.status);
            showAuth();
            return;
        }

        const data = await response.json();
        
        if (data.logged_in) {
            currentUser = data.user;
            console.log('User logged in:', currentUser);
            showApp();
        } else {
            console.log('User not logged in');
            showAuth();
        }
    } catch (error) {
        console.error('Session check failed:', error);
        showAuth();
    }
}

function showAuth() {
    document.getElementById('authContainer').style.display = 'flex';
    document.getElementById('appContainer').style.display = 'none';
    stopAutoRefresh();
}

function showApp() {
    document.getElementById('authContainer').style.display = 'none';
    document.getElementById('appContainer').style.display = 'block';
    
    // Update user name
    if (currentUser) {
        document.getElementById('userName').textContent = currentUser.first_name;
        document.getElementById('accountName').textContent = `${currentUser.first_name} ${currentUser.last_name || ''}`.trim();
        document.getElementById('accountEmail').textContent = currentUser.email;
    }
    
    // Load initial data
    loadProducts();
    loadStats();
    
    // Start auto-refresh
    startAutoRefresh();
}

function showLoginForm() {
    document.getElementById('loginForm').style.display = 'block';
    document.getElementById('signupForm').style.display = 'none';
    document.getElementById('loginEmail').focus();
}

function showSignupForm() {
    document.getElementById('signupForm').style.display = 'block';
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('signupFirstName').focus();
}

async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;
    
    // Validate fields
    if (!email || !password) {
        showToast('Please enter both email and password', 'error');
        return;
    }
    
    console.log('Attempting login for email:', email);
    
    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ email, password })
        });
        
        console.log('Login response status:', response.status);
        
;
            emoji = '🎮';
        } else {
            savingsText = `${savings.toFixed(2)}`;
            emoji = '💰';
        }
        
        return `
            <div class="status-badge status-triggered">
                <i class="fas fa-check-circle"></i>
                ${emoji} Target Hit! Save ${savingsText}
            </div>
        `;
    }
    
    let statusText = 'Monitoring Price';
    if (platform === 'roblox') {
        statusText = 'Watching Robux Price';
    }
    
    return `
        <div class="status-badge status-waiting">
            <i class="fas fa-eye"></i>
            ${statusText}
        </div>
    `;
}

// ===== PRODUCTS MANAGEMENT (Amazon, eBay, Etsy, Walmart, Storenvy) =====
async function loadProducts() {
    try {
        const response = await fetch(`${API_URL}/products`, {
            credentials: 'include',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                showAuth();
                return;
            }
            throw new Error('Failed to load products');
        }
        
        const allProducts = await response.json();
        
        // Filter for e-commerce platforms only
        const ecommerceProducts = allProducts.filter(product => 
            ['amazon', 'ebay', 'etsy', 'walmart', 'storenvy'].includes(product.platform)
        );
        
        const productsList = document.getElementById('productsList');
        const emptyState = document.getElementById('emptyState');
        
        if (ecommerceProducts.length === 0) {
            productsList.style.display = 'none';
            emptyState.style.display = 'block';
        } else {
            productsList.style.display = 'grid';
            emptyState.style.display = 'none';
            
            productsList.innerHTML = ecommerceProducts.map(product => {
                const platform = product.platform || 'storenvy';
                const config = platformConfigs[platform] || {};
                
                return `
                <div class="card" data-platform="${platform}" id="product-${product.id}">
                    <div class="platform-badge">
                        <span>${product.platform_icon || config.icon || '🛒'}</span>
                        <span style="font-weight: 500;">${product.platform_name || config.name || 'Unknown'}</span>
                    </div>
                    <h3 class="card-title">${product.title || 'Loading product details...'}</h3>
                    <p class="card-subtitle">${truncateUrl(product.url)}</p>
                    
                    <div class="price-info">
                        <div class="price-item">
                            <span class="price-label">Current Price</span>
                            <span class="price-value" id="current-price-${product.id}">
                                ${product.last_price ? formatPrice(product.last_price, platform) : '--'}
                            </span>
                        </div>
                        <div class="price-item">
                            <span class="price-label">Target Price</span>
                            <span class="price-value">${formatPrice(product.target_price, platform)}</span>
                        </div>
                    </div>
                    
                    <div id="status-${product.id}">
                        ${renderProductStatus(product, platform)}
                    </div>
                    
                    <div class="card-actions">
                        <a href="${product.url}" target="_blank" class="btn btn-primary btn-icon">
                            <i class="fas fa-external-link-alt"></i> View Product
                        </a>
                        <button onclick="deleteProduct(${product.id})" class="btn btn-secondary btn-icon">
                            <i class="fas fa-trash"></i> Remove
                        </button>
                    </div>
                </div>
            `;
            }).join('');
        }
    } catch (error) {
        showToast('Failed to load products', 'error');
        console.error('Error loading products:', error);
    }
}

// Check if response is actually JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const responseText = await response.text();
            console.error('Non-JSON response received:', responseText.substring(0, 200));
            showToast('Server error: Backend is not responding with JSON. Please check if the Flask server is running correctly.', 'error');
            return;
        }
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = data.user;
            showToast('Welcome back, ' + currentUser.first_name + '!');
            showApp();
            document.getElementById('loginForm').querySelector('form').reset();
        } else {
            console.error('Login error response:', data);
            showToast(data.error || 'Login failed', 'error');
        }
    } catch (error) {
        console.error('Network error during login:', error);
        if (error.message.includes('JSON')) {
            showToast('Backend server error: Received HTML instead of JSON. Please ensure the Flask backend server is running properly on port 5000.', 'error');
        } else if (error.message.includes('fetch')) {
            showToast('Cannot connect to backend server. Please make sure the Flask app is running: python backend/app.py', 'error');
        } else {
            showToast(`Network error: ${error.message}`, 'error');
        }
    }
}

async function handleSignup(event) {
    event.preventDefault();
    
    const data = {
        first_name: document.getElementById('signupFirstName').value.trim(),
        last_name: document.getElementById('signupLastName').value.trim(),
        email: document.getElementById('signupEmail').value.trim(),
        password: document.getElementById('signupPassword').value,
        smtp_password: document.getElementById('signupSmtpPassword').value.trim()
    };
    
    // Validate required fields
    if (!data.first_name || !data.email || !data.password) {
        showToast('Please fill in all required fields', 'error');
        return;
    }
    
    if (data.password.length < 6) {
        showToast('Password must be at least 6 characters long', 'error');
        return;
    }
    
    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(data.email)) {
        showToast('Please enter a valid email address', 'error');
        return;
    }
    
    console.log('Attempting signup with data:', { ...data, password: '[HIDDEN]', smtp_password: '[HIDDEN]' });
    
    try {
        const response = await fetch(`${API_URL}/auth/signup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify(data)
        });
        
        console.log('Signup response status:', response.status);
        
        // Check if response is actually JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const responseText = await response.text();
            console.error('Non-JSON response received:', responseText.substring(0, 200));
            showToast('Server error: Backend is not responding with JSON. Please check if the Flask server is running correctly.', 'error');
            return;
        }
        
        const responseData = await response.json();
        
        if (response.ok) {
            currentUser = responseData.user;
            showToast('Welcome to PriceTracker, ' + currentUser.first_name + '!');
            showApp();
            document.getElementById('signupForm').querySelector('form').reset();
        } else {
            console.error('Signup error response:', responseData);
            showToast(responseData.error || 'Signup failed', 'error');
        }
    } catch (error) {
        console.error('Network error during signup:', error);
        if (error.message.includes('JSON')) {
            showToast('Backend server error: Received HTML instead of JSON. Please ensure the Flask backend server is running properly on port 5000.', 'error');
        } else if (error.message.includes('fetch')) {
            showToast('Cannot connect to backend server. Please make sure the Flask app is running: python backend/app.py', 'error');
        } else {
            showToast(`Network error: ${error.message}`, 'error');
        }
    }
}

async function handleLogout() {
    if (!confirm('Are you sure you want to sign out?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/auth/logout`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            currentUser = null;
            showAuth();
            showToast('Signed out successfully');
        }
    } catch (error) {
        showToast('Failed to sign out', 'error');
        console.error('Logout error:', error);
    }
}

// ===== PAGE MANAGEMENT =====
function showPage(pageId, navItem) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    
    // Show selected page
    document.getElementById(pageId).classList.add('active');
    
    // Update nav
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    navItem.classList.add('active');
    
    // Load page-specific data
    if (pageId === 'productsPage') {
        loadProducts();
        loadStats();
    } else if (pageId === 'robloxPage') {
        loadRobloxItems();
        loadStats();
    } else if (pageId === 'stocksPage') {
        loadStockAlerts();
        loadStats();
    } else if (pageId === 'settingsPage') {
        loadEmailConfig();
    }
}

// ===== AUTO-REFRESH FUNCTIONALITY =====
function startAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
    
    // Refresh data every 30 seconds
    autoRefreshInterval = setInterval(() => {
        loadStats();
        
        // Refresh current page data
        const activePage = document.querySelector('.page.active');
        if (activePage) {
            const pageId = activePage.id;
            if (pageId === 'productsPage') {
                loadProducts();
            } else if (pageId === 'robloxPage') {
                loadRobloxItems();
            } else if (pageId === 'stocksPage') {
                loadStockAlerts();
            }
        }
    }, 30000); // 30 seconds
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

// ===== STATS LOADING =====
async function loadStats() {
    try {
        const response = await fetch(`${API_URL}/stats`, {
            credentials: 'include',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                showAuth();
                return;
            }
            throw new Error('Failed to load stats');
        }
        
        const stats = await response.json();
        
        // Count products by type
        const productsResponse = await fetch(`${API_URL}/products`, {
            credentials: 'include',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (productsResponse.ok) {
            const allProducts = await productsResponse.json();
            const ecommerceCount = allProducts.filter(p => 
                ['amazon', 'ebay', 'etsy', 'walmart', 'storenvy'].includes(p.platform)
            ).length;
            const robloxCount = allProducts.filter(p => p.platform === 'roblox').length;
            
            document.getElementById('totalProducts').textContent = ecommerceCount;
            document.getElementById('totalRobloxItems').textContent = robloxCount;
        }
        
        document.getElementById('totalStockAlerts').textContent = stats.total_stock_alerts || 0;
        document.getElementById('totalSavings').textContent = (stats.total_savings || 0).toFixed(2);
        
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

// ===== TOAST NOTIFICATIONS =====
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}

// ===== UTILITY FUNCTIONS =====
function truncateUrl(url) {
    if (url.length <= 50) return url;
    return url.substring(0, 47) + '...';
}

function formatPrice(price, platform) {
    if (platform === 'roblox') {
        return `${Math.round(price)} R$`;
    }
    return `$${price.toFixed(2)}`;
}

function validatePlatformUrl(url, platform) {
    const domainPatterns = {
        amazon: /amazon\.(com|co\.uk|ca|de|fr|es|it|jp|in|com\.mx|com\.br)/i,
        ebay: /ebay\.(com|co\.uk|ca|de|fr|it|es|com\.au)/i,
        etsy: /etsy\.com/i,
        walmart: /walmart\.com/i,
        storenvy: /storenvy\.com/i,
        roblox: /roblox\.com/i
    };
    
    if (!platform || !domainPatterns[platform]) {
        return false;
    }
    
    return domainPatterns[platform].test(url);
}

// ===== SHARED FUNCTIONS =====
function renderProductStatus(product, platform = null) {
    if (!product.last_price) {
        return `
            <div class="status-badge status-waiting">
                <i class="fas fa-clock"></i>
                Not Checked Yet
            </div>
        `;
    }
    
    if (product.status === 'below_target') {
        const savings = product.target_price - product.last_price;
        let savingsText;
        let emoji;
        
        if (platform === 'roblox') {
            savingsText = `${Math.round(savings)} R$`;
            emoji = '🎮';
        } else {
            savingsText = `$${savings.toFixed(2)}`;
            emoji = '💰';
        }
        
        return `
            <div class="status-badge status-triggered">
                <i class="fas fa-check-circle"></i>
                ${emoji} Target Hit! Save ${savingsText}
            </div>
        `;
    }
    
    let statusText = 'Monitoring Price';
    if (platform === 'roblox') {
        statusText = 'Watching Robux Price';
    }
    
    return `
        <div class="status-badge status-waiting">
            <i class="fas fa-eye"></i>
            ${statusText}
        </div>
    `;
}

// ===== PRODUCTS MANAGEMENT (Amazon, eBay, Etsy, Walmart, Storenvy) =====
async function loadProducts() {
    try {
        const response = await fetch(`${API_URL}/products`, {
            credentials: 'include',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                showAuth();
                return;
            }
            throw new Error('Failed to load products');
        }
        
        const allProducts = await response.json();
        
        // Filter for e-commerce platforms only
        const ecommerceProducts = allProducts.filter(product => 
            ['amazon', 'ebay', 'etsy', 'walmart', 'storenvy'].includes(product.platform)
        );
        
        const productsList = document.getElementById('productsList');
        const emptyState = document.getElementById('emptyState');
        
        if (ecommerceProducts.length === 0) {
            productsList.style.display = 'none';
            emptyState.style.display = 'block';
        } else {
            productsList.style.display = 'grid';
            emptyState.style.display = 'none';
            
            productsList.innerHTML = ecommerceProducts.map(product => {
                const platform = product.platform || 'storenvy';
                const config = platformConfigs[platform] || {};
                
                return `
                <div class="card" data-platform="${platform}" id="product-${product.id}">
                    <div class="platform-badge">
                        <span>${product.platform_icon || config.icon || '🛒'}</span>
                        <span style="font-weight: 500;">${product.platform_name || config.name || 'Unknown'}</span>
                    </div>
                    <h3 class="card-title">${product.title || 'Loading product details...'}</h3>
                    <p class="card-subtitle">${truncateUrl(product.url)}</p>
                    
                    <div class="price-info">
                        <div class="price-item">
                            <span class="price-label">Current Price</span>
                            <span class="price-value" id="current-price-${product.id}">
                                ${product.last_price ? formatPrice(product.last_price, platform) : '--'}
                            </span>
                        </div>
                        <div class="price-item">
                            <span class="price-label">Target Price</span>
                            <span class="price-value">${formatPrice(product.target_price, platform)}</span>
                        </div>
                    </div>
                    
                    <div id="status-${product.id}">
                        ${renderProductStatus(product, platform)}
                    </div>
                    
                    <div class="card-actions">
                        <a href="${product.url}" target="_blank" class="btn btn-primary btn-icon">
                            <i class="fas fa-external-link-alt"></i> View Product
                        </a>
                        <button onclick="deleteProduct(${product.id})" class="btn btn-secondary btn-icon">
                            <i class="fas fa-trash"></i> Remove
                        </button>
                    </div>
                </div>
            `;
            }).join('');
        }
    } catch (error) {
        showToast('Failed to load products', 'error');
        console.error('Error loading products:', error);
    }
}

function showAddProductModal() {
    document.getElementById('addProductModal').classList.add('show');
    document.getElementById('platformSelect').focus();
}

function closeAddProductModal() {
    document.getElementById('addProductModal').classList.remove('show');
    document.getElementById('addProductForm').reset();
    document.getElementById('productUrl').disabled = true;
    document.getElementById('productUrl').placeholder = 'Select a platform first...';
    document.getElementById('urlHint').textContent = '';
    document.getElementById('platformInfo').style.display = 'none';
}

function updateUrlPlaceholder() {
    const platformSelect = document.getElementById('platformSelect');
    const urlInput = document.getElementById('productUrl');
    const urlHint = document.getElementById('urlHint');
    const platformInfo = document.getElementById('platformInfo');
    const platformTips = document.getElementById('platformTips');
    
    const selectedPlatform = platformSelect.value;
    
    if (selectedPlatform && platformConfigs[selectedPlatform]) {
        const config = platformConfigs[selectedPlatform];
        urlInput.placeholder = config.exampleUrl;
        urlHint.textContent = `Example: ${config.exampleUrl}`;
        platformTips.textContent = config.tips;
        platformInfo.style.display = 'block';
        urlInput.disabled = false;
        urlInput.value = '';
    } else {
        urlInput.placeholder = 'Select a platform first...';
        urlHint.textContent = '';
        platformInfo.style.display = 'none';
        urlInput.disabled = true;
    }
}

async function addProduct(event) {
    event.preventDefault();
    
    const platform = document.getElementById('platformSelect').value;
    const url = document.getElementById('productUrl').value.trim();
    const targetPrice = parseFloat(document.getElementById('targetPrice').value);
    
    if (!platform) {
        showToast('Please select an e-commerce platform', 'error');
        return;
    }
    
    if (!url || !targetPrice || targetPrice <= 0) {
        showToast('Please enter a valid URL and target price', 'error');
        return;
    }
    
    if (!validatePlatformUrl(url, platform)) {
        showToast(`This URL doesn't appear to be from ${platformConfigs[platform].name}. Please check the URL and platform selection.`, 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/products`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ url, target_price: targetPrice })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            const platformName = platformConfigs[platform].name;
            showToast(`✅ ${platformName} product added successfully! Automatic monitoring has started.`);
            closeAddProductModal();
            loadProducts();
            loadStats();
        } else {
            showToast(data.error || 'Failed to add product', 'error');
        }
    } catch (error) {
        showToast('Network error: Failed to add product', 'error');
        console.error('Error adding product:', error);
    }
}

async function deleteProduct(productId) {
    if (!confirm('Are you sure you want to stop tracking this product?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/products/${productId}`, {
            method: 'DELETE',
            credentials: 'include',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (response.ok) {
            showToast('Product removed from tracking');
            loadProducts();
            loadStats();
        } else {
            const data = await response.json();
            showToast(data.error || 'Failed to remove product', 'error');
        }
    } catch (error) {
        showToast('Network error: Failed to remove product', 'error');
        console.error('Error deleting product:', error);
    }
}

// ===== ROBLOX MANAGEMENT =====
async function loadRobloxItems() {
    try {
        const response = await fetch(`${API_URL}/products`, {
            credentials: 'include',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                showAuth();
                return;
            }
            throw new Error('Failed to load Roblox items');
        }
        
        const allProducts = await response.json();
        
        // Filter for Roblox items only
        const robloxItems = allProducts.filter(product => product.platform === 'roblox');
        
        const robloxList = document.getElementById('robloxList');
        const emptyState = document.getElementById('robloxEmptyState');
        
        if (robloxItems.length === 0) {
            robloxList.style.display = 'none';
            emptyState.style.display = 'block';
        } else {
            robloxList.style.display = 'grid';
            emptyState.style.display = 'none';
            
            robloxList.innerHTML = robloxItems.map(item => `
                <div class="card" data-platform="roblox" id="roblox-${item.id}">
                    <div class="platform-badge">
                        <span>🎮</span>
                        <span style="font-weight: 500;">Roblox UGC</span>
                    </div>
                    <h3 class="card-title">${item.title || 'Loading item details...'}</h3>
                    <p class="card-subtitle">${truncateUrl(item.url)}</p>
                    
                    <div class="price-info">
                        <div class="price-item">
                            <span class="price-label">Current Price</span>
                            <span class="price-value robux" id="roblox-price-${item.id}">
                                ${item.last_price ? `${Math.round(item.last_price)} R$` : '--'}
                            </span>
                        </div>
                        <div class="price-item">
                            <span class="price-label">Target Price</span>
                            <span class="price-value robux">${Math.round(item.target_price)} R$</span>
                        </div>
                    </div>
                    
                    <div id="roblox-status-${item.id}">
                        ${renderProductStatus(item, 'roblox')}
                    </div>
                    
                    <div class="card-actions">
                        <a href="${item.url}" target="_blank" class="btn btn-primary btn-icon">
                            <i class="fas fa-external-link-alt"></i> View Item
                        </a>
                        <button onclick="deleteRobloxItem(${item.id})" class="btn btn-secondary btn-icon">
                            <i class="fas fa-trash"></i> Remove
                        </button>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        showToast('Failed to load Roblox items', 'error');
        console.error('Error loading Roblox items:', error);
    }
}

function showAddRobloxModal() {
    document.getElementById('addRobloxModal').classList.add('show');
    document.getElementById('robloxUrl').focus();
}

function closeAddRobloxModal() {
    document.getElementById('addRobloxModal').classList.remove('show');
    document.getElementById('addRobloxForm').reset();
}

async function addRobloxItem(event) {
    event.preventDefault();
    
    const url = document.getElementById('robloxUrl').value.trim();
    const targetPrice = parseInt(document.getElementById('robloxTargetPrice').value);
    
    if (!url || !targetPrice || targetPrice <= 0) {
        showToast('Please enter a valid Roblox URL and target price in Robux', 'error');
        return;
    }
    
    if (!validatePlatformUrl(url, 'roblox')) {
        showToast('This URL doesn\'t appear to be from Roblox. Please check the URL.', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/products`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ url, target_price: targetPrice })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('🎮 Roblox UGC item added successfully! Automatic monitoring has started.');
            closeAddRobloxModal();
            loadRobloxItems();
            loadStats();
        } else {
            showToast(data.error || 'Failed to add Roblox item', 'error');
        }
    } catch (error) {
        showToast('Network error: Failed to add Roblox item', 'error');
        console.error('Error adding Roblox item:', error);
    }
}

async function deleteRobloxItem(itemId) {
    if (!confirm('Are you sure you want to stop tracking this Roblox item?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/products/${itemId}`, {
            method: 'DELETE',
            credentials: 'include',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (response.ok) {
            showToast('Roblox item removed from tracking');
            loadRobloxItems();
            loadStats();
        } else {
            const data = await response.json();
            showToast(data.error || 'Failed to remove Roblox item', 'error');
        }
    } catch (error) {
        showToast('Network error: Failed to remove Roblox item', 'error');
        console.error('Error deleting Roblox item:', error);
    }
}

// ===== STOCK MANAGEMENT =====
async function loadStockAlerts() {
    try {
        const response = await fetch(`${API_URL}/stocks`, {
            credentials: 'include',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                showAuth();
                return;
            }
            throw new Error('Failed to load stock alerts');
        }
        
        const alerts = await response.json();
        
        const stocksList = document.getElementById('stocksList');
        const emptyState = document.getElementById('stocksEmptyState');
        
        if (alerts.length === 0) {
            stocksList.style.display = 'none';
            emptyState.style.display = 'block';
        } else {
            stocksList.style.display = 'grid';
            emptyState.style.display = 'none';
            
            stocksList.innerHTML = alerts.map(alert => `
                <div class="card" id="stock-${alert.id}">
                    <h3 class="card-title">
                        <i class="fas fa-chart-line"></i>
                        ${alert.company_name} (${alert.symbol})
                    </h3>
                    <p class="card-subtitle">${formatAlertDescription(alert)}</p>
                    
                    <div class="price-info">
                        <div class="price-item">
                            <span class="price-label">Current Price</span>
                            <span class="price-value" id="stock-price-${alert.id}">$${alert.current_price ? alert.current_price.toFixed(2) : '--'}</span>
                        </div>
                        <div class="price-item">
                            <span class="price-label">Threshold</span>
                            <span class="price-value">${formatThreshold(alert)}</span>
                        </div>
                    </div>
                    
                    <div id="stock-status-${alert.id}">
                        ${renderStockStatus(alert)}
                    </div>
                    
                    <div class="card-actions">
                        <a href="https://finance.yahoo.com/quote/${alert.symbol}" target="_blank" class="btn btn-primary btn-icon">
                            <i class="fas fa-chart-line"></i> View Chart
                        </a>
                        <button onclick="deleteStockAlert(${alert.id})" class="btn btn-secondary btn-icon">
                            <i class="fas fa-trash"></i> Remove
                        </button>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        showToast('Failed to load stock alerts', 'error');
        console.error('Error loading stock alerts:', error);
    }
}

function formatAlertDescription(alert) {
    const alertDescriptions = {
        'price_above': `Alert when price rises above $${alert.threshold}`,
        'price_below': `Alert when price drops below $${alert.threshold}`,
        'percent_up': `Alert when price increases by ${alert.threshold}%`,
        'percent_down': `Alert when price decreases by ${alert.threshold}%`
    };
    return alertDescriptions[alert.alert_type] || 'Custom alert';
}

function formatThreshold(alert) {
    if (alert.alert_type.includes('percent')) {
        return `${alert.threshold}%`;
    }
    return `$${alert.threshold.toFixed(2)}`;
}

function renderStockStatus(alert) {
    if (alert.is_triggered) {
        return `
            <div class="status-badge status-triggered">
                <i class="fas fa-bell"></i>
                Alert Triggered!
            </div>
        `;
    }
    
    if (!alert.current_price) {
        return `
            <div class="status-badge status-waiting">
                <i class="fas fa-clock"></i>
                Waiting for Data
            </div>
        `;
    }
    
    return `
        <div class="status-badge status-waiting">
            <i class="fas fa-eye"></i>
            Monitoring
        </div>
    `;
}

function showAddStockModal() {
    document.getElementById('addStockModal').classList.add('show');
    document.getElementById('stockSymbol').focus();
}

function closeAddStockModal() {
    document.getElementById('addStockModal').classList.remove('show');
    document.getElementById('addStockForm').reset();
    updateThresholdLabel();
}

function updateThresholdLabel() {
    const alertType = document.getElementById('alertType').value;
    const label = document.getElementById('thresholdLabel');
    const input = document.getElementById('alertThreshold');
    
    const labelConfig = {
        'price_above': { text: '💰 Price Threshold ($)', placeholder: '210.00', step: '0.01' },
        'price_below': { text: '💰 Price Threshold ($)', placeholder: '180.00', step: '0.01' },
        'percent_up': { text: '📈 Percentage Threshold (%)', placeholder: '5.0', step: '0.1' },
        'percent_down': { text: '📉 Percentage Threshold (%)', placeholder: '5.0', step: '0.1' }
    };
    
    const config = labelConfig[alertType] || { text: '🎯 Threshold', placeholder: '', step: '0.01' };
    
    label.innerHTML = config.text;
    input.placeholder = config.placeholder;
    input.step = config.step
;
}

async function addStockAlert(event) {
    event.preventDefault();
    
    const symbol = document.getElementById('stockSymbol').value.toUpperCase().trim();
    const alertType = document.getElementById('alertType').value;
    const threshold = parseFloat(document.getElementById('alertThreshold').value);
    
    if (!symbol || !alertType || !threshold || threshold <= 0) {
        showToast('Please fill in all fields with valid values', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/stocks`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ 
                symbol: symbol, 
                alert_type: alertType, 
                threshold: threshold 
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast(`🚨 Stock alert created for ${symbol}! Automatic monitoring will notify you when conditions are met.`);
            closeAddStockModal();
            loadStockAlerts();
            loadStats();
        } else {
            showToast(data.error || 'Failed to add stock alert', 'error');
        }
    } catch (error) {
        showToast('Network error: Failed to add stock alert', 'error');
        console.error('Error adding stock alert:', error);
    }
}

async function deleteStockAlert(alertId) {
    if (!confirm('Are you sure you want to remove this stock alert?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/stocks/${alertId}`, {
            method: 'DELETE',
            credentials: 'include',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (response.ok) {
            showToast('Stock alert removed successfully');
            loadStockAlerts();
            loadStats();
        } else {
            const data = await response.json();
            showToast(data.error || 'Failed to remove stock alert', 'error');
        }
    } catch (error) {
        showToast('Network error: Failed to remove stock alert', 'error');
        console.error('Error deleting stock alert:', error);
    }
}

// ===== SETTINGS MANAGEMENT =====
async function loadEmailConfig() {
    try {
        // Since email config is now per-user and handled through SMTP password,
        // we just need to show the current user's configuration status
        const response = await fetch(`${API_URL}/auth/session`, {
            credentials: 'include',
            headers: {
                'Accept': 'application/json'
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.logged_in && data.user.has_smtp) {
                document.getElementById('smtpPassword').placeholder = 'Current password configured (hidden)';
            } else {
                document.getElementById('smtpPassword').placeholder = 'Enter your Gmail app password';
            }
        }
    } catch (error) {
        console.error('Failed to load email config:', error);
    }
}

async function handleEmailSettings(event) {
    event.preventDefault();
    
    const smtpPassword = document.getElementById('smtpPassword').value.trim();
    
    if (!smtpPassword) {
        showToast('Please enter your Gmail app password', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/auth/update-smtp`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ smtp_password: smtpPassword })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('✅ Email settings updated! You will now receive alerts when deals are found.');
            document.getElementById('smtpPassword').value = '';
            document.getElementById('smtpPassword').placeholder = 'Current password configured (hidden)';
        } else {
            showToast(data.error || 'Failed to update email settings', 'error');
        }
    } catch (error) {
        showToast('Network error: Failed to update email settings', 'error');
        console.error('Error updating email settings:', error);
    }
}

// ===== EVENT LISTENERS SETUP =====
function setupEventListeners() {
    // Modal close on background click
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.classList.remove('show');
            }
        });
    });
    
    // Alert type change listener for stock modal
    const alertTypeSelect = document.getElementById('alertType');
    if (alertTypeSelect) {
        alertTypeSelect.addEventListener('change', updateThresholdLabel);
        // Initialize the label
        updateThresholdLabel();
    }
    
    // Email form submission
    const emailForm = document.getElementById('emailForm');
    if (emailForm) {
        emailForm.addEventListener('submit', handleEmailSettings);
    }
    
    // Platform select change for product modal
    const platformSelect = document.getElementById('platformSelect');
    if (platformSelect) {
        platformSelect.addEventListener('change', updateUrlPlaceholder);
    }
    
    // Auto-focus on modal opens
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            // Close any open modals
            document.querySelectorAll('.modal.show').forEach(modal => {
                modal.classList.remove('show');
            });
        }
    });
}

// ===== UTILITY FUNCTIONS =====
function formatLastChecked(timestamp) {
    if (!timestamp) return 'Never';
    
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffMins < 1) {
        return 'Just now';
    } else if (diffMins < 60) {
        return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
    } else if (diffHours < 24) {
        return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
    } else if (diffDays < 7) {
        return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
    } else {
        return date.toLocaleDateString();
    }
}

function generateProductCard(product, platform) {
    const config = platformConfigs[platform] || {};
    const isRoblox = platform === 'roblox';
    
    return `
        <div class="card" data-platform="${platform}" id="product-${product.id}">
            <div class="platform-badge">
                <span>${product.platform_icon || config.icon || (isRoblox ? '🎮' : '🛒')}</span>
                <span style="font-weight: 500;">${product.platform_name || config.name || 'Unknown'}</span>
            </div>
            <h3 class="card-title">${product.title || 'Loading product details...'}</h3>
            <p class="card-subtitle">${truncateUrl(product.url)}</p>
            
            <div class="price-info">
                <div class="price-item">
                    <span class="price-label">Current Price</span>
                    <span class="price-value ${isRoblox ? 'robux' : ''}" id="current-price-${product.id}">
                        ${product.last_price ? formatPrice(product.last_price, platform) : '--'}
                    </span>
                </div>
                <div class="price-item">
                    <span class="price-label">Target Price</span>
                    <span class="price-value ${isRoblox ? 'robux' : ''}">${formatPrice(product.target_price, platform)}</span>
                </div>
            </div>
            
            <div id="status-${product.id}">
                ${renderProductStatus(product, platform)}
            </div>
            
            ${product.last_checked ? `
                <div style="text-align: center; color: #666; font-size: 0.85rem; margin: 12px 0;">
                    Last checked: ${formatLastChecked(product.last_checked)}
                </div>
            ` : ''}
            
            <div class="card-actions">
                <a href="${product.url}" target="_blank" class="btn btn-primary btn-icon">
                    <i class="fas fa-external-link-alt"></i> ${isRoblox ? 'View Item' : 'View Product'}
                </a>
                <button onclick="${isRoblox ? 'deleteRobloxItem' : 'deleteProduct'}(${product.id})" class="btn btn-secondary btn-icon">
                    <i class="fas fa-trash"></i> Remove
                </button>
            </div>
        </div>
    `;
}

// ===== KEYBOARD SHORTCUTS =====
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K to focus on adding products
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const activePage = document.querySelector('.page.active');
            if (activePage) {
                const pageId = activePage.id;
                if (pageId === 'productsPage') {
                    showAddProductModal();
                } else if (pageId === 'robloxPage') {
                    showAddRobloxModal();
                } else if (pageId === 'stocksPage') {
                    showAddStockModal();
                }
            }
        }
        
        // Number keys for quick page navigation
        if (e.altKey && e.key >= '1' && e.key <= '4') {
            e.preventDefault();
            const navItems = document.querySelectorAll('.nav-item');
            const pageMap = {
                '1': 'productsPage',
                '2': 'robloxPage', 
                '3': 'stocksPage',
                '4': 'settingsPage'
            };
            
            const pageId = pageMap[e.key];
            const navItem = navItems[parseInt(e.key) - 1];
            
            if (pageId && navItem) {
                showPage(pageId, navItem);
            }
        }
    });
}

// ===== APP INITIALIZATION =====
async function initializeApp() {
    console.log('🚀 Initializing PriceTracker App...');
    
    try {
        // Set up event listeners
        setupEventListeners();
        setupKeyboardShortcuts();
        
        // Check user session
        await checkSession();
        
        console.log('✅ App initialized successfully');
        
    } catch (error) {
        console.error('❌ App initialization failed:', error);
        showToast('Failed to initialize app. Please refresh the page.', 'error');
    }
}

// ===== PERIODIC DATA REFRESH =====
function startPeriodicRefresh() {
    // Refresh stats every 2 minutes
    setInterval(() => {
        if (currentUser) {
            loadStats();
        }
    }, 120000);
    
    // Refresh current page data every 5 minutes
    setInterval(() => {
        if (currentUser) {
            const activePage = document.querySelector('.page.active');
            if (activePage) {
                const pageId = activePage.id;
                if (pageId === 'productsPage') {
                    loadProducts();
                } else if (pageId === 'robloxPage') {
                    loadRobloxItems();
                } else if (pageId === 'stocksPage') {
                    loadStockAlerts();
                }
            }
        }
    }, 300000);
}

// ===== ERROR HANDLING =====
window.addEventListener('error', function(e) {
    console.error('Global error caught:', e.error);
    if (e.error && e.error.message && e.error.message.includes('fetch')) {
        showToast('Network error: Please check your connection and ensure the backend is running.', 'error');
    }
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    if (e.reason && e.reason.message && e.reason.message.includes('fetch')) {
        showToast('Network error: Failed to connect to server.', 'error');
    }
});

// ===== DOCUMENT READY =====
document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 DOM Content Loaded');
    initializeApp();
    startPeriodicRefresh();
});

// ===== PAGE VISIBILITY HANDLING =====
document.addEventListener('visibilitychange', function() {
    if (!document.hidden && currentUser) {
        // Page became visible, refresh data
        loadStats();
        
        const activePage = document.querySelector('.page.active');
        if (activePage) {
            const pageId = activePage.id;
            if (pageId === 'productsPage') {
                loadProducts();
            } else if (pageId === 'robloxPage') {
                loadRobloxItems();
            } else if (pageId === 'stocksPage') {
                loadStockAlerts();
            }
        }
    }
});

// ===== SERVICE WORKER REGISTRATION (Optional) =====
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        // Service worker could be added here for offline functionality
        console.log('🔧 Service Worker support detected');
    });
}

console.log('📱 PriceTracker App loaded successfully!');