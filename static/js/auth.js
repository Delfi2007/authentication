// Toggle between Login and Sign Up forms
const loginToggle = document.getElementById('loginToggle');
const signupToggle = document.getElementById('signupToggle');
const loginForm = document.getElementById('loginForm');
const signupForm = document.getElementById('signupForm');
const subtitle = document.getElementById('subtitle');
const footerText = document.getElementById('footerText');
const footerLink = document.getElementById('footerLink');

let currentMode = 'login'; // 'login' or 'signup'
let stream = null;
let facialMode = null; // 'login' or 'signup'

// Toggle to Login
loginToggle.addEventListener('click', () => {
    currentMode = 'login';
    loginToggle.classList.add('active');
    signupToggle.classList.remove('active');
    loginForm.classList.remove('hidden');
    signupForm.classList.add('hidden');
    subtitle.textContent = 'Login to your account';
    footerText.innerHTML = 'Don\'t have an account? <a href="#" id="footerLink">Sign Up</a>';
    attachFooterLinkEvent();
});

// Toggle to Sign Up
signupToggle.addEventListener('click', () => {
    currentMode = 'signup';
    signupToggle.classList.add('active');
    loginToggle.classList.remove('active');
    signupForm.classList.remove('hidden');
    loginForm.classList.add('hidden');
    subtitle.textContent = 'Create your account';
    footerText.innerHTML = 'Already have an account? <a href="#" id="footerLink">Login</a>';
    attachFooterLinkEvent();
});

// Footer link toggle
function attachFooterLinkEvent() {
    const link = document.getElementById('footerLink');
    link.addEventListener('click', (e) => {
        e.preventDefault();
        if (currentMode === 'login') {
            signupToggle.click();
        } else {
            loginToggle.click();
        }
    });
}

attachFooterLinkEvent();

// Password visibility toggle
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const icon = input.nextElementSibling;
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

// Google Login
function loginWithGoogle() {
    showLoading();
    // Redirect to Google OAuth endpoint
    window.location.href = '/auth/google';
}

// Facial Login
function facialLogin() {
    facialMode = 'login';
    openFacialModal('Facial Login');
}

// Facial Signup
function facialSignup() {
    // Prompt for username first
    const username = prompt('Please enter a username for facial registration:');
    
    if (!username || username.trim() === '') {
        showAlert('Username is required for facial signup', 'warning');
        return;
    }
    
    // Store username in session storage
    sessionStorage.setItem('facial_signup_username', username.trim());
    
    facialMode = 'signup';
    openFacialModal('Facial Signup - ' + username.trim());
}

// Open Facial Authentication Modal
function openFacialModal(title) {
    const modal = document.getElementById('facialModal');
    const modalTitle = document.getElementById('modalTitle');
    const video = document.getElementById('video');
    
    modalTitle.textContent = title;
    modal.classList.remove('hidden');
    
    // Start camera
    startCamera();
}

// Close Facial Modal
function closeFacialModal() {
    const modal = document.getElementById('facialModal');
    modal.classList.add('hidden');
    
    // Stop camera
    stopCamera();
}

// Start Camera
async function startCamera() {
    const video = document.getElementById('video');
    
    try {
        stream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                width: { ideal: 640 },
                height: { ideal: 480 },
                facingMode: 'user'
            } 
        });
        video.srcObject = stream;
    } catch (error) {
        console.error('Error accessing camera:', error);
        showAlert('Unable to access camera. Please check permissions.', 'error');
        closeFacialModal();
    }
}

// Stop Camera
function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
}

// Capture Image
async function captureImage() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');
    
    // Set canvas dimensions to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Draw video frame to canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Convert canvas to blob
    canvas.toBlob(async (blob) => {
        showLoading();
        closeFacialModal();
        
        // Send image to server
        const formData = new FormData();
        formData.append('image', blob, 'face.jpg');
        formData.append('mode', facialMode);
        
        // Add username for signup
        if (facialMode === 'signup') {
            const username = sessionStorage.getItem('facial_signup_username');
            if (username) {
                formData.append('username', username);
                sessionStorage.removeItem('facial_signup_username');
            }
        }
        
        try {
            const endpoint = facialMode === 'login' ? '/face-login' : '/face-signup';
            const response = await fetch(endpoint, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            hideLoading();
            
            if (result.success) {
                showAlert(result.message || 'Authentication successful!', 'success');
                // Redirect after successful authentication
                setTimeout(() => {
                    window.location.href = result.redirect || '/dashboard';
                }, 1500);
            } else {
                showAlert(result.message || 'Authentication failed. Please try again.', 'error');
            }
        } catch (error) {
            hideLoading();
            console.error('Error during facial authentication:', error);
            showAlert('An error occurred. Please try again.', 'error');
        }
    }, 'image/jpeg', 0.95);
}

// Show Loading Spinner
function showLoading() {
    document.getElementById('loadingSpinner').classList.remove('hidden');
}

// Hide Loading Spinner
function hideLoading() {
    document.getElementById('loadingSpinner').classList.add('hidden');
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

// Form validation
document.addEventListener('DOMContentLoaded', () => {
    // Login form submission
    const loginFormElement = document.querySelector('#loginForm form');
    if (loginFormElement) {
        loginFormElement.addEventListener('submit', (e) => {
            e.preventDefault();
            showLoading();
            
            const formData = new FormData(loginFormElement);
            
            fetch('/login', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(result => {
                hideLoading();
                if (result.success) {
                    showAlert('Login successful!', 'success');
                    setTimeout(() => {
                        window.location.href = result.redirect || '/dashboard';
                    }, 1000);
                } else {
                    showAlert(result.message || 'Login failed. Please check your credentials.', 'error');
                }
            })
            .catch(error => {
                hideLoading();
                console.error('Login error:', error);
                showAlert('An error occurred. Please try again.', 'error');
            });
        });
    }
    
    // Signup form submission
    const signupFormElement = document.querySelector('#signupForm form');
    if (signupFormElement) {
        signupFormElement.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const password = document.querySelector('#signupPassword').value;
            const confirmPassword = document.querySelector('#confirmPassword').value;
            
            if (password !== confirmPassword) {
                showAlert('Passwords do not match!', 'error');
                return;
            }
            
            if (password.length < 8) {
                showAlert('Password must be at least 8 characters long!', 'warning');
                return;
            }
            
            showLoading();
            
            const formData = new FormData(signupFormElement);
            
            fetch('/signup', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(result => {
                hideLoading();
                if (result.success) {
                    showAlert('Account created successfully! Please login.', 'success');
                    setTimeout(() => {
                        loginToggle.click();
                    }, 1500);
                } else {
                    showAlert(result.message || 'Signup failed. Please try again.', 'error');
                }
            })
            .catch(error => {
                hideLoading();
                console.error('Signup error:', error);
                showAlert('An error occurred. Please try again.', 'error');
            });
        });
    }
});

// Handle browser back button when modal is open
window.addEventListener('popstate', () => {
    const modal = document.getElementById('facialModal');
    if (!modal.classList.contains('hidden')) {
        closeFacialModal();
    }
});

// Clean up camera on page unload
window.addEventListener('beforeunload', () => {
    stopCamera();
});
