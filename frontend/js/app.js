// Modern PriceTracker JavaScript with Auto-Refresh and Updated Platforms Including Roblox & Flights

const API_URL = 'http://localhost:5000/api';

// Updated platform configurations with new platforms
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
    },
    roblox: {
        name: 'Roblox UGC',
        exampleUrl: 'https://www.roblox.com/catalog/123456789/Item-Name',
        tips: 'Use the catalog URL for UGC items. Prices shown in Robux.',
        icon: '🎮',
        currency: 'robux'
    },
    flights: {
        name: 'Flight Tickets',
        exampleUrl: 'https://www.kayak.com/flights/NYC-LAX/2024-03-15',
        tips: 'Use flight search result URLs from Kayak, Expedia, or similar sites',
        icon: '✈️'
    }
};

// Auto-refresh state
let autoRefreshInterval = null;
let isChecking = false;

// Page Management
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
    } else if (pageId === 'stocksPage') {
        loadStockAlerts();
        loadStats();
    } else if (pageId === 'monitorPage') {
        loadSchedulerStatus();
        loadStats();
    } else if (pageId === 'settingsPage') {
        loadEmailConfig();
    }
}

// Auto-refresh functionality
function startAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
    }
    
    // Refresh stats every 5 seconds, products/stocks every 30 seconds
    autoRefreshInterval = setInterval(() => {
        if (!isChecking) {
            loadStats();
            
            // Refresh current page data
            const activePage = document.querySelector('.page.active');
            if (activePage) {
                const pageId = activePage.id;
                if (pageId === 'productsPage') {
                    loadProducts();
                } else if (pageId === 'stocksPage') {
                    loadStockAlerts();
                } else if (pageId === 'monitorPage') {
                    loadSchedulerStatus();
                }
            }
        }
    }, 30000); // 30 seconds
    
    // Faster stats refresh
    setInterval(loadStats, 5000); // 5 seconds for stats only
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

// Toast Notifications
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}

// Update URL placeholder based on selected platform
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
        
        // Clear the URL field when switching platforms
        urlInput.value = '';
        
        // Enable the URL input
        urlInput.disabled = false;
        
        // Update target price label for Roblox
        const targetPriceLabel = document.querySelector('label[for="targetPrice"]');
        if (targetPriceLabel) {
            if (config.currency === 'robux') {
                targetPriceLabel.innerHTML = '<i class="fas fa-coins"></i> Target Price (Robux)';
            } else {
                targetPriceLabel.innerHTML = '<i class="fas fa-dollar-sign"></i> Target Price ($)';
            }
        }
    } else {
        urlInput.placeholder = 'Select a platform first...';
        urlHint.textContent = '';
        platformInfo.style.display = 'none';
        urlInput.disabled = true;
    }
}

// Validate URL matches selected platform
function validateProductUrl(url, platform) {
    const domainPatterns = {
        amazon: /amazon\.(com|co\.uk|ca|de|fr|es|it|jp|in|com\.mx|com\.br)/i,
        ebay: /ebay\.(com|co\.uk|ca|de|fr|it|es|com\.au)/i,
        etsy: /etsy\.com/i,
        walmart: /walmart\.com/i,
        storenvy: /storenvy\.com/i,
        roblox: /roblox\.com/i,
        flights: /(kayak|expedia|booking|priceline|momondo)\.com/i
    };
    
    if (!platform || !domainPatterns[platform]) {
        return false;
    }
    
    return domainPatterns[platform].test(url);
}

// Format price based on platform currency
function formatPrice(price, platform) {
    const config = platformConfigs[platform];
    if (config && config.currency === 'robux') {
        return `${Math.round(price)} R$`;
    }
    return `$${price.toFixed(2)}`;
}

// Products Management with Auto-Update
async function loadProducts() {
    try {
        const response = await fetch(`${API_URL}/products`);
        const products = await response.json();
        
        const productsList = document.getElementById('productsList');
        const emptyState = document.getElementById('emptyState');
        
        if (products.length === 0) {
            productsList.style.display = 'none';
            emptyState.style.display = 'block';
        } else {
            productsList.style.display = 'grid';
            emptyState.style.display = 'none';
            
            productsList.innerHTML = products.map(product => {
                const platform = product.platform || 'storenvy';
                const config = platformConfigs[platform] || {};
                const isRobux = config.currency === 'robux';
                
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
                            <i class="fas fa-external-link-alt"></i> View ${isRobux ? 'Item' : 'Product'}
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

function renderProductStatus(product, platform = null) {
    const config = platformConfigs[platform] || {};
    const isRobux = config.currency === 'robux';
    
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
        const savingsText = isRobux ? `${Math.round(savings)} R$` : `$${savings.toFixed(2)}`;
        return `
            <div class="status-badge status-triggered">
                <i class="fas fa-check-circle"></i>
                Target Hit! Save ${savingsText}
            </div>
        `;
    }
    
    return `
        <div class="status-badge status-waiting">
            <i class="fas fa-eye"></i>
            Monitoring Price
        </div>
    `;
}

// Real-time price update function
function updateProductPrice(productId, newPrice, targetPrice, platform = null) {
    const priceElement = document.getElementById(`current-price-${productId}`);
    const statusElement = document.getElementById(`status-${productId}`);
    const cardElement = document.getElementById(`product-${productId}`);
    
    if (priceElement) {
        // Animate price change
        priceElement.style.transition = 'all 0.3s ease';
        priceElement.style.transform = 'scale(1.1)';
        priceElement.textContent = formatPrice(newPrice, platform);
        
        setTimeout(() => {
            priceElement.style.transform = 'scale(1)';
        }, 300);
    }
    
    if (statusElement) {
        const product = { last_price: newPrice, target_price: targetPrice, status: newPrice <= targetPrice ? 'below_target' : 'waiting' };
        statusElement.innerHTML = renderProductStatus(product, platform);
    }
    
    // Add visual feedback for price updates
    if (cardElement) {
        cardElement.style.boxShadow = '0 0 20px rgba(99, 102, 241, 0.3)';
        setTimeout(() => {
            cardElement.style.boxShadow = '';
        }, 2000);
    }
}

// Product Modal Functions
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
    
    // Reset target price label
    const targetPriceLabel = document.querySelector('label[for="targetPrice"]');
    if (targetPriceLabel) {
        targetPriceLabel.innerHTML = '<i class="fas fa-dollar-sign"></i> Target Price';
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
        const config = platformConfigs[platform];
        const priceType = config && config.currency === 'robux' ? 'target price in Robux' : 'target price in dollars';
        showToast(`Please enter a valid URL and ${priceType}`, 'error');
        return;
    }
    
    // Validate URL matches selected platform
    if (!validateProductUrl(url, platform)) {
        showToast(`This URL doesn't appear to be from ${platformConfigs[platform].name}. Please check the URL and platform selection.`, 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/products`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url, target_price: targetPrice })
        });
        
        if (response.ok) {
            const platformName = platformConfigs[platform].name;
            const config = platformConfigs[platform];
            const successMessage = config && config.currency === 'robux' 
                ? `✅ ${platformName} item added successfully! Monitoring will begin shortly.`
                : `✅ ${platformName} product added successfully! Monitoring will begin shortly.`;
            showToast(successMessage);
            closeAddProductModal();
            loadProducts();
            loadStats();
        } else {
            const error = await response.json();
            showToast(error.error || 'Failed to add product', 'error');
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
            method: 'DELETE'
        });
        
        if (response.ok) {
            showToast('Product removed from tracking');
            loadProducts();
            loadStats();
        } else {
            showToast('Failed to remove product', 'error');
        }
    } catch (error) {
        showToast('Network error: Failed to remove product', 'error');
        console.error('Error deleting product:', error);
    }
}

// Stock Management Functions
async function loadStockAlerts() {
    try {
        const response = await fetch(`${API_URL}/stocks`);
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
            <i class="fas fa-radar"></i>
            Monitoring
        </div>
    `;
}

// Real-time stock update function
function updateStockPrice(alertId, newPrice, isTriggered = false) {
    const priceElement = document.getElementById(`stock-price-${alertId}`);
    const statusElement = document.getElementById(`stock-status-${alertId}`);
    const cardElement = document.getElementById(`stock-${alertId}`);
    
    if (priceElement) {
        priceElement.style.transition = 'all 0.3s ease';
        priceElement.style.transform = 'scale(1.1)';
        priceElement.textContent = `${newPrice.toFixed(2)}`;
        
        setTimeout(() => {
            priceElement.style.transform = 'scale(1)';
        }, 300);
    }
    
    if (statusElement) {
        const alert = { current_price: newPrice, is_triggered: isTriggered };
        statusElement.innerHTML = renderStockStatus(alert);
    }
    
    if (cardElement) {
        cardElement.style.boxShadow = '0 0 20px rgba(16, 185, 129, 0.3)';
        setTimeout(() => {
            cardElement.style.boxShadow = '';
        }, 2000);
    }
}

// Statistics with Real-time Updates
async function loadStats() {
    try {
        const response = await fetch(`${API_URL}/stats`);
        const stats = await response.json();
        
        // Animate stats updates
        updateStatWithAnimation('totalProducts', stats.total_products || 0);
        updateStatWithAnimation('totalStockAlerts', stats.total_stock_alerts || 0);
        updateStatWithAnimation('triggeredAlerts', stats.triggered_stock_alerts || 0);
        updateStatWithAnimation('totalSavings', `${(stats.total_savings || 0).toFixed(2)}`);
        
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

function updateStatWithAnimation(elementId, newValue) {
    const element = document.getElementById(elementId);
    if (element && element.textContent !== newValue.toString()) {
        element.style.transition = 'all 0.3s ease';
        element.style.transform = 'scale(1.1)';
        element.textContent = newValue;
        
        setTimeout(() => {
            element.style.transform = 'scale(1)';
        }, 300);
    }
}

// Stock Modal Functions
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
            },
            body: JSON.stringify({ 
                symbol: symbol, 
                alert_type: alertType, 
                threshold: threshold 
            })
        });
        
        if (response.ok) {
            showToast(`🚨 Stock alert created for ${symbol}! You'll be notified when conditions are met.`);
            closeAddStockModal();
            loadStockAlerts();
            loadStats();
        } else {
            const error = await response.json();
            showToast(error.error || 'Failed to create stock alert', 'error');
        }
    } catch (error) {
        showToast('Network error: Failed to create stock alert', 'error');
        console.error('Error adding stock alert:', error);
    }
}

async function deleteStockAlert(alertId) {
    if (!confirm('Are you sure you want to delete this stock alert?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/stocks/${alertId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showToast('Stock alert deleted');
            loadStockAlerts();
            loadStats();
        } else {
            showToast('Failed to delete stock alert', 'error');
        }
    } catch (error) {
        showToast('Network error: Failed to delete stock alert', 'error');
        console.error('Error deleting stock alert:', error);
    }
}

// Enhanced Monitor Page Functions with Real-time Updates
async function checkPrices() {
    if (isChecking) {
        showToast('Price check already in progress', 'warning');
        return;
    }
    
    isChecking = true;
    const button = document.getElementById('checkPricesBtn');
    const status = document.getElementById('checkingStatus');
    
    button.style.display = 'none';
    status.style.display = 'block';
    
    try {
        showToast('🔄 Starting comprehensive price check...', 'success');
        
        // Check both products and stocks simultaneously
        const [productsResponse, stocksResponse] = await Promise.all([
            fetch(`${API_URL}/check-prices`, { method: 'POST' }),
            fetch(`${API_URL}/stocks/check`, { method: 'POST' })
        ]);
        
        let successCount = 0;
        let errorMessages = [];
        
        if (productsResponse.ok) {
            const productData = await productsResponse.json();
            successCount++;
            
            // Real-time update products if response contains updated data
            if (productData.products) {
                productData.products.forEach(product => {
                    if (product.last_price) {
                        const platform = product.platform || 'storenvy';
                        updateProductPrice(product.id, product.last_price, product.target_price, platform);
                    }
                });
            }
        } else {
            errorMessages.push('Product price check failed');
        }
        
        if (stocksResponse.ok) {
            const stockData = await stocksResponse.json();
            successCount++;
            
            // Real-time update stocks if response contains updated data
            if (stockData.alerts) {
                stockData.alerts.forEach(alert => {
                    if (alert.current_price) {
                        updateStockPrice(alert.id, alert.current_price, alert.is_triggered);
                    }
                });
            }
        } else {
            errorMessages.push('Stock price check failed');
        }
        
        if (successCount === 2) {
            showToast('✅ All prices checked successfully! Check your alerts for updates.');
        } else if (successCount === 1) {
            showToast(`⚠️ Partial success: ${errorMessages.join(', ')}`, 'error');
        } else {
            showToast('❌ Price check failed. Please try again.', 'error');
        }
        
        // Refresh data
        setTimeout(() => {
            loadProducts();
            loadStockAlerts();
            loadStats();
        }, 2000);
        
    } catch (error) {
        showToast('Network error: Failed to check prices', 'error');
        console.error('Error checking prices:', error);
    } finally {
        isChecking = false;
        button.style.display = 'inline-flex';
        status.style.display = 'none';
    }
}

// Scheduler Functions
async function loadSchedulerStatus() {
    try {
        const response = await fetch(`${API_URL}/scheduler/status`);
        const status = await response.json();
        
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        
        if (status.running) {
            statusDot.classList.add('active');
            statusText.textContent = 'Background monitoring is active';
            startBtn.style.display = 'none';
            stopBtn.style.display = 'inline-flex';
        } else {
            statusDot.classList.remove('active');
            statusText.textContent = 'Background monitoring is inactive';
            startBtn.style.display = 'inline-flex';
            stopBtn.style.display = 'none';
        }
        
    } catch (error) {
        console.error('Failed to load scheduler status:', error);
        document.getElementById('statusText').textContent = 'Status unknown';
    }
}

async function startScheduler() {
    try {
        const response = await fetch(`${API_URL}/scheduler/start`, { method: 'POST' });
        
        if (response.ok) {
            showToast('🚀 Background monitoring started! Your items will be checked automatically.');
            loadSchedulerStatus();
        } else {
            showToast('Failed to start background monitoring', 'error');
        }
    } catch (error) {
        showToast('Network error: Failed to start monitoring', 'error');
        console.error('Error starting scheduler:', error);
    }
}

async function stopScheduler() {
    if (!confirm('Are you sure you want to stop background monitoring?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/scheduler/stop`, { method: 'POST' });
        
        if (response.ok) {
            showToast('⏹️ Background monitoring stopped');
            loadSchedulerStatus();
        } else {
            showToast('Failed to stop background monitoring', 'error');
        }
    } catch (error) {
        showToast('Network error: Failed to stop monitoring', 'error');
        console.error('Error stopping scheduler:', error);
    }
}

// Email Configuration
async function loadEmailConfig() {
    try {
        const response = await fetch(`${API_URL}/email-config`);
        const config = await response.json();
        
        const emailEnabled = document.getElementById('emailEnabled');
        const emailSettings = document.getElementById('emailSettings');
        
        emailEnabled.checked = config.enabled;
        emailSettings.style.display = config.enabled ? 'block' : 'none';
        
        // Load existing values if they exist
        if (config.enabled) {
            // Note: We don't load sensitive data like passwords for security
            document.getElementById('smtpServer').value = config.smtp_server || '';
            document.getElementById('smtpPort').value = config.smtp_port || 587;
            document.getElementById('fromEmail').value = config.from_email || '';
            document.getElementById('toEmail').value = config.to_email || '';
        }
        
    } catch (error) {
        console.error('Failed to load email config:', error);
    }
}

// Utility Functions
function truncateUrl(url) {
    if (url.length <= 50) return url;
    return url.substring(0, 47) + '...';
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

function formatDate(dateString) {
    if (!dateString) return 'Never';
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Disable URL input initially
    const urlInput = document.getElementById('productUrl');
    if (urlInput) {
        urlInput.disabled = true;
    }
    
    // Set up alert type change listener
    const alertTypeSelect = document.getElementById('alertType');
    if (alertTypeSelect) {
        alertTypeSelect.addEventListener('change', updateThresholdLabel);
    }
    
    // Set up email toggle
    const emailEnabled = document.getElementById('emailEnabled');
    if (emailEnabled) {
        emailEnabled.addEventListener('change', function() {
            document.getElementById('emailSettings').style.display = this.checked ? 'block' : 'none';
        });
    }
    
    // Set up email form submission
    const emailForm = document.getElementById('emailForm');
    if (emailForm) {
        emailForm.addEventListener('submit', async function(event) {
            event.preventDefault();
            
            const config = {
                enabled: document.getElementById('emailEnabled').checked,
                smtp_server: document.getElementById('smtpServer').value,
                smtp_port: parseInt(document.getElementById('smtpPort').value),
                from_email: document.getElementById('fromEmail').value,
                password: document.getElementById('password').value,
                to_email: document.getElementById('toEmail').value
            };
            
            try {
                const response = await fetch(`${API_URL}/email-config`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(config)
                });
                
                if (response.ok) {
                    showToast('📧 Email settings saved successfully!');
                    // Clear password field for security
                    document.getElementById('password').value = '';
                } else {
                    showToast('Failed to save email settings', 'error');
                }
            } catch (error) {
                showToast('Network error: Failed to save email settings', 'error');
                console.error('Error saving email config:', error);
            }
        });
    }
    
    // Set up modal close on backdrop click
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', function(event) {
            if (event.target === modal) {
                modal.classList.remove('show');
            }
        });
    });
    
    // Set up keyboard shortcuts
    document.addEventListener('keydown', function(event) {
        // ESC to close modals
        if (event.key === 'Escape') {
            document.querySelectorAll('.modal.show').forEach(modal => {
                modal.classList.remove('show');
            });
        }
        
        // Ctrl/Cmd + Enter to submit forms
        if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
            const activeModal = document.querySelector('.modal.show');
            if (activeModal) {
                const form = activeModal.querySelector('form');
                if (form) {
                    form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
                }
            }
        }
    });
    
    // Load initial data
    loadProducts();
    loadStats();
    
    // Start auto-refresh functionality
    startAutoRefresh();
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', function() {
        stopAutoRefresh();
    });
});