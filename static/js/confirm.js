// State Management
let productData = {};
let originalInput = '';
let currentEditField = '';

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeUserAvatar();
    loadProductData();
});

// Initialize User Avatar
function initializeUserAvatar() {
    const username = sessionStorage.getItem('username') || localStorage.getItem('username') || 'User';
    const avatarElement = document.getElementById('userAvatar');
    
    if (avatarElement) {
        const initials = username.substring(0, 2).toUpperCase();
        avatarElement.textContent = initials;
    }
}

// Load Product Data from Session Storage
function loadProductData() {
    // Get data from session storage (passed from Page 2)
    const dataStr = sessionStorage.getItem('productData');
    const inputStr = sessionStorage.getItem('originalInput');
    
    if (dataStr) {
        try {
            productData = JSON.parse(dataStr);
            originalInput = inputStr || '';
            populateData();
        } catch (e) {
            console.error('Error parsing product data:', e);
            showAlert('Error loading product data. Please go back and try again.', 'error');
            setTimeout(() => {
                window.location.href = '/input-data';
            }, 2000);
        }
    } else {
        // No data found, redirect back to input page
        showAlert('No product data found. Please complete the input form first.', 'warning');
        setTimeout(() => {
            window.location.href = '/input-data';
        }, 2000);
    }
}

// Populate Data in Table
function populateData() {
    // Product Name
    document.getElementById('value-productName').textContent = productData.productName || 'N/A';
    updateSource('productName', productData.source?.productName || 'ai');
    
    // Material Type
    const materialType = productData.materialType || 'N/A';
    document.getElementById('value-materialType').textContent = 
        capitalizeFirstLetter(materialType);
    updateSource('materialType', productData.source?.materialType || 'ai');
    
    // Weight
    const weight = productData.weight || 0;
    const weightUnit = productData.weightUnit || 'kg';
    document.getElementById('value-weight').textContent = `${weight} ${weightUnit}`;
    updateSource('weight', productData.source?.weight || 'ai');
    
    // Recycled Content
    const recycledContent = productData.recycledContent || 0;
    document.getElementById('value-recycledContent').textContent = `${recycledContent}%`;
    updateSource('recycledContent', productData.source?.recycledContent || 'ai');
    
    // Lifecycle Stage
    const lifecycleStage = productData.lifecycleStage || 'Production';
    document.getElementById('value-lifecycleStage').textContent = 
        formatLifecycleStage(lifecycleStage);
    updateSource('lifecycleStage', productData.source?.lifecycleStage || 'default');
    
    // Processing Details
    const processingDetails = productData.processingDetails || 'Not specified';
    document.getElementById('value-processingDetails').textContent = processingDetails;
    updateSource('processingDetails', productData.source?.processingDetails || 'ai');
    
    // Original Input
    document.getElementById('originalInput').textContent = 
        originalInput || 'No original input text available';
}

// Update Source Badge
function updateSource(field, source) {
    const sourceElement = document.getElementById(`source-${field}`);
    if (!sourceElement) return;
    
    const badge = sourceElement;
    
    switch (source.toLowerCase()) {
        case 'ai':
        case 'extracted':
            badge.className = 'badge badge-ai';
            badge.textContent = 'AI Extracted';
            break;
        case 'default':
        case 'system':
            badge.className = 'badge badge-default';
            badge.textContent = 'System Default';
            break;
        case 'openlca':
        case 'database':
            badge.className = 'badge badge-openlca';
            badge.textContent = 'OpenLCA Data';
            break;
        case 'user':
        case 'manual':
            badge.className = 'badge badge-ai';
            badge.textContent = 'User Edited';
            break;
        default:
            badge.className = 'badge badge-ai';
            badge.textContent = 'AI Extracted';
    }
}

// Edit Field
function editField(fieldName) {
    currentEditField = fieldName;
    const modal = document.getElementById('editModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalLabel = document.getElementById('modalLabel');
    const modalInput = document.getElementById('modalInput');
    const modalSelect = document.getElementById('modalSelect');
    const modalLifecycleSelect = document.getElementById('modalLifecycleSelect');
    
    // Reset visibility
    modalInput.style.display = 'block';
    modalSelect.style.display = 'none';
    modalLifecycleSelect.style.display = 'none';
    
    // Set title and label
    modalTitle.textContent = `Edit ${formatFieldName(fieldName)}`;
    modalLabel.textContent = formatFieldName(fieldName);
    
    // Set current value and input type
    switch (fieldName) {
        case 'materialType':
            modalInput.style.display = 'none';
            modalSelect.style.display = 'block';
            modalSelect.value = productData.materialType || 'aluminum';
            break;
            
        case 'lifecycleStage':
            modalInput.style.display = 'none';
            modalLifecycleSelect.style.display = 'block';
            modalLifecycleSelect.value = productData.lifecycleStage || 'manufacturing';
            break;
            
        case 'weight':
            modalInput.value = productData.weight || '';
            modalInput.type = 'number';
            modalInput.step = '0.01';
            modalInput.min = '0';
            break;
            
        case 'recycledContent':
            modalInput.value = productData.recycledContent || '';
            modalInput.type = 'number';
            modalInput.step = '1';
            modalInput.min = '0';
            modalInput.max = '100';
            break;
            
        default:
            modalInput.value = productData[fieldName] || '';
            modalInput.type = 'text';
    }
    
    modal.classList.add('active');
}

// Close Modal
function closeModal() {
    const modal = document.getElementById('editModal');
    modal.classList.remove('active');
    currentEditField = '';
}

// Save Edit
function saveEdit() {
    const modalInput = document.getElementById('modalInput');
    const modalSelect = document.getElementById('modalSelect');
    const modalLifecycleSelect = document.getElementById('modalLifecycleSelect');
    
    let newValue;
    
    // Get new value based on field type
    switch (currentEditField) {
        case 'materialType':
            newValue = modalSelect.value;
            break;
        case 'lifecycleStage':
            newValue = modalLifecycleSelect.value;
            break;
        case 'weight':
        case 'recycledContent':
            newValue = parseFloat(modalInput.value);
            if (isNaN(newValue) || newValue < 0) {
                showAlert('Please enter a valid positive number', 'error');
                return;
            }
            if (currentEditField === 'recycledContent' && newValue > 100) {
                showAlert('Recycled content cannot exceed 100%', 'error');
                return;
            }
            break;
        default:
            newValue = modalInput.value.trim();
            if (!newValue) {
                showAlert('Value cannot be empty', 'error');
                return;
            }
    }
    
    // Update product data
    productData[currentEditField] = newValue;
    
    // Mark as user edited
    if (!productData.source) {
        productData.source = {};
    }
    productData.source[currentEditField] = 'user';
    
    // Update display
    updateFieldDisplay(currentEditField, newValue);
    updateSource(currentEditField, 'user');
    
    // Save to session storage
    sessionStorage.setItem('productData', JSON.stringify(productData));
    
    closeModal();
    showAlert('Value updated successfully', 'success');
}

// Update Field Display
function updateFieldDisplay(field, value) {
    const valueElement = document.getElementById(`value-${field}`);
    
    switch (field) {
        case 'materialType':
            valueElement.textContent = capitalizeFirstLetter(value);
            break;
        case 'weight':
            valueElement.textContent = `${value} ${productData.weightUnit || 'kg'}`;
            break;
        case 'recycledContent':
            valueElement.textContent = `${value}%`;
            break;
        case 'lifecycleStage':
            valueElement.textContent = formatLifecycleStage(value);
            break;
        default:
            valueElement.textContent = value;
    }
}

// Format Field Name
function formatFieldName(fieldName) {
    const names = {
        'productName': 'Product Name',
        'materialType': 'Material Type',
        'weight': 'Weight',
        'recycledContent': 'Recycled Content',
        'lifecycleStage': 'Lifecycle Stage',
        'processingDetails': 'Processing Details'
    };
    return names[fieldName] || fieldName;
}

// Format Lifecycle Stage
function formatLifecycleStage(stage) {
    const stages = {
        'raw-material': 'Raw Material Extraction',
        'manufacturing': 'Manufacturing',
        'production': 'Production',
        'distribution': 'Distribution',
        'use': 'Use Phase',
        'end-of-life': 'End of Life'
    };
    return stages[stage] || capitalizeFirstLetter(stage);
}

// Capitalize First Letter
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

// Go Back to Input Page
function goBack() {
    window.location.href = '/input-data';
}

// Confirm and Continue
async function confirmAndContinue() {
    showLoading();
    
    try {
        // Save confirmed data to session
        sessionStorage.setItem('confirmedData', JSON.stringify(productData));
        
        // Send data to backend for analysis
        const response = await fetch('/api/save-confirmed-data', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                productData: productData,
                dataSource: sessionStorage.getItem('dataSource')
            })
        });
        
        const result = await response.json();
        
        hideLoading();
        
        if (result.success) {
            // Redirect to analysis/results page (Page 4)
            showAlert('Data confirmed! Proceeding to analysis...', 'success');
            setTimeout(() => {
                window.location.href = '/analysis';
            }, 1500);
        } else {
            showAlert(result.message || 'Error saving data', 'error');
        }
    } catch (error) {
        hideLoading();
        console.error('Error:', error);
        showAlert('Error connecting to server. Please try again.', 'error');
    }
}

// Logout
function logout() {
    sessionStorage.clear();
    localStorage.clear();
    window.location.href = '/auth/logout';
}

// Show Loading
function showLoading() {
    const overlay = document.getElementById('loadingOverlay');
    overlay.classList.add('active');
}

// Hide Loading
function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    overlay.classList.remove('active');
}

// Show Alert
function showAlert(message, type = 'info') {
    // Create alert element
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 16px 24px;
        background: ${type === 'success' ? '#10B981' : type === 'error' ? '#EF4444' : '#3B82F6'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 10000;
        animation: slideIn 0.3s ease;
        max-width: 400px;
        font-weight: 600;
    `;
    alert.textContent = message;
    
    document.body.appendChild(alert);
    
    setTimeout(() => {
        alert.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(alert);
        }, 300);
    }, 3000);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeModal();
    }
});

// Close modal on background click
document.getElementById('editModal').addEventListener('click', (e) => {
    if (e.target.id === 'editModal') {
        closeModal();
    }
});
