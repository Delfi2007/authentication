from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from flask_cors import CORS
from flask_session import Session
import os
import base64
import json
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from google_auth_oauthlib.flow import Flow

# Import our custom modules
from face_api import FacePlusPlusAPI
from database import (init_db, create_user, get_user_by_username, update_user_face_status, 
                     log_login_attempt, update_last_login, get_all_users, get_user_login_attempts,
                     create_google_user, get_user_by_google_id)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///face_auth.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max for image data

# Session configuration
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)

# Google OAuth Configuration
app.config['GOOGLE_CLIENT_ID'] = '1001852997221-lekla2rgordhmbp46lf3c0dpvtmi5nb5.apps.googleusercontent.com'
app.config['GOOGLE_CLIENT_SECRET'] = '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'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # For development only

# Enable CORS for all routes
CORS(app)

# Initialize Face++ API system
face_system = FacePlusPlusAPI()
print("Face++ API initialized with professional recognition")

# Initialize database
init_db(app)

# HTML template for testing
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Face Recognition Authentication</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .container { background: #f5f5f5; padding: 20px; border-radius: 10px; margin: 10px 0; }
        .button { background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
        .button:hover { background: #45a049; }
        .button.danger { background: #f44336; }
        .button.danger:hover { background: #da190b; }
        .result { margin: 10px 0; padding: 10px; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
        video { width: 100%; max-width: 400px; border: 2px solid #ddd; border-radius: 10px; }
        .users-list { background: white; padding: 15px; border-radius: 5px; margin: 10px 0; }
    </style>
</head>
<body>
    <h1>🔐 Face Recognition Authentication System</h1>
    
    <div class="container" style="background: #d4edda; border: 2px solid #c3e6cb;">
        <h3>🚀 Quick Start Guide - Improved System!</h3>
        <p><strong>✅ Now using enhanced face recognition!</strong></p>
        <p><strong>First time user?</strong> Follow these steps:</p>
        <ol>
            <li><strong>Start Camera</strong> and <strong>Capture Photo</strong> below</li>
            <li><strong>Register a User</strong> with your captured photo</li>
            <li><strong>Test Login</strong> using Face Recognition</li>
        </ol>
        <p><em>⚠️ You must register a user before you can login!</em></p>
        <p><strong>📸 Tips for best results:</strong></p>
        <ul>
            <li>Ensure good lighting on your face</li>
            <li>Look directly at the camera</li>
            <li>Keep your face clearly visible</li>
            <li>Avoid shadows or reflections</li>
        </ul>
    </div>
    
    <div class="container">
        <h2>📹 Camera Access</h2>
        <p><strong>Instructions:</strong></p>
        <ol>
            <li>Click "Start Camera" to enable your webcam</li>
            <li>Position your face in the camera view</li>
            <li>Click "Capture Photo" to take your picture</li>
            <li>Use the captured photo for registration or login</li>
        </ol>
        <video id="video" autoplay></video><br>
        <canvas id="canvas" style="display: none;"></canvas>
        <button class="button" onclick="startCamera()">Start Camera</button>
        <button class="button" onclick="capturePhoto()">Capture Photo</button>
        <div id="cameraResult"></div>
    </div>

    <div class="container" style="background: #e3f2fd; border: 2px solid #81c784;">
        <h2>🌐 Google Login</h2>
        <p><strong>Quick & Secure Authentication</strong></p>
        <p>Login with your Google account instantly - No registration required!</p>
        <button class="button" onclick="loginWithGoogle()" style="background: #db4437; color: white; font-size: 16px; padding: 12px 24px;">
            🔑 Login with Google
        </button>
        <div id="googleLoginResult"></div>
        <p style="font-size: 12px; color: #666; margin-top: 10px;">
            💡 After Google login, you can optionally register your face for even faster future logins!
        </p>
    </div>

    <div class="container">
        <h2>👤 Manual User Registration</h2>
        <p><strong>Register with face recognition only (no Google account needed)</strong></p>
        <input type="text" id="registerUsername" placeholder="Username" style="padding: 10px; margin: 5px; width: 200px;">
        <input type="email" id="registerEmail" placeholder="Email (optional)" style="padding: 10px; margin: 5px; width: 200px;">
        <input type="text" id="registerName" placeholder="Full Name (optional)" style="padding: 10px; margin: 5px; width: 200px;"><br>
        <input type="file" id="registerImage" accept="image/*" style="margin: 10px 0;">
        <button class="button" onclick="registerUser()">Register User</button>
        <div id="registerResult"></div>
    </div>

    <div class="container">
        <h2>🔑 Face Recognition Login</h2>
        <p><strong>Click the button below to start login with face recognition.</strong></p>
        <p>The camera will open automatically and capture your photo for authentication.</p>
        <button class="button" onclick="loginWithFace()">Login with Face</button>
        <div id="loginResult"></div>
    </div>

    <div class="container">
        <h2>📊 System Status</h2>
        <button class="button" onclick="getUsers()">Get Registered Users</button>
        <button class="button" onclick="getSystemStats()">Get System Statistics</button>
        <div id="statusResult"></div>
    </div>

    <script>
        let video = document.getElementById('video');
        let canvas = document.getElementById('canvas');
        let ctx = canvas.getContext('2d');
        let currentStream = null;

        async function startCamera() {
            try {
                currentStream = await navigator.mediaDevices.getUserMedia({ 
                    video: { width: 640, height: 480 } 
                });
                video.srcObject = currentStream;
                document.getElementById('cameraResult').innerHTML = 
                    '<div class="result success">Camera started successfully!</div>';
            } catch (error) {
                document.getElementById('cameraResult').innerHTML = 
                    '<div class="result error">Error accessing camera: ' + error.message + '</div>';
            }
        }

        function capturePhoto() {
            if (!currentStream) {
                document.getElementById('cameraResult').innerHTML = 
                    '<div class="result error">Please start camera first!</div>';
                return;
            }
            
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            ctx.drawImage(video, 0, 0);
            
            // Convert canvas to blob with compression
            canvas.toBlob(function(blob) {
                if (blob) {
                    // Convert blob to base64
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        window.capturedImageData = e.target.result;
                        document.getElementById('cameraResult').innerHTML = 
                            '<div class="result success">📸 Photo captured successfully!<br>' +
                            '✅ You can now use this photo for:<br>' +
                            '• User registration<br>' +
                            '• Face recognition login<br>' +
                            '<strong>Ready to proceed!</strong></div>';
                    };
                    reader.readAsDataURL(blob);
                } else {
                    document.getElementById('cameraResult').innerHTML = 
                        '<div class="result error">❌ Failed to capture photo! Please try again.</div>';
                }
            }, 'image/jpeg', 0.7); // JPEG with 70% quality for smaller file size
        }

        async function registerUser() {
            const username = document.getElementById('registerUsername').value;
            const email = document.getElementById('registerEmail').value;
            const fullName = document.getElementById('registerName').value;
            const fileInput = document.getElementById('registerImage');
            
            if (!username) {
                document.getElementById('registerResult').innerHTML = 
                    '<div class="result error">Please enter a username!</div>';
                return;
            }

            let imageData;
            if (fileInput.files && fileInput.files[0]) {
                // Check file size (max 10MB)
                if (fileInput.files[0].size > 10 * 1024 * 1024) {
                    document.getElementById('registerResult').innerHTML = 
                        '<div class="result error">Image file too large! Please use an image smaller than 10MB.</div>';
                    return;
                }
                imageData = await fileToBase64(fileInput.files[0]);
            } else if (window.capturedImageData) {
                imageData = window.capturedImageData;
            } else {
                document.getElementById('registerResult').innerHTML = 
                    '<div class="result error">Please provide an image (upload file or capture photo)!</div>';
                return;
            }

            const formData = new FormData();
            formData.append('username', username);
            formData.append('email', email);
            formData.append('full_name', fullName);
            formData.append('image', imageData);

            try {
                const response = await fetch('/register', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.json();
                
                if (result.success) {
                    document.getElementById('registerResult').innerHTML = 
                        '<div class="result success">' + result.message + '</div>';
                } else {
                    document.getElementById('registerResult').innerHTML = 
                        '<div class="result error">' + result.message + '</div>';
                }
            } catch (error) {
                document.getElementById('registerResult').innerHTML = 
                    '<div class="result error">Error: ' + error.message + '</div>';
            }
        }

        async function loginWithFace() {
            // Clear any previous login results
            document.getElementById('loginResult').innerHTML = 
                '<div class="result" style="background: #fff3cd; color: #856404;">Starting camera for login...</div>';

            try {
                // Start camera for login
                if (currentStream) {
                    // Stop existing stream first
                    currentStream.getTracks().forEach(track => track.stop());
                }
                
                currentStream = await navigator.mediaDevices.getUserMedia({ 
                    video: { width: 640, height: 480 } 
                });
                video.srcObject = currentStream;
                
                document.getElementById('loginResult').innerHTML = 
                    '<div class="result" style="background: #d1ecf1; color: #0c5460;">' +
                    '📹 Camera opened for login!<br>' +
                    'Please position your face in the camera and wait...<br>' +
                    '<strong>Capturing photo automatically in 3 seconds...</strong></div>';

                // Auto-capture after 3 seconds
                setTimeout(async () => {
                    // Capture photo automatically
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                    ctx.drawImage(video, 0, 0);
                    
                    // Convert canvas to blob with compression
                    canvas.toBlob(async function(blob) {
                        if (blob) {
                            // Convert blob to base64
                            const reader = new FileReader();
                            reader.onload = async function(e) {
                                const loginImageData = e.target.result;
                                
                                // Stop camera after capture
                                if (currentStream) {
                                    currentStream.getTracks().forEach(track => track.stop());
                                    currentStream = null;
                                }
                                
                                // Show processing message
                                document.getElementById('loginResult').innerHTML = 
                                    '<div class="result" style="background: #fff3cd; color: #856404;">📸 Photo captured! Processing your face for login...</div>';

                                // Send to server
                                const formData = new FormData();
                                formData.append('image', loginImageData);

                                try {
                                    const response = await fetch('/login', {
                                        method: 'POST',
                                        body: formData
                                    });
                                    const result = await response.json();
                                    
                                    if (result.success) {
                                        document.getElementById('loginResult').innerHTML = 
                                            '<div class="result success">🎉 Login Successful!<br>Welcome back, ' + result.username + '!<br>Confidence: ' + 
                                            result.confidence.toFixed(2) + '%<br><strong>✅ Authentication completed successfully!</strong></div>';
                                    } else {
                                        document.getElementById('loginResult').innerHTML = 
                                            '<div class="result error">❌ Login Failed: ' + result.message + '</div>';
                                    }
                                } catch (error) {
                                    document.getElementById('loginResult').innerHTML = 
                                        '<div class="result error">❌ Error during login: ' + error.message + '</div>';
                                }
                            };
                            reader.readAsDataURL(blob);
                        } else {
                            document.getElementById('loginResult').innerHTML = 
                                '<div class="result error">❌ Failed to capture photo for login! Please try again.</div>';
                        }
                    }, 'image/jpeg', 0.7);
                }, 3000);

            } catch (error) {
                document.getElementById('loginResult').innerHTML = 
                    '<div class="result error">❌ Error accessing camera for login: ' + error.message + '</div>';
            }
        }

        async function getUsers() {
            try {
                const response = await fetch('/users');
                const result = await response.json();
                
                if (result.success) {
                    let html = '<div class="users-list"><h3>Registered Users:</h3>';
                    result.users.forEach(user => {
                        html += '<p><strong>' + user.username + '</strong> - ' + user.full_name + 
                                ' (Face: ' + (user.face_registered ? '✅' : '❌') + ')</p>';
                    });
                    html += '</div>';
                    document.getElementById('statusResult').innerHTML = html;
                } else {
                    document.getElementById('statusResult').innerHTML = 
                        '<div class="result error">' + result.message + '</div>';
                }
            } catch (error) {
                document.getElementById('statusResult').innerHTML = 
                    '<div class="result error">Error: ' + error.message + '</div>';
            }
        }

        async function getSystemStats() {
            try {
                const response = await fetch('/stats');
                const result = await response.json();
                
                if (result.success) {
                    document.getElementById('statusResult').innerHTML = 
                        '<div class="result success">Total Users: ' + result.total_users + 
                        ', Users with Face: ' + result.users_with_face + '</div>';
                } else {
                    document.getElementById('statusResult').innerHTML = 
                        '<div class="result error">' + result.message + '</div>';
                }
            } catch (error) {
                document.getElementById('statusResult').innerHTML = 
                    '<div class="result error">Error: ' + error.message + '</div>';
            }
        }

        function fileToBase64(file) {
            return new Promise((resolve, reject) => {
                const reader = new FileReader();
                reader.readAsDataURL(file);
                reader.onload = () => resolve(reader.result);
                reader.onerror = error => reject(error);
            });
        }

        async function loginWithGoogle() {
            try {
                // Redirect to Google OAuth
                window.location.href = '/auth/google';
            } catch (error) {
                document.getElementById('googleLoginResult').innerHTML = 
                    '<div class="result error">Google login error: ' + error.message + '</div>';
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main page with testing interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/register', methods=['POST'])
def register_user():
    """Register a new user with face encoding"""
    try:
        # Get form data
        username = request.form.get('username')
        email = request.form.get('email', '')
        full_name = request.form.get('full_name', '')
        image_data = request.form.get('image')
        
        if not username:
            return jsonify({'success': False, 'message': 'Username is required'})
        
        if not image_data:
            return jsonify({'success': False, 'message': 'Image is required'})
        
        # Create user in database
        user, message = create_user(username, email if email else None, full_name if full_name else None)
        if not user:
            return jsonify({'success': False, 'message': message})
        
        # Register face
        success, result_message = face_system.register_face(username, image_data)
        
        if success:
            # Update user's face registration status
            update_user_face_status(username, True)
            
            # Log registration attempt
            log_login_attempt(
                user_id=user.id,
                attempted_username=username,
                success=True,
                method='face_registration',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            return jsonify({
                'success': True, 
                'message': f'User {username} registered successfully with face recognition!',
                'user': user.to_dict()
            })
        else:
            # Registration failed, but user was created
            log_login_attempt(
                user_id=user.id,
                attempted_username=username,
                success=False,
                method='face_registration',
                error_message=result_message,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            return jsonify({'success': False, 'message': result_message})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})

@app.route('/login', methods=['POST'])
def login_user():
    """Login user using face recognition"""
    try:
        image_data = request.form.get('image')
        
        if not image_data:
            return jsonify({'success': False, 'message': 'Image is required'})
        
        # Recognize face
        username, confidence, message = face_system.recognize_face(image_data)
        
        if username:
            # Get user from database
            user = get_user_by_username(username)
            if user and user.is_active:
                # Update last login
                update_last_login(username)
                
                # Log successful login
                log_login_attempt(
                    user_id=user.id,
                    attempted_username=username,
                    success=True,
                    confidence=confidence,
                    method='face_recognition',
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent')
                )
                
                return jsonify({
                    'success': True,
                    'message': f'Welcome back, {username}!',
                    'username': username,
                    'confidence': confidence,
                    'user': user.to_dict()
                })
            else:
                # User not found or inactive
                log_login_attempt(
                    attempted_username=username,
                    success=False,
                    confidence=confidence,
                    method='face_recognition',
                    error_message='User not found or inactive',
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent')
                )
                
                return jsonify({'success': False, 'message': 'User not found or account is inactive'})
        else:
            # Check if we have any registered users at all
            all_users = get_all_users()
            users_with_faces = [user for user in all_users if user.face_registered]
            
            if not users_with_faces:
                error_msg = "No registered users found. Please register a user first before attempting to login."
            else:
                error_msg = f"Face not recognized. Current registered users: {len(users_with_faces)}. Please ensure good lighting and clear face visibility, or register this face first."
            
            # Face not recognized
            log_login_attempt(
                success=False,
                confidence=0.0,
                method='face_recognition',
                error_message=error_msg,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            return jsonify({'success': False, 'message': error_msg})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})

@app.route('/users', methods=['GET'])
def get_users():
    """Get list of all registered users"""
    try:
        users = get_all_users()
        users_data = [user.to_dict() for user in users]
        
        return jsonify({
            'success': True,
            'users': users_data,
            'total': len(users_data)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})

@app.route('/user/<username>', methods=['GET'])
def get_user(username):
    """Get specific user details"""
    try:
        user = get_user_by_username(username)
        if not user:
            return jsonify({'success': False, 'message': 'User not found'})
        
        # Get recent login attempts
        login_attempts = get_user_login_attempts(username, limit=5)
        attempts_data = [attempt.to_dict() for attempt in login_attempts]
        
        return jsonify({
            'success': True,
            'user': user.to_dict(),
            'recent_attempts': attempts_data
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    try:
        all_users = get_all_users()
        total_users = len(all_users)
        users_with_face = len([user for user in all_users if user.face_registered])
        registered_faces = len(face_system.get_registered_users())
        
        return jsonify({
            'success': True,
            'total_users': total_users,
            'users_with_face': users_with_face,
            'registered_faces': registered_faces,
            'active_users': len([user for user in all_users if user.is_active])
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})

@app.route('/reload-faces', methods=['POST'])
def reload_faces():
    """Reload face encodings from disk"""
    try:
        success, message = face_system.reload_faces()
        return jsonify({'success': success, 'message': message})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'})

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Face Recognition Authentication API',
        'version': '1.0.0'
    })

# Google OAuth Routes
@app.route('/auth/google')
def google_login():
    """Initiate Google OAuth flow"""
    try:
        # Create client configuration
        client_config = {
            "web": {
                "client_id": app.config['GOOGLE_CLIENT_ID'],
                "client_secret": app.config['GOOGLE_CLIENT_SECRET'],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [url_for('google_callback', _external=True)]
            }
        }
        
        flow = Flow.from_client_config(
            client_config,
            scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email', 
                   'https://www.googleapis.com/auth/userinfo.profile']
        )
        
        flow.redirect_uri = url_for('google_callback', _external=True)
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        
        session['state'] = state
        return redirect(authorization_url)
    
    except Exception as e:
        return f"Error initiating Google login: {str(e)}<br><a href='/'>Go back</a>"

@app.route('/auth/google/callback')
def google_callback():
    """Handle Google OAuth callback"""
    try:
        # Verify state
        if 'state' not in session or request.args.get('state') != session['state']:
            return "Invalid state parameter<br><a href='/'>Go back</a>", 400
        
        # Create flow
        client_config = {
            "web": {
                "client_id": app.config['GOOGLE_CLIENT_ID'],
                "client_secret": app.config['GOOGLE_CLIENT_SECRET'],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [url_for('google_callback', _external=True)]
            }
        }
        
        flow = Flow.from_client_config(
            client_config,
            scopes=['openid', 'https://www.googleapis.com/auth/userinfo.email',
                   'https://www.googleapis.com/auth/userinfo.profile'],
            state=session['state']
        )
        
        flow.redirect_uri = url_for('google_callback', _external=True)
        flow.fetch_token(authorization_response=request.url)
        
        # Get user info
        credentials = flow.credentials
        request_session = google_requests.Request()
        
        id_info = id_token.verify_oauth2_token(
            credentials.id_token,
            request_session,
            app.config['GOOGLE_CLIENT_ID']
        )
        
        # Extract user information
        google_id = id_info.get('sub')
        email = id_info.get('email')
        full_name = id_info.get('name')
        avatar_url = id_info.get('picture')
        
        # Create or get Google user
        user, message = create_google_user(google_id, email, full_name, avatar_url)
        
        if user:
            # Store user info in session
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_name'] = user.full_name
            session['avatar_url'] = user.avatar_url
            session['auth_method'] = user.auth_method
            
            # Update last login
            update_last_login(user.username)
            
            # Log successful login
            log_login_attempt(
                user_id=user.id,
                attempted_username=user.username,
                success=True,
                method='google_oauth',
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            
            # Redirect to success page
            return redirect(url_for('google_success'))
        else:
            return f"Error creating user: {message}<br><a href='/'>Go back</a>"
    
    except Exception as e:
        return f"Error during Google authentication: {str(e)}<br><a href='/'>Go back</a>"

@app.route('/auth/google/success')
def google_success():
    """Google login success page"""
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    user_name = session.get('user_name', 'User')
    user_email = session.get('user_email', '')
    avatar_url = session.get('avatar_url', '')
    auth_method = session.get('auth_method', 'google')
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Google Login Successful</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; text-align: center; }
            .success-box { background: #d4edda; border: 2px solid #c3e6cb; padding: 30px; border-radius: 15px; }
            .avatar { width: 100px; height: 100px; border-radius: 50%; margin: 20px 0; }
            .button { background: #4CAF50; color: white; padding: 12px 24px; border: none; border-radius: 5px; 
                     cursor: pointer; margin: 10px; text-decoration: none; display: inline-block; }
            .button:hover { background: #45a049; }
            .info { background: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="success-box">
            <h1>✅ Google Login Successful!</h1>
            {% if avatar_url %}
            <img src="{{ avatar_url }}" alt="Avatar" class="avatar">
            {% endif %}
            <h2>Welcome, {{ user_name }}!</h2>
            <p><strong>Email:</strong> {{ user_email }}</p>
            <p><strong>Authentication:</strong> {{ auth_method }}</p>
            
            <div class="info">
                <h3>🎯 What's Next?</h3>
                <p>You're now logged in! You can:</p>
                <ul style="text-align: left; display: inline-block;">
                    <li>Register your face for faster future logins</li>
                    <li>Access the full authentication system</li>
                    <li>Combine Google + Face recognition for maximum security</li>
                </ul>
            </div>
            
            <a href="/" class="button">🏠 Go to Dashboard</a>
            <a href="/auth/logout" class="button" style="background: #f44336;">🚪 Logout</a>
        </div>
    </body>
    </html>
    """, user_name=user_name, user_email=user_email, avatar_url=avatar_url, auth_method=auth_method)

@app.route('/auth/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Ensure user_faces directory exists
    os.makedirs('user_faces', exist_ok=True)
    
    print("🚀 Starting Face Recognition Authentication Server...")
    print("📝 Available endpoints:")
    print("  GET  /          - Web interface for testing")
    print("  POST /register  - Register new user with face")
    print("  POST /login     - Login with face recognition")
    print("  GET  /users     - Get all users")
    print("  GET  /user/<username> - Get user details")
    print("  GET  /stats     - Get system statistics")
    print("  POST /reload-faces - Reload face encodings")
    print("  GET  /health    - Health check")
    print("\n🌐 Open http://localhost:5000 in your browser to test the system!")
    
    app.run(debug=True, host='0.0.0.0', port=5000)