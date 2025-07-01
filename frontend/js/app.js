// frontend/js/app.js

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
    } else if (pageId === 'emailPage') {
        loadEmailConfig();
    } else if (pageId === 'schedulePage') {
        loadSchedulerStatus();
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
    }, 3000);
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
                <div class="product-card">
                    <h3 class="product-title">${product.title || 'Loading...'}</h3>
                    <p class="product-url">${product.url}</p>
                    
                    <div class="price-info">
                        <div class="price-item">
                            <span class="price-label">Current</span>
                            <span class="price-value">$${product.last_price ? product.last_price.toFixed(2) : '--'}</span>
                        </div>
                        <div class="price-item">
                            <span class="price-label">Target</span>
                            <span class="price-value">$${product.target_price.toFixed(2)}</span>
                        </div>
                    </div>
                    
                    ${product.last_price ? `
                        <div class="product-status ${product.status === 'below_target' ? 'status-below' : 'status-waiting'}">
                            <i class="fas ${product.status === 'below_target' ? 'fa-check-circle' : 'fa-clock'}"></i>
                            ${product.status === 'below_target' ? 'Below Target!' : 'Waiting for Drop'}
                        </div>
                    ` : '<div class="product-status status-waiting"><i class="fas fa-clock"></i> Not Checked Yet</div>'}
                    
                    <div class="product-actions">
                        <a href="${product.url}" target="_blank" class="btn btn-primary btn-icon">
                            <i class="fas fa-external-link-alt"></i> View
                        </a>
                        <button onclick="deleteProduct(${product.id})" class="btn btn-secondary btn-icon">
                            <i class="fas fa-trash"></i> Delete
                        </button>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        showToast('Failed to load products', 'error');
    }
}

async function loadStats() {
    try {
        const response = await fetch(`${API_URL}/stats`);
        const stats = await response.json();
        
        document.getElementById('totalProducts').textContent = stats.total_products;
        document.getElementById('belowTarget').textContent = stats.products_below_target;
        document.getElementById('totalSavings').textContent = `$${stats.total_savings.toFixed(2)}`;
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

// Add Product Modal
function showAddProductModal() {
    document.getElementById('addProductModal').classList.add('show');
}

function closeAddProductModal() {
    document.getElementById('addProductModal').classList.remove('show');
    document.getElementById('addProductForm').reset();
}

async function addProduct(event) {
    event.preventDefault();
    
    const url = document.getElementById('productUrl').value;
    const targetPrice = document.getElementById('targetPrice').value;
    
    try {
        const response = await fetch(`${API_URL}/products`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url, target_price: targetPrice })
        });
        
        if (response.ok) {
            showToast('Product added successfully!');
            closeAddProductModal();
            loadProducts();
            loadStats();
        } else {
            const error = await response.json();
            showToast(error.error || 'Failed to add product', 'error');
        }
    } catch (error) {
        showToast('Failed to add product', 'error');
    }
}

async function deleteProduct(productId) {
    if (!confirm('Are you sure you want to delete this product?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/products/${productId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showToast('Product deleted successfully!');
            loadProducts();
            loadStats();
        } else {
            showToast('Failed to delete product', 'error');
        }
    } catch (error) {
        showToast('Failed to delete product', 'error');
    }
}

// Price Checking
async function checkPrices() {
    const button = document.getElementById('checkPricesBtn');
    const status = document.getElementById('checkingStatus');
    
    button.style.display = 'none';
    status.style.display = 'block';
    
    try {
        const response = await fetch(`${API_URL}/check-prices`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showToast('Price check completed!');
            loadProducts();
            loadStats();
        } else {
            showToast('Failed to check prices', 'error');
        }
    } catch (error) {
        showToast('Failed to check prices', 'error');
    } finally {
        button.style.display = 'inline-flex';
        status.style.display = 'none';
    }
}

// Email Configuration
async function loadEmailConfig() {
    try {
        const response = await fetch(`${API_URL}/email-config`);
        const config = await response.json();
        
        document.getElementById('emailEnabled').checked = config.enabled;
        document.getElementById('emailSettings').style.display = config.enabled ? 'block' : 'none';
    } catch (error) {
        console.error('Failed to load email config:', error);
    }
}

document.getElementById('emailEnabled').addEventListener('change', function() {
    document.getElementById('emailSettings').style.display = this.checked ? 'block' : 'none';
});

document.getElementById('emailForm').addEventListener('submit', async function(event) {
    event.preventDefault();
    
    const config = {
        enabled: document.getElementById('emailEnabled').checked,
        smtp_server: document.getElementById('smtpServer').value,
        smtp_port: document.getElementById('smtpPort').value,
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
            showToast('Email settings saved!');
        } else {
            showToast('Failed to save email settings', 'error');
        }
    } catch (error) {
        showToast('Failed to save email settings', 'error');
    }
});

// Scheduler
async function loadSchedulerStatus() {
    try {
        const response = await fetch(`${API_URL}/scheduler/status`);
        const status = await response.json();
        
        updateSchedulerUI(status.running);
    } catch (error) {
        console.error('Failed to load scheduler status:', error);
    }
}

function updateSchedulerUI(running) {
    const statusIndicator = document.getElementById('statusIndicator');
    const statusDot = statusIndicator.querySelector('.status-dot');
    const statusText = statusIndicator.querySelector('.status-text');
    const startBtn = document.getElementById('startSchedulerBtn');
    const stopBtn = document.getElementById('stopSchedulerBtn');
    
    if (running) {
        statusDot.classList.add('active');
        statusText.textContent = 'Scheduler Active';
        startBtn.style.display = 'none';
        stopBtn.style.display = 'inline-flex';
    } else {
        statusDot.classList.remove('active');
        statusText.textContent = 'Scheduler Inactive';
        startBtn.style.display = 'inline-flex';
        stopBtn.style.display = 'none';
    }
}

async function startScheduler() {
    try {
        const response = await fetch(`${API_URL}/scheduler/start`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showToast('Scheduler started!');
            updateSchedulerUI(true);
        } else {
            showToast('Failed to start scheduler', 'error');
        }
    } catch (error) {
        showToast('Failed to start scheduler', 'error');
    }
}

async function stopScheduler() {
    try {
        const response = await fetch(`${API_URL}/scheduler/stop`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showToast('Scheduler stopped!');
            updateSchedulerUI(false);
        } else {
            showToast('Failed to stop scheduler', 'error');
        }
    } catch (error) {
        showToast('Failed to stop scheduler', 'error');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    loadProducts();
    loadStats();
});