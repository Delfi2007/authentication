// API Configuration
const OPENLCA_API_URL = 'http://localhost:8080';
const API_ENDPOINTS = {
    checkOpenLCA: '/api/check-openlca',
    getDatasets: '/api/datasets',
    uploadDataset: '/api/upload-dataset'
};

// State Management
let selectedOption = null;
let selectedDataSource = 'openlca';

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    checkOpenLCAStatus();
    initializeDataSourceSelection();
    initializeUserAvatar();
});

// Check OpenLCA API Status
async function checkOpenLCAStatus() {
    const statusBadge = document.getElementById('openlcaStatus');
    
    try {
        const response = await fetch(API_ENDPOINTS.checkOpenLCA);
        const result = await response.json();
        
        if (result.available) {
            statusBadge.textContent = 'Available';
            statusBadge.className = 'status-badge available';
            console.log('OpenLCA API is available');
        } else {
            statusBadge.textContent = 'Offline';
            statusBadge.className = 'status-badge unavailable';
            console.log('OpenLCA API is not available');
        }
    } catch (error) {
        statusBadge.textContent = 'Offline';
        statusBadge.className = 'status-badge unavailable';
        console.error('Error checking OpenLCA status:', error);
    }
}

// Initialize Data Source Selection
function initializeDataSourceSelection() {
    const radioButtons = document.querySelectorAll('input[name="dataSource"]');
    
    radioButtons.forEach(radio => {
        radio.addEventListener('change', (e) => {
            selectedDataSource = e.target.value;
            console.log('Selected data source:', selectedDataSource);
        });
    });
}

// Initialize User Avatar
function initializeUserAvatar() {
    // Get username from session or local storage
    const username = sessionStorage.getItem('username') || localStorage.getItem('username') || 'User';
    const avatarElement = document.getElementById('userAvatar');
    
    // Set initials
    const initials = username.substring(0, 2).toUpperCase();
    avatarElement.textContent = initials;
}

// Select Option Handler
function selectOption(option) {
    selectedOption = option;
    
    if (option === 'upload') {
        handleUploadOption();
    } else if (option === 'default') {
        handleDefaultOption();
    }
}

// Handle Upload Option
function handleUploadOption() {
    // Create file input
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.csv,.xlsx,.xls,.json,.xml';
    fileInput.multiple = true;
    
    fileInput.onchange = async (e) => {
        const files = Array.from(e.target.files);
        
        if (files.length === 0) return;
        
        showLoading();
        
        try {
            const formData = new FormData();
            files.forEach(file => {
                formData.append('files', file);
            });
            
            const response = await fetch(API_ENDPOINTS.uploadDataset, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            hideLoading();
            
            if (result.success) {
                showAlert('Files uploaded successfully!', 'success');
                setTimeout(() => {
                    proceedToNext();
                }, 1500);
            } else {
                showAlert(result.message || 'Upload failed. Please try again.', 'error');
            }
        } catch (error) {
            hideLoading();
            console.error('Upload error:', error);
            showAlert('An error occurred during upload. Please try again.', 'error');
        }
    };
    
    fileInput.click();
}

// Handle Default Option
async function handleDefaultOption() {
    showLoading();
    
    try {
        // Store selected data source
        sessionStorage.setItem('dataSource', selectedDataSource);
        
        // Fetch dataset metadata
        const response = await fetch(`${API_ENDPOINTS.getDatasets}?source=${selectedDataSource}`);
        const result = await response.json();
        
        hideLoading();
        
        if (result.success) {
            showAlert(`${getDataSourceName(selectedDataSource)} dataset loaded successfully!`, 'success');
            setTimeout(() => {
                proceedToNext();
            }, 1500);
        } else {
            showAlert(result.message || 'Failed to load dataset. Please try again.', 'error');
        }
    } catch (error) {
        hideLoading();
        console.error('Dataset loading error:', error);
        showAlert('An error occurred. Please try again.', 'error');
    }
}

// Get Data Source Name
function getDataSourceName(source) {
    const names = {
        'openlca': 'OpenLCA',
        'ecoinvent': 'Ecoinvent',
        'indian': 'Indian LCA',
        'builtin': 'Built-in'
    };
    return names[source] || 'Default';
}

// Proceed to Next Page
function proceedToNext() {
    if (!selectedOption) {
        selectedOption = 'default';
        selectedDataSource = document.querySelector('input[name="dataSource"]:checked').value;
    }
    
    // Store selections
    sessionStorage.setItem('selectedOption', selectedOption);
    sessionStorage.setItem('dataSource', selectedDataSource);
    
    // Redirect to next page (Input Data)
    window.location.href = '/input-data';
}

// Show Loading
function showLoading() {
    document.getElementById('loadingOverlay').classList.remove('hidden');
}

// Hide Loading
function hideLoading() {
    document.getElementById('loadingOverlay').classList.add('hidden');
}

// Show Alert
function showAlert(message, type = 'success') {
    const alertBox = document.getElementById('alertBox');
    const alertMessage = document.getElementById('alertMessage');
    
    alertMessage.textContent = message;
    alertBox.className = `alert ${type}`;
    alertBox.classList.remove('hidden');
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        closeAlert();
    }, 5000);
}

// Close Alert
function closeAlert() {
    document.getElementById('alertBox').classList.add('hidden');
}

// Periodic OpenLCA Status Check
setInterval(checkOpenLCAStatus, 30000); // Check every 30 seconds
