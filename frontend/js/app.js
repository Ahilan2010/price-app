// Modern PriceTracker JavaScript

const API_URL = 'http://localhost:5000/api';

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

// Products Management
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
            
            productsList.innerHTML = products.map(product => `
                <div class="card">
                    <h3 class="card-title">${product.title || 'Loading product details...'}</h3>
                    <p class="card-subtitle">${truncateUrl(product.url)}</p>
                    
                    <div class="price-info">
                        <div class="price-item">
                            <span class="price-label">Current Price</span>
                            <span class="price-value">$${product.last_price ? product.last_price.toFixed(2) : '--'}</span>
                        </div>
                        <div class="price-item">
                            <span class="price-label">Target Price</span>
                            <span class="price-value">$${product.target_price.toFixed(2)}</span>
                        </div>
                    </div>
                    
                    ${renderProductStatus(product)}
                    
                    <div class="card-actions">
                        <a href="${product.url}" target="_blank" class="btn btn-primary btn-icon">
                            <i class="fas fa-external-link-alt"></i> View Product
                        </a>
                        <button onclick="deleteProduct(${product.id})" class="btn btn-secondary btn-icon">
                            <i class="fas fa-trash"></i> Remove
                        </button>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        showToast('Failed to load products', 'error');
        console.error('Error loading products:', error);
    }
}

function renderProductStatus(product) {
    if (!product.last_price) {
        return `
            <div class="status-badge status-waiting">
                <i class="fas fa-clock"></i>
                Not Checked Yet
            </div>
        `;
    }
    
    if (product.status === 'below_target') {
        const savings = (product.target_price - product.last_price).toFixed(2);
        return `
            <div class="status-badge status-triggered">
                <i class="fas fa-check-circle"></i>
                Target Hit! Save $${savings}
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
                <div class="card">
                    <h3 class="card-title">
                        <i class="fas fa-chart-line"></i>
                        ${alert.company_name} (${alert.symbol})
                    </h3>
                    <p class="card-subtitle">${formatAlertDescription(alert)}</p>
                    
                    <div class="price-info">
                        <div class="price-item">
                            <span class="price-label">Current Price</span>
                            <span class="price-value">$${alert.current_price ? alert.current_price.toFixed(2) : '--'}</span>
                        </div>
                        <div class="price-item">
                            <span class="price-label">Threshold</span>
                            <span class="price-value">${formatThreshold(alert)}</span>
                        </div>
                    </div>
                    
                    ${renderStockStatus(alert)}
                    
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

// Statistics
async function loadStats() {
    try {
        const response = await fetch(`${API_URL}/stats`);
        const stats = await response.json();
        
        document.getElementById('totalProducts').textContent = stats.total_products || 0;
        document.getElementById('totalStockAlerts').textContent = stats.total_stock_alerts || 0;
        document.getElementById('triggeredAlerts').textContent = stats.triggered_stock_alerts || 0;
        document.getElementById('totalSavings').textContent = `${(stats.total_savings || 0).toFixed(2)}`;
        
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

// Product Modal Functions
function showAddProductModal() {
    document.getElementById('addProductModal').classList.add('show');
    document.getElementById('productUrl').focus();
}

function closeAddProductModal() {
    document.getElementById('addProductModal').classList.remove('show');
    document.getElementById('addProductForm').reset();
}

async function addProduct(event) {
    event.preventDefault();
    
    const url = document.getElementById('productUrl').value.trim();
    const targetPrice = parseFloat(document.getElementById('targetPrice').value);
    
    if (!url || !targetPrice || targetPrice <= 0) {
        showToast('Please enter a valid URL and target price', 'error');
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
            showToast('✅ Product added successfully! Monitoring will begin shortly.');
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

// Monitor Page Functions
async function checkPrices() {
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
            successCount++;
        } else {
            errorMessages.push('Product price check failed');
        }
        
        if (stocksResponse.ok) {
            successCount++;
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
        loadProducts();
        loadStockAlerts();
        loadStats();
        
    } catch (error) {
        showToast('Network error: Failed to check prices', 'error');
        console.error('Error checking prices:', error);
    } finally {
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
    
    // Set up periodic stats refresh (every 30 seconds)
    setInterval(loadStats, 30000);
});