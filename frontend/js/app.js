// frontend/js/app.js - FIXED VERSION WITH REAL SAVINGS CALCULATION
// TagTracker JavaScript - Complete Implementation with Accurate Savings

const API_URL = window.location.origin + '/api';  // Dynamic API URL based on current host

// Application state
let currentUser = null;
let autoRefreshInterval = null;
let lastDataUpdate = null;
let connectionRetryCount = 0;
let maxRetries = 3;

// Platform configurations with enhanced metadata
const platformConfigs = {
    amazon: {
        name: 'Amazon',
        exampleUrl: 'https://www.amazon.com/dp/B08N5WRWNW',
        tips: 'Use the product URL from the address bar. Amazon URLs typically contain /dp/ or /gp/product/',
        icon: '🛒',
        color: '#ff9900',
        domains: ['amazon.com', 'amazon.co.uk', 'amazon.ca', 'amazon.de', 'amazon.fr']
    },
    ebay: {
        name: 'eBay',
        exampleUrl: 'https://www.ebay.com/itm/123456789012',
        tips: 'Use the item URL that contains /itm/ followed by the item number',
        icon: '🏷️',
        color: '#e53238',
        domains: ['ebay.com', 'ebay.co.uk', 'ebay.ca', 'ebay.de']
    },
    etsy: {
        name: 'Etsy',
        exampleUrl: 'https://www.etsy.com/listing/123456789/handmade-product-name',
        tips: 'Copy the listing URL that contains /listing/ followed by the listing ID',
        icon: '🎨',
        color: '#f16521',
        domains: ['etsy.com']
    },
    walmart: {
        name: 'Walmart',
        exampleUrl: 'https://www.walmart.com/ip/Product-Name/123456789',
        tips: 'Walmart URLs contain /ip/ followed by the product name and ID',
        icon: '🏪',
        color: '#004c91',
        domains: ['walmart.com']
    },
    storenvy: {
        name: 'Storenvy',
        exampleUrl: 'https://store-name.storenvy.com/products/123456-product-name',
        tips: 'Copy the full product URL from the product page',
        icon: '🏬',
        color: '#00bfa5',
        domains: ['storenvy.com']
    },
    roblox: {
        name: 'Roblox UGC',
        exampleUrl: 'https://www.roblox.com/catalog/123456789/item-name',
        tips: 'Copy the URL from the Roblox catalog item page',
        icon: '🎮',
        color: '#00b06f',
        domains: ['roblox.com'],
        currency: 'robux'
    }
};

// Theme management
const themeManager = {
    init() {
        const savedTheme = localStorage.getItem('tagtracker-theme') || 'auto';
        this.setTheme(savedTheme);
        this.updateThemeButtons(savedTheme);
    },

    setTheme(theme) {
        const root = document.documentElement;
        
        if (theme === 'auto') {
            // Use system preference
            root.removeAttribute('data-theme');
        } else {
            root.setAttribute('data-theme', theme);
        }
        
        localStorage.setItem('tagtracker-theme', theme);
        this.updateThemeButtons(theme);
    },

    updateThemeButtons(activeTheme) {
        document.querySelectorAll('.theme-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.theme === activeTheme);
        });
    }
};

// Enhanced connection manager
const connectionManager = {
    async checkConnection() {
        try {
            console.log('🔗 Checking backend connection at:', API_URL);
            const response = await fetch(`${API_URL}/auth/session`, {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                },
                timeout: 10000
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                const responseText = await response.text();
                console.error('Non-JSON response:', responseText.substring(0, 200));
                throw new Error('Backend is not returning JSON - server may be down');
            }
            
            connectionRetryCount = 0; // Reset on successful connection
            return true;
            
        } catch (error) {
            console.error('🚫 Backend connection failed:', error);
            
            if (connectionRetryCount < maxRetries) {
                connectionRetryCount++;
                console.log(`🔄 Retrying connection (${connectionRetryCount}/${maxRetries})...`);
                await new Promise(resolve => setTimeout(resolve, 2000 * connectionRetryCount));
                return this.checkConnection();
            }
            
            this.showConnectionError(error);
            return false;
        }
    },

    showConnectionError(error) {
        const isServerDown = error.message.includes('fetch') || error.message.includes('Failed to fetch');
        const isServerError = error.message.includes('500') || error.message.includes('JSON');
        
        if (isServerDown) {
            showToast('🚫 Cannot connect to backend server. Please start the Flask app: python backend/app.py', 'error');
        } else if (isServerError) {
            showToast('🛠️ Backend server error. Please check the Flask server logs and restart it.', 'error');
        } else {
            showToast(`⚠️ Connection error: ${error.message}`, 'error');
        }
    }
};

// Enhanced auth manager
const authManager = {
    async checkSession() {
        try {
            const backendOk = await connectionManager.checkConnection();
            if (!backendOk) {
                this.showAuth();
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
                console.error('❌ Session check failed:', response.status);
                this.showAuth();
                return;
            }

            const data = await response.json();
            
            if (data.logged_in) {
                currentUser = data.user;
                console.log('✅ User authenticated:', currentUser.email);
                this.showApp();
            } else {
                console.log('👤 User not authenticated');
                this.showAuth();
            }
        } catch (error) {
            console.error('❌ Session check error:', error);
            this.showAuth();
        }
    },

    showAuth() {
        document.getElementById('authContainer').style.display = 'flex';
        document.getElementById('appContainer').style.display = 'none';
        dataManager.stopAutoRefresh();
    },

    showApp() {
        document.getElementById('authContainer').style.display = 'none';
        document.getElementById('appContainer').style.display = 'block';
        
        // Update user interface
        if (currentUser) {
            document.getElementById('userName').textContent = currentUser.first_name;
            document.getElementById('accountName').textContent = `${currentUser.first_name} ${currentUser.last_name || ''}`.trim();
            document.getElementById('accountEmail').textContent = currentUser.email;
        }
        
        // Initialize app data
        dataManager.loadInitialData();
        dataManager.startAutoRefresh();
    },

    async login(email, password) {
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
            
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                throw new Error('Server returned non-JSON response - backend may be misconfigured');
            }
            
            const data = await response.json();
            
            if (response.ok) {
                currentUser = data.user;
                showToast(`🎉 Welcome back, ${currentUser.first_name}!`);
                this.showApp();
                return { success: true };
            } else {
                return { success: false, error: data.error || 'Login failed' };
            }
        } catch (error) {
            console.error('🚫 Login error:', error);
            return { 
                success: false, 
                error: error.message.includes('JSON') ? 
                    'Backend server error - please check server logs' : 
                    `Network error: ${error.message}`
            };
        }
    },

    async signup(userData) {
        try {
            // Enhanced validation
            const validation = this.validateSignupData(userData);
            if (!validation.valid) {
                return { success: false, error: validation.error };
            }

            const response = await fetch(`${API_URL}/auth/signup`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify(userData)
            });
            
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                throw new Error('Server returned non-JSON response - backend may be misconfigured');
            }
            
            const data = await response.json();
            
            if (response.ok) {
                currentUser = data.user;
                showToast(`🎉 Welcome to TagTracker, ${currentUser.first_name}!`);
                this.showApp();
                return { success: true };
            } else {
                return { success: false, error: data.error || 'Signup failed' };
            }
        } catch (error) {
            console.error('🚫 Signup error:', error);
            return { 
                success: false, 
                error: error.message.includes('JSON') ? 
                    'Backend server error - please check server logs' : 
                    `Network error: ${error.message}`
            };
        }
    },

    validateSignupData(data) {
        if (!data.first_name?.trim()) {
            return { valid: false, error: 'First name is required' };
        }
        
        if (!data.email?.trim()) {
            return { valid: false, error: 'Email address is required' };
        }
        
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(data.email)) {
            return { valid: false, error: 'Please enter a valid email address' };
        }
        
        if (!data.password || data.password.length < 6) {
            return { valid: false, error: 'Password must be at least 6 characters long' };
        }
        
        // Validate SMTP password format if provided
        if (data.smtp_password && data.smtp_password.length > 0) {
            if (data.smtp_password.length < 16 || !data.smtp_password.includes(' ')) {
                return { 
                    valid: false, 
                    error: 'Gmail app password should be 16 characters with spaces (like: xxxx xxxx xxxx xxxx)' 
                };
            }
        }
        
        return { valid: true };
    },

    async logout() {
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
                this.showAuth();
                showToast('👋 Signed out successfully');
            }
        } catch (error) {
            showToast('❌ Failed to sign out', 'error');
            console.error('Logout error:', error);
        }
    }
};

// Enhanced data manager with REAL SAVINGS CALCULATION
const dataManager = {
    async loadInitialData() {
        const loadingPromises = [
            this.loadStats(),
            this.loadProducts(),
        ];
        
        try {
            await Promise.all(loadingPromises);
            lastDataUpdate = new Date();
            console.log('📊 Initial data loaded successfully');
        } catch (error) {
            console.error('❌ Failed to load initial data:', error);
            showToast('⚠️ Some data failed to load. Retrying...', 'error');
            // Retry after a delay
            setTimeout(() => this.loadInitialData(), 3000);
        }
    },

    // FIXED: Calculate REAL savings based on actual price drops
    async loadStats() {
        try {
            // Get all products to calculate REAL savings
            const productsResponse = await fetch(`${API_URL}/products`, {
                credentials: 'include',
                headers: { 'Accept': 'application/json' }
            });
            
            if (!productsResponse.ok) {
                if (productsResponse.status === 401) {
                    authManager.showAuth();
                    return;
                }
                throw new Error(`Failed to load products: ${productsResponse.status}`);
            }
            
            const allProducts = await productsResponse.json();
            
            // Calculate REAL SAVINGS - only from products that are actually below target
            let totalRealSavings = 0;
            let ecommerceCount = 0;
            let robloxCount = 0;
            
            allProducts.forEach(product => {
                const platform = product.platform;
                
                // Count by platform type
                if (['amazon', 'ebay', 'etsy', 'walmart', 'storenvy'].includes(platform)) {
                    ecommerceCount++;
                } else if (platform === 'roblox') {
                    robloxCount++;
                }
                
                // Calculate REAL savings only for products below target with valid prices
                if (product.last_price && product.target_price && product.last_price < product.target_price) {
                    const savings = product.target_price - product.last_price;
                    totalRealSavings += savings;
                    console.log(`💰 Real savings found: ${product.title} - $${savings.toFixed(2)}`);
                }
            });
            
            // Get stock alerts count
            const stockResponse = await fetch(`${API_URL}/stocks`, {
                credentials: 'include',
                headers: { 'Accept': 'application/json' }
            });
            
            let stockAlertsCount = 0;
            if (stockResponse.ok) {
                const stocks = await stockResponse.json();
                stockAlertsCount = stocks.length;
            }
            
            // Update stats with animation - using REAL calculated savings
            this.animateNumber('totalProducts', ecommerceCount);
            this.animateNumber('totalRobloxItems', robloxCount);
            this.animateNumber('totalStockAlerts', stockAlertsCount);
            this.animateNumber('totalSavings', totalRealSavings, true);
            
            console.log(`📊 Stats updated - Real savings: $${totalRealSavings.toFixed(2)}`);
            
        } catch (error) {
            console.error('❌ Failed to load stats:', error);
            // Set default values on error
            this.animateNumber('totalProducts', 0);
            this.animateNumber('totalRobloxItems', 0);
            this.animateNumber('totalStockAlerts', 0);
            this.animateNumber('totalSavings', 0, true);
        }
    },

    animateNumber(elementId, targetValue, isCurrency = false) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const currentValue = parseFloat(element.textContent.replace(/[^0-9.]/g, '')) || 0;
        const increment = (targetValue - currentValue) / 20;
        let current = currentValue;
        
        const animation = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= targetValue) || (increment < 0 && current <= targetValue)) {
                current = targetValue;
                clearInterval(animation);
            }
            
            if (isCurrency) {
                element.textContent = current.toFixed(2);
            } else {
                element.textContent = Math.round(current);
            }
        }, 50);
    },

    async loadProducts() {
        try {
            const response = await fetch(`${API_URL}/products`, {
                credentials: 'include',
                headers: { 'Accept': 'application/json' }
            });
            
            if (!response.ok) {
                if (response.status === 401) {
                    authManager.showAuth();
                    return;
                }
                throw new Error(`Failed to load products: ${response.status}`);
            }
            
            const allProducts = await response.json();
            
            // Update current page if it's showing products
            const activePage = document.querySelector('.page.active');
            if (activePage) {
                const pageId = activePage.id;
                if (pageId === 'productsPage') {
                    this.renderProducts(allProducts.filter(p => 
                        ['amazon', 'ebay', 'etsy', 'walmart', 'storenvy'].includes(p.platform)
                    ), 'products');
                } else if (pageId === 'robloxPage') {
                    this.renderProducts(allProducts.filter(p => p.platform === 'roblox'), 'roblox');
                }
            }
            
        } catch (error) {
            console.error('❌ Failed to load products:', error);
            showToast('Failed to load products', 'error');
        }
    },

    async loadStockAlerts() {
        try {
            const response = await fetch(`${API_URL}/stocks`, {
                credentials: 'include',
                headers: { 'Accept': 'application/json' }
            });
            
            if (!response.ok) {
                if (response.status === 401) {
                    authManager.showAuth();
                    return;
                }
                throw new Error(`Failed to load stock alerts: ${response.status}`);
            }
            
            const alerts = await response.json();
            this.renderStockAlerts(alerts);
            
        } catch (error) {
            console.error('❌ Failed to load stock alerts:', error);
            showToast('Failed to load stock alerts', 'error');
        }
    },

    renderProducts(products, type) {
        const listId = type === 'roblox' ? 'robloxList' : 'productsList';
        const emptyStateId = type === 'roblox' ? 'robloxEmptyState' : 'emptyState';
        
        const productsList = document.getElementById(listId);
        const emptyState = document.getElementById(emptyStateId);
        
        if (!productsList || !emptyState) return;
        
        if (products.length === 0) {
            productsList.style.display = 'none';
            emptyState.style.display = 'block';
        } else {
            productsList.style.display = 'grid';
            emptyState.style.display = 'none';
            
            productsList.innerHTML = products.map(product => 
                this.createProductCard(product, type)
            ).join('');
            
            // Add fade-in animation
            productsList.querySelectorAll('.card').forEach((card, index) => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                setTimeout(() => {
                    card.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                    card.style.opacity = '1';
                    card.style.transform = 'translateY(0)';
                }, index * 100);
            });
        }
    },

    createProductCard(product, type) {
        const platform = product.platform || 'storenvy';
        const config = platformConfigs[platform] || {};
        const isRoblox = platform === 'roblox';
        
        return `
            <div class="card" data-platform="${platform}" id="product-${product.id}">
                <div class="platform-badge" style="background-color: ${config.color}20; color: ${config.color};">
                    <span>${product.platform_icon || config.icon || '🛒'}</span>
                    <span style="font-weight: 500;">${product.platform_name || config.name || 'Unknown'}</span>
                </div>
                <h3 class="card-title" title="${product.title || 'Loading product details...'}">${product.title || 'Loading product details...'}</h3>
                <p class="card-subtitle" title="${product.url}">${this.truncateUrl(product.url)}</p>
                
                <div class="price-info">
                    <div class="price-item">
                        <span class="price-label">Current Price</span>
                        <span class="price-value ${isRoblox ? 'robux' : ''}" id="current-price-${product.id}">
                            ${product.last_price ? this.formatPrice(product.last_price, platform) : '--'}
                        </span>
                    </div>
                    <div class="price-item">
                        <span class="price-label">Target Price</span>
                        <span class="price-value ${isRoblox ? 'robux' : ''}">${this.formatPrice(product.target_price, platform)}</span>
                    </div>
                </div>
                
                <div id="status-${product.id}">
                    ${this.renderProductStatus(product, platform)}
                </div>
                
                ${product.last_checked ? `
                    <div class="last-checked">
                        <i class="fas fa-clock"></i>
                        Last checked: ${this.formatLastChecked(product.last_checked)}
                    </div>
                ` : ''}
                
                <div class="card-actions">
                    <a href="${product.url}" target="_blank" class="btn btn-primary btn-icon">
                        <i class="fas fa-external-link-alt"></i> ${isRoblox ? 'View Item' : 'View Product'}
                    </a>
                    <button onclick="productManager.deleteProduct(${product.id}, '${type}')" class="btn btn-secondary btn-icon">
                        <i class="fas fa-trash"></i> Remove
                    </button>
                </div>
            </div>
        `;
    },

    renderStockAlerts(alerts) {
        const stocksList = document.getElementById('stocksList');
        const emptyState = document.getElementById('stocksEmptyState');
        
        if (!stocksList || !emptyState) return;
        
        if (alerts.length === 0) {
            stocksList.style.display = 'none';
            emptyState.style.display = 'block';
        } else {
            stocksList.style.display = 'grid';
            emptyState.style.display = 'none';
            
            stocksList.innerHTML = alerts.map(alert => `
                <div class="card" id="stock-${alert.id}">
                    <div class="platform-badge" style="background-color: #ff6b6b20; color: #ff6b6b;">
                        <i class="fas fa-chart-line"></i>
                        <span style="font-weight: 500;">Stock Alert</span>
                    </div>
                    <h3 class="card-title">
                        ${alert.company_name} (${alert.symbol})
                    </h3>
                    <p class="card-subtitle">${this.formatAlertDescription(alert)}</p>
                    
                    <div class="price-info">
                        <div class="price-item">
                            <span class="price-label">Current Price</span>
                            <span class="price-value" id="stock-price-${alert.id}">
                                ${alert.current_price ? `$${alert.current_price.toFixed(2)}` : '--'}
                            </span>
                        </div>
                        <div class="price-item">
                            <span class="price-label">Threshold</span>
                            <span class="price-value">${this.formatThreshold(alert)}</span>
                        </div>
                    </div>
                    
                    <div id="stock-status-${alert.id}">
                        ${this.renderStockStatus(alert)}
                    </div>
                    
                    <div class="card-actions">
                        <a href="https://finance.yahoo.com/quote/${alert.symbol}" target="_blank" class="btn btn-primary btn-icon">
                            <i class="fas fa-chart-line"></i> View Chart
                        </a>
                        <button onclick="stockManager.deleteAlert(${alert.id})" class="btn btn-secondary btn-icon">
                            <i class="fas fa-trash"></i> Remove
                        </button>
                    </div>
                </div>
            `).join('');
        }
    },

    // Utility methods
    truncateUrl(url) {
        if (url.length <= 50) return url;
        return url.substring(0, 47) + '...';
    },

    formatPrice(price, platform) {
        if (platform === 'roblox') {
            return `${Math.round(price)} R$`;
        }
        return `$${price.toFixed(2)}`;
    },

    formatLastChecked(timestamp) {
        if (!timestamp) return 'Never';
        
        const date = new Date(timestamp);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        if (diffDays < 7) return `${diffDays}d ago`;
        return date.toLocaleDateString();
    },

    renderProductStatus(product, platform) {
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
            const savingsText = platform === 'roblox' ? 
                `${Math.round(savings)} R$` : 
                `$${savings.toFixed(2)}`;
            const emoji = platform === 'roblox' ? '🎮' : '💰';
            
            return `
                <div class="status-badge status-triggered">
                    <i class="fas fa-check-circle"></i>
                    ${emoji} Target Hit! Save ${savingsText}
                </div>
            `;
        }
        
        const statusText = platform === 'roblox' ? 'Watching Robux Price' : 'Monitoring Price';
        
        return `
            <div class="status-badge status-waiting">
                <i class="fas fa-eye"></i>
                ${statusText}
            </div>
        `;
    },

    formatAlertDescription(alert) {
        const descriptions = {
            'price_above': `Alert when price rises above $${alert.threshold}`,
            'price_below': `Alert when price drops below $${alert.threshold}`,
            'percent_up': `Alert when price increases by ${alert.threshold}%`,
            'percent_down': `Alert when price decreases by ${alert.threshold}%`
        };
        return descriptions[alert.alert_type] || 'Custom alert';
    },

    formatThreshold(alert) {
        if (alert.alert_type.includes('percent')) {
            return `${alert.threshold}%`;
        }
        return `$${alert.threshold.toFixed(2)}`;
    },

    renderStockStatus(alert) {
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
    },

    startAutoRefresh() {
        if (autoRefreshInterval) {
            clearInterval(autoRefreshInterval);
        }
        
        // Refresh data every 30 seconds
        autoRefreshInterval = setInterval(() => {
            this.loadStats();
            
            // Refresh current page data
            const activePage = document.querySelector('.page.active');
            if (activePage) {
                const pageId = activePage.id;
                if (pageId === 'productsPage' || pageId === 'robloxPage') {
                    this.loadProducts();
                } else if (pageId === 'stocksPage') {
                    this.loadStockAlerts();
                }
            }
        }, 30000);
    },

    stopAutoRefresh() {
        if (autoRefreshInterval) {
            clearInterval(autoRefreshInterval);
            autoRefreshInterval = null;
        }
    }
};

// Enhanced product manager
const productManager = {
    validateUrl(url, platform) {
        if (!platform || !platformConfigs[platform]) {
            return false;
        }
        
        const config = platformConfigs[platform];
        return config.domains.some(domain => url.toLowerCase().includes(domain));
    },

    async addProduct(formData) {
        try {
            const response = await fetch(`${API_URL}/products`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            
            if (response.ok) {
                const platform = formData.platform || 'unknown';
                const platformName = platformConfigs[platform]?.name || 'Product';
                showToast(`✅ ${platformName} added successfully! Monitoring has started.`);
                dataManager.loadProducts();
                dataManager.loadStats();
                return { success: true };
            } else {
                return { success: false, error: data.error || 'Failed to add product' };
            }
        } catch (error) {
            console.error('❌ Add product error:', error);
            return { success: false, error: 'Network error: Failed to add product' };
        }
    },

    async deleteProduct(productId, type) {
        const itemType = type === 'roblox' ? 'Roblox item' : 'product';
        
        if (!confirm(`Are you sure you want to stop tracking this ${itemType}?`)) {
            return;
        }
        
        try {
            const response = await fetch(`${API_URL}/products/${productId}`, {
                method: 'DELETE',
                credentials: 'include',
                headers: { 'Accept': 'application/json' }
            });
            
            if (response.ok) {
                showToast(`${itemType.charAt(0).toUpperCase() + itemType.slice(1)} removed from tracking`);
                dataManager.loadProducts();
                dataManager.loadStats();
            } else {
                const data = await response.json();
                showToast(data.error || `Failed to remove ${itemType}`, 'error');
            }
        } catch (error) {
            showToast(`Network error: Failed to remove ${itemType}`, 'error');
            console.error('Delete product error:', error);
        }
    }
};

// Enhanced stock manager
const stockManager = {
    async addAlert(alertData) {
        try {
            const response = await fetch(`${API_URL}/stocks`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                credentials: 'include',
                body: JSON.stringify(alertData)
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showToast(`🚨 Stock alert created for ${alertData.symbol}! Monitoring has started.`);
                dataManager.loadStockAlerts();
                dataManager.loadStats();
                return { success: true };
            } else {
                return { success: false, error: data.error || 'Failed to add stock alert' };
            }
        } catch (error) {
            console.error('❌ Add stock alert error:', error);
            return { success: false, error: 'Network error: Failed to add stock alert' };
        }
    },

    async deleteAlert(alertId) {
        if (!confirm('Are you sure you want to remove this stock alert?')) {
            return;
        }
        
        try {
            const response = await fetch(`${API_URL}/stocks/${alertId}`, {
                method: 'DELETE',
                credentials: 'include',
                headers: { 'Accept': 'application/json' }
            });
            
            if (response.ok) {
                showToast('Stock alert removed successfully');
                dataManager.loadStockAlerts();
                dataManager.loadStats();
            } else {
                const data = await response.json();
                showToast(data.error || 'Failed to remove stock alert', 'error');
            }
        } catch (error) {
            showToast('Network error: Failed to remove stock alert', 'error');
            console.error('Delete stock alert error:', error);
        }
    }
};

// Enhanced settings manager
const settingsManager = {
    async loadEmailConfig() {
        try {
            const response = await fetch(`${API_URL}/auth/session`, {
                credentials: 'include',
                headers: { 'Accept': 'application/json' }
            });
            
            if (response.ok) {
                const data = await response.json();
                const smtpInput = document.getElementById('smtpPassword');
                if (smtpInput) {
                    if (data.logged_in && data.user.has_smtp) {
                        smtpInput.placeholder = 'Current password configured (hidden)';
                    } else {
                        smtpInput.placeholder = 'Enter your Gmail app password';
                    }
                }
            }
        } catch (error) {
            console.error('Failed to load email config:', error);
        }
    },

    async updateEmailSettings(smtpPassword) {
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
                const smtpInput = document.getElementById('smtpPassword');
                if (smtpInput) {
                    smtpInput.value = '';
                    smtpInput.placeholder = 'Current password configured (hidden)';
                }
                return { success: true };
            } else {
                return { success: false, error: data.error || 'Failed to update email settings' };
            }
        } catch (error) {
            console.error('❌ Update email settings error:', error);
            return { success: false, error: 'Network error: Failed to update email settings' };
        }
    }
};

// Enhanced UI manager
const uiManager = {
    showPage(pageId, navItem) {
        // Hide all pages
        document.querySelectorAll('.page').forEach(page => {
            page.classList.remove('active');
        });
        
        // Show selected page with animation
        const targetPage = document.getElementById(pageId);
        targetPage.classList.add('active');
        targetPage.style.opacity = '0';
        targetPage.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            targetPage.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            targetPage.style.opacity = '1';
            targetPage.style.transform = 'translateY(0)';
        }, 50);
        
        // Update nav
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
        });
        if (navItem) navItem.classList.add('active');
        
        // Load page-specific data
        if (pageId === 'productsPage') {
            dataManager.loadProducts();
            dataManager.loadStats();
        } else if (pageId === 'robloxPage') {
            dataManager.loadProducts();
            dataManager.loadStats();
        } else if (pageId === 'stocksPage') {
            dataManager.loadStockAlerts();
            dataManager.loadStats();
        } else if (pageId === 'settingsPage') {
            settingsManager.loadEmailConfig();
        }
    },

    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('show');
            // Focus first input
            const firstInput = modal.querySelector('input, select');
            if (firstInput) {
                setTimeout(() => firstInput.focus(), 100);
            }
        }
    },

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('show');
            // Reset form if exists
            const form = modal.querySelector('form');
            if (form) form.reset();
            
            // Reset any dynamic content
            if (modalId === 'addProductModal') {
                this.resetProductModal();
            } else if (modalId === 'addStockModal') {
                this.resetStockModal();
            }
        }
    },

    resetProductModal() {
        const urlInput = document.getElementById('productUrl');
        const urlHint = document.getElementById('urlHint');
        const platformInfo = document.getElementById('platformInfo');
        
        if (urlInput) {
            urlInput.disabled = true;
            urlInput.placeholder = 'Select a platform first...';
        }
        if (urlHint) urlHint.textContent = '';
        if (platformInfo) platformInfo.style.display = 'none';
    },

    resetStockModal() {
        this.updateThresholdLabel();
    },

    updateUrlPlaceholder() {
        const platformSelect = document.getElementById('platformSelect');
        const urlInput = document.getElementById('productUrl');
        const urlHint = document.getElementById('urlHint');
        const platformInfo = document.getElementById('platformInfo');
        const platformTips = document.getElementById('platformTips');
        
        if (!platformSelect || !urlInput) return;
        
        const selectedPlatform = platformSelect.value;
        
        if (selectedPlatform && platformConfigs[selectedPlatform]) {
            const config = platformConfigs[selectedPlatform];
            urlInput.placeholder = config.exampleUrl;
            if (urlHint) urlHint.textContent = `Example: ${config.exampleUrl}`;
            if (platformTips) platformTips.textContent = config.tips;
            if (platformInfo) platformInfo.style.display = 'block';
            urlInput.disabled = false;
            urlInput.value = '';
        } else {
            urlInput.placeholder = 'Select a platform first...';
            if (urlHint) urlHint.textContent = '';
            if (platformInfo) platformInfo.style.display = 'none';
            urlInput.disabled = true;
        }
    },

    updateThresholdLabel() {
        const alertType = document.getElementById('alertType');
        const label = document.getElementById('thresholdLabel');
        const input = document.getElementById('alertThreshold');
        
        if (!alertType || !label || !input) return;
        
        const labelConfig = {
            'price_above': { text: '💰 Price Threshold ($)', placeholder: '210.00', step: '0.01' },
            'price_below': { text: '💰 Price Threshold ($)', placeholder: '180.00', step: '0.01' },
            'percent_up': { text: '📈 Percentage Threshold (%)', placeholder: '5.0', step: '0.1' },
            'percent_down': { text: '📉 Percentage Threshold (%)', placeholder: '5.0', step: '0.1' }
        };
        
        const config = labelConfig[alertType.value] || { text: '🎯 Threshold', placeholder: '', step: '0.01' };
        
        label.innerHTML = config.text;
        input.placeholder = config.placeholder;
        input.step = config.step;
    }
};

// Enhanced toast notifications
function showToast(message, type = 'success', duration = 4000) {
    const toast = document.getElementById('toast');
    if (!toast) return;
    
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.add('show');
    
    // Add icon based on type
    const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
    toast.textContent = `${icon} ${message}`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, duration);
}

// Enhanced event handlers
async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('loginEmail').value.trim();
    const password = document.getElementById('loginPassword').value;
    
    if (!email || !password) {
        showToast('Please enter both email and password', 'error');
        return;
    }
    
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Signing In...';
    submitBtn.disabled = true;
    
    try {
        const result = await authManager.login(email, password);
        
        if (result.success) {
            document.getElementById('loginForm').querySelector('form').reset();
        } else {
            showToast(result.error, 'error');
        }
    } finally {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

async function handleSignup(event) {
    event.preventDefault();
    
    const formData = {
        first_name: document.getElementById('signupFirstName').value.trim(),
        last_name: document.getElementById('signupLastName').value.trim(),
        email: document.getElementById('signupEmail').value.trim(),
        password: document.getElementById('signupPassword').value,
        smtp_password: document.getElementById('signupSmtpPassword').value.trim()
    };
    
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating Account...';
    submitBtn.disabled = true;
    
    try {
        const result = await authManager.signup(formData);
        
        if (result.success) {
            document.getElementById('signupForm').querySelector('form').reset();
        } else {
            showToast(result.error, 'error');
        }
    } finally {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

async function handleLogout() {
    if (!confirm('Are you sure you want to sign out?')) {
        return;
    }
    
    await authManager.logout();
}

// Form handlers
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

// Modal handlers
function showAddProductModal() {
    uiManager.showModal('addProductModal');
}

function closeAddProductModal() {
    uiManager.closeModal('addProductModal');
}

function showAddRobloxModal() {
    uiManager.showModal('addRobloxModal');
}

function closeAddRobloxModal() {
    uiManager.closeModal('addRobloxModal');
}

function showAddStockModal() {
    uiManager.showModal('addStockModal');
}

function closeAddStockModal() {
    uiManager.closeModal('addStockModal');
}

function updateUrlPlaceholder() {
    uiManager.updateUrlPlaceholder();
}

function updateThresholdLabel() {
    uiManager.updateThresholdLabel();
}

// Page navigation
function showPage(pageId, navItem) {
    uiManager.showPage(pageId, navItem);
}

// Theme management
function setTheme(theme) {
    themeManager.setTheme(theme);
}

// Product form handlers
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
    
    if (!productManager.validateUrl(url, platform)) {
        showToast(`This URL doesn't appear to be from ${platformConfigs[platform].name}. Please check the URL and platform selection.`, 'error');
        return;
    }
    
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';
    submitBtn.disabled = true;
    
    try {
        const result = await productManager.addProduct({ url, target_price: targetPrice });
        
        if (result.success) {
            closeAddProductModal();
        } else {
            showToast(result.error, 'error');
        }
    } finally {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

async function addRobloxItem(event) {
    event.preventDefault();
    
    const url = document.getElementById('robloxUrl').value.trim();
    const targetPrice = parseInt(document.getElementById('robloxTargetPrice').value);
    
    if (!url || !targetPrice || targetPrice <= 0) {
        showToast('Please enter a valid Roblox URL and target price in Robux', 'error');
        return;
    }
    
    if (!productManager.validateUrl(url, 'roblox')) {
        showToast('This URL doesn\'t appear to be from Roblox. Please check the URL.', 'error');
        return;
    }
    
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';
    submitBtn.disabled = true;
    
    try {
        const result = await productManager.addProduct({ url, target_price: targetPrice });
        
        if (result.success) {
            closeAddRobloxModal();
        } else {
            showToast(result.error, 'error');
        }
    } finally {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
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
    
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating...';
    submitBtn.disabled = true;
    
    try {
        const result = await stockManager.addAlert({ 
            symbol: symbol, 
            alert_type: alertType, 
            threshold: threshold 
        });
        
        if (result.success) {
            closeAddStockModal();
        } else {
            showToast(result.error, 'error');
        }
    } finally {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

// Email settings handler
async function handleEmailSettings(event) {
    event.preventDefault();
    
    const smtpPassword = document.getElementById('smtpPassword').value.trim();
    
    if (!smtpPassword) {
        showToast('Please enter your Gmail app password', 'error');
        return;
    }
    
    const submitBtn = event.target.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
    submitBtn.disabled = true;
    
    try {
        const result = await settingsManager.updateEmailSettings(smtpPassword);
        
        if (!result.success) {
            showToast(result.error, 'error');
        }
    } finally {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    }
}

// Enhanced keyboard shortcuts
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Escape to close modals
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal.show').forEach(modal => {
                modal.classList.remove('show');
            });
        }
        
        // Ctrl/Cmd + K to add items
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
        
        // Alt + number for page navigation
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

// Enhanced event listeners setup
function setupEventListeners() {
    // Modal close on background click
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.classList.remove('show');
            }
        });
    });
    
    // Platform select change
    const platformSelect = document.getElementById('platformSelect');
    if (platformSelect) {
        platformSelect.addEventListener('change', updateUrlPlaceholder);
    }
    
    // Alert type change
    const alertTypeSelect = document.getElementById('alertType');
    if (alertTypeSelect) {
        alertTypeSelect.addEventListener('change', updateThresholdLabel);
        updateThresholdLabel(); // Initialize
    }
    
    // Email form submission
    const emailForm = document.getElementById('emailForm');
    if (emailForm) {
        emailForm.addEventListener('submit', handleEmailSettings);
    }
    
    // Auto-uppercase stock symbols
    const stockSymbolInput = document.getElementById('stockSymbol');
    if (stockSymbolInput) {
        stockSymbolInput.addEventListener('input', function(e) {
            e.target.value = e.target.value.toUpperCase();
        });
    }
}

// Page visibility handling for data refresh
function setupVisibilityHandling() {
    document.addEventListener('visibilitychange', function() {
        if (!document.hidden && currentUser) {
            // Page became visible, refresh data
            dataManager.loadStats();
            
            const activePage = document.querySelector('.page.active');
            if (activePage) {
                const pageId = activePage.id;
                if (pageId === 'productsPage' || pageId === 'robloxPage') {
                    dataManager.loadProducts();
                } else if (pageId === 'stocksPage') {
                    dataManager.loadStockAlerts();
                }
            }
        }
    });
}

// Enhanced error handling
function setupErrorHandling() {
    window.addEventListener('error', function(e) {
        console.error('🚫 Global error:', e.error);
        if (e.error?.message?.includes('fetch')) {
            showToast('Network error: Please check your connection and ensure the backend is running.', 'error');
        }
    });

    window.addEventListener('unhandledrejection', function(e) {
        console.error('🚫 Unhandled promise rejection:', e.reason);
        if (e.reason?.message?.includes('fetch')) {
            showToast('Network error: Failed to connect to server.', 'error');
        }
    });
}

// Periodic health check
function startHealthCheck() {
    setInterval(async () => {
        if (currentUser) {
            try {
                const response = await fetch(`${API_URL}/auth/session`, {
                    credentials: 'include',
                    headers: { 'Accept': 'application/json' }
                });
                
                if (!response.ok || response.status === 401) {
                    console.log('🔒 Session expired, redirecting to login');
                    authManager.showAuth();
                }
            } catch (error) {
                console.warn('⚠️ Health check failed:', error);
            }
        }
    }, 300000); // Check every 5 minutes
}

// App initialization
async function initializeApp() {
    console.log('🚀 Initializing TagTracker App...');
    
    try {
        // Initialize theme
        themeManager.init();
        
        // Set up event listeners
        setupEventListeners();
        setupKeyboardShortcuts();
        setupVisibilityHandling();
        setupErrorHandling();
        
        // Check authentication
        await authManager.checkSession();
        
        // Start health monitoring
        startHealthCheck();
        
        console.log('✅ TagTracker initialized successfully');
        
    } catch (error) {
        console.error('❌ App initialization failed:', error);
        showToast('Failed to initialize app. Please refresh the page.', 'error');
    }
}

// Document ready handler
document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 DOM Content Loaded - Starting TagTracker');
    initializeApp();
});

// Service worker registration (future enhancement)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        console.log('🔧 Service Worker support detected');
        // Future: Register service worker for offline functionality
    });
}

console.log('📱 TagTracker App Script Loaded Successfully - REAL SAVINGS EDITION!');