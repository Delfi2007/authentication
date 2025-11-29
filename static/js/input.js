// Configuration
const API_ENDPOINTS = {
    analyzeNLP: '/api/analyze-nlp',
    analyzeStructured: '/api/analyze-structured',
    gapFill: '/api/gap-fill',
    getOpenLCAData: '/api/openlca-data'
};

// State Management
let currentMode = 'nlp'; // 'nlp' or 'form'
let extractedData = null;
let datasetSource = sessionStorage.getItem('dataSource') || 'builtin';

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeUserAvatar();
    loadSavedData();
});

// Initialize User Avatar
function initializeUserAvatar() {
    const username = sessionStorage.getItem('username') || localStorage.getItem('username') || 'User';
    const avatarElement = document.getElementById('userAvatar');
    const initials = username.substring(0, 2).toUpperCase();
    avatarElement.textContent = initials;
}

// Switch Input Mode
function switchMode(mode) {
    currentMode = mode;
    
    const nlpMode = document.getElementById('nlpMode');
    const formMode = document.getElementById('formMode');
    const nlpToggle = document.getElementById('nlpToggle');
    const formToggle = document.getElementById('formToggle');
    
    if (mode === 'nlp') {
        nlpMode.classList.remove('hidden');
        formMode.classList.add('hidden');
        nlpToggle.classList.add('active');
        formToggle.classList.remove('active');
    } else {
        formMode.classList.remove('hidden');
        nlpMode.classList.add('hidden');
        formToggle.classList.add('active');
        nlpToggle.classList.remove('active');
    }
}

// Fill Example
function fillExample(text) {
    document.getElementById('nlpInput').value = text;
}

// Update Slider Value
function updateSliderValue(slider) {
    const value = slider.value;
    document.getElementById('recycledValue').textContent = value + '%';
}

// Analyze NLP Input
async function analyzeNLP() {
    const nlpText = document.getElementById('nlpInput').value.trim();
    
    if (!nlpText) {
        showAlert('Please describe your product first', 'warning');
        return;
    }
    
    showLoading('Analyzing your product description...', 'Using AI to extract product details');
    
    try {
        const response = await fetch(API_ENDPOINTS.analyzeNLP, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: nlpText,
                dataSource: datasetSource
            })
        });
        
        const result = await response.json();
        
        hideLoading();
        
        if (result.success) {
            extractedData = result.data;
            
            // Check for missing data and perform gap filling
            if (result.missingData && result.missingData.length > 0) {
                showAlert('Some data is missing. Performing gap filling...', 'warning');
                await performGapFilling(extractedData, result.missingData);
            } else {
                showAlert('Product analyzed successfully!', 'success');
                setTimeout(() => {
                    proceedToConfirm(extractedData);
                }, 1500);
            }
        } else {
            showAlert(result.message || 'Analysis failed. Please try again.', 'error');
        }
    } catch (error) {
        hideLoading();
        console.error('NLP Analysis error:', error);
        showAlert('An error occurred during analysis. Please try again.', 'error');
    }
}

// Analyze Structured Form
async function analyzeStructured() {
    const formData = {
        productName: document.getElementById('productName').value,
        recycledContent: parseInt(document.getElementById('recycledSlider').value),
        weight: parseFloat(document.getElementById('weight').value),
        materialType: document.getElementById('materialType').value,
        lifecycleStage: document.getElementById('lifecycleStage').value,
        processingDetails: document.getElementById('processingDetails').value,
        dataSource: datasetSource
    };
    
    // Validate required fields
    if (!formData.productName || !formData.weight || !formData.materialType || !formData.lifecycleStage) {
        showAlert('Please fill in all required fields', 'warning');
        return;
    }
    
    showLoading('Calculating environmental impact...', 'Processing your product data');
    
    try {
        const response = await fetch(API_ENDPOINTS.analyzeStructured, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        hideLoading();
        
        if (result.success) {
            extractedData = result.data;
            
            // Check for missing data and perform gap filling
            if (result.missingData && result.missingData.length > 0) {
                showAlert('Filling missing data using OpenLCA database...', 'warning');
                await performGapFilling(extractedData, result.missingData);
            } else {
                showAlert('Impact calculated successfully!', 'success');
                setTimeout(() => {
                    proceedToConfirm(extractedData);
                }, 1500);
            }
        } else {
            showAlert(result.message || 'Calculation failed. Please try again.', 'error');
        }
    } catch (error) {
        hideLoading();
        console.error('Structured analysis error:', error);
        showAlert('An error occurred during calculation. Please try again.', 'error');
    }
}

// Perform Gap Filling
async function performGapFilling(data, missingFields) {
    showLoading('Filling missing data...', 'Using AI and OpenLCA database');
    
    try {
        const response = await fetch(API_ENDPOINTS.gapFill, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                data: data,
                missingFields: missingFields,
                dataSource: datasetSource
            })
        });
        
        const result = await response.json();
        
        hideLoading();
        
        if (result.success) {
            extractedData = result.data;
            showAlert('Missing data filled successfully!', 'success');
            setTimeout(() => {
                proceedToConfirm(extractedData);
            }, 1500);
        } else {
            showAlert(result.message || 'Gap filling failed. Please review your data.', 'error');
        }
    } catch (error) {
        hideLoading();
        console.error('Gap filling error:', error);
        showAlert('Gap filling encountered an error. Proceeding with available data.', 'warning');
        setTimeout(() => {
            proceedToConfirm(extractedData);
        }, 1500);
    }
}

// Proceed to Confirm Page
function proceedToConfirm(data) {
    // Store data in session
    sessionStorage.setItem('productData', JSON.stringify(data));
    
    // Redirect to confirmation page
    window.location.href = '/confirm-data';
}

// Load Saved Data
function loadSavedData() {
    const savedData = sessionStorage.getItem('productData');
    if (savedData) {
        try {
            extractedData = JSON.parse(savedData);
            // Optionally pre-fill form if user comes back
        } catch (e) {
            console.error('Error loading saved data:', e);
        }
    }
}

// Show Loading
function showLoading(mainText, subText) {
    const overlay = document.getElementById('loadingOverlay');
    document.getElementById('loadingText').textContent = mainText || 'Processing...';
    document.getElementById('loadingSubtext').textContent = subText || 'Please wait';
    overlay.classList.remove('hidden');
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

// Auto-save form data
let autoSaveTimeout;
document.addEventListener('input', (e) => {
    if (e.target.matches('input, textarea, select')) {
        clearTimeout(autoSaveTimeout);
        autoSaveTimeout = setTimeout(() => {
            // Auto-save logic here
            console.log('Auto-saving form data...');
        }, 2000);
    }
});
