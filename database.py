from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json
import random
import string
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    full_name = db.Column(db.String(200), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    face_registered = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Google OAuth fields
    google_id = db.Column(db.String(100), unique=True, nullable=True)
    auth_method = db.Column(db.String(20), default='manual')  # 'manual', 'google', 'google+face', 'email', 'email+face'
    avatar_url = db.Column(db.String(500), nullable=True)
    
    # Password authentication
    password_hash = db.Column(db.String(255), nullable=True)
    
    # Two-Factor Authentication
    phone_number = db.Column(db.String(20), nullable=True)
    two_factor_enabled = db.Column(db.Boolean, default=False)
    otp_secret = db.Column(db.String(10), nullable=True)
    otp_created_at = db.Column(db.DateTime, nullable=True)
    
    # Relationship with login attempts
    login_attempts = db.relationship('LoginAttempt', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def generate_otp(self):
        """Generate a 6-digit OTP and store it"""
        self.otp_secret = ''.join(random.choices(string.digits, k=6))
        self.otp_created_at = datetime.utcnow()
        return self.otp_secret
    
    def verify_otp(self, otp):
        """Verify OTP - must be used within 10 minutes"""
        if not self.otp_secret or not self.otp_created_at:
            return False
        
        # Check if OTP has expired (10 minutes)
        if datetime.utcnow() - self.otp_created_at > timedelta(minutes=10):
            return False
        
        # Check if OTP matches
        return self.otp_secret == otp
    
    def clear_otp(self):
        """Clear OTP after successful verification"""
        self.otp_secret = None
        self.otp_created_at = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'face_registered': self.face_registered,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'google_id': self.google_id,
            'auth_method': self.auth_method,
            'avatar_url': self.avatar_url,
            'phone_number': self.phone_number,
            'two_factor_enabled': self.two_factor_enabled
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

class LoginAttempt(db.Model):
    __tablename__ = 'login_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    attempted_username = db.Column(db.String(80), nullable=True)
    success = db.Column(db.Boolean, nullable=False)
    confidence = db.Column(db.Float, nullable=True)
    method = db.Column(db.String(20), nullable=False)  # 'face_recognition' or 'password'
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'attempted_username': self.attempted_username,
            'success': self.success,
            'confidence': self.confidence,
            'method': self.method,
            'ip_address': self.ip_address,
            'error_message': self.error_message,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    def __repr__(self):
        return f'<LoginAttempt {self.attempted_username} - {self.success}>'

def init_db(app):
    """Initialize the database with the Flask app"""
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")
        
        # Create a default admin user if no users exist
        if User.query.count() == 0:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                full_name='System Administrator',
                is_active=True,
                face_registered=False
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user created!")

def get_user_by_username(username):
    """Get user by username"""
    return User.query.filter_by(username=username).first()

def create_user(username, email=None, full_name=None):
    """Create a new user"""
    try:
        # Check if user already exists
        existing_user = get_user_by_username(username)
        if existing_user:
            return None, "User already exists"
        
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            is_active=True,
            face_registered=False
        )
        
        db.session.add(user)
        db.session.commit()
        
        return user, "User created successfully"
    
    except Exception as e:
        db.session.rollback()
        return None, f"Error creating user: {str(e)}"

def update_user_face_status(username, face_registered=True):
    """Update user's face registration status"""
    try:
        user = get_user_by_username(username)
        if not user:
            return False, "User not found"
        
        user.face_registered = face_registered
        db.session.commit()
        
        return True, "Face registration status updated"
    
    except Exception as e:
        db.session.rollback()
        return False, f"Error updating user: {str(e)}"

def log_login_attempt(user_id=None, attempted_username=None, success=False, 
                     confidence=None, method='face_recognition', ip_address=None, 
                     user_agent=None, error_message=None):
    """Log a login attempt"""
    try:
        login_attempt = LoginAttempt(
            user_id=user_id,
            attempted_username=attempted_username,
            success=success,
            confidence=confidence,
            method=method,
            ip_address=ip_address,
            user_agent=user_agent,
            error_message=error_message
        )
        
        db.session.add(login_attempt)
        db.session.commit()
        
        return True, "Login attempt logged"
    
    except Exception as e:
        db.session.rollback()
        return False, f"Error logging login attempt: {str(e)}"

def update_last_login(username):
    """Update user's last login timestamp"""
    try:
        user = get_user_by_username(username)
        if user:
            user.last_login = datetime.utcnow()
            db.session.commit()
            return True, "Last login updated"
        return False, "User not found"
    
    except Exception as e:
        db.session.rollback()
        return False, f"Error updating last login: {str(e)}"

def get_all_users():
    """Get all users"""
    return User.query.all()

def create_google_user(google_id, email, full_name, avatar_url=None):
    """Create or get a Google-authenticated user"""
    try:
        # Check if Google user already exists
        existing_user = User.query.filter_by(google_id=google_id).first()
        if existing_user:
            return existing_user, "Google user already exists"
        
        # Check if email is already used
        existing_email_user = User.query.filter_by(email=email).first()
        if existing_email_user:
            # Link Google account to existing user
            existing_email_user.google_id = google_id
            existing_email_user.auth_method = 'google+face' if existing_email_user.face_registered else 'google'
            existing_email_user.avatar_url = avatar_url
            db.session.commit()
            return existing_email_user, "Google account linked to existing user"
        
        # Create new Google user
        username = email.split('@')[0]  # Use email prefix as username
        
        # Make username unique if it already exists
        counter = 1
        original_username = username
        while User.query.filter_by(username=username).first():
            username = f"{original_username}_{counter}"
            counter += 1
        
        new_user = User(
            username=username,
            email=email,
            full_name=full_name,
            google_id=google_id,
            auth_method='google',
            avatar_url=avatar_url,
            is_active=True
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return new_user, "Google user created successfully"
    
    except Exception as e:
        db.session.rollback()
        return None, f"Error creating Google user: {str(e)}"

def get_user_by_google_id(google_id):
    """Get user by Google ID"""
    return User.query.filter_by(google_id=google_id).first()

def create_email_password_user(username, email, password, full_name=None):
    """Create a new user with email and password"""
    try:
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return None, "Username already exists"
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            return None, "Email already registered"
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            full_name=full_name,
            auth_method='email',
            is_active=True
        )
        
        # Set password
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        return new_user, "User registered successfully"
    
    except Exception as e:
        db.session.rollback()
        return None, f"Error creating user: {str(e)}"

def authenticate_user(email, password):
    """Authenticate user with email and password"""
    try:
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return None, "Invalid email or password"
        
        # Check if user is active
        if not user.is_active:
            return None, "Account is disabled"
        
        # Verify password
        if not user.check_password(password):
            return None, "Invalid email or password"
        
        return user, "Login successful"
    
    except Exception as e:
        return None, f"Error during authentication: {str(e)}"

def get_user_by_email(email):
    """Get user by email"""
    return User.query.filter_by(email=email).first()

def enable_two_factor(username, phone_number):
    """Enable two-factor authentication for a user"""
    try:
        user = get_user_by_username(username)
        if not user:
            return False, "User not found"
        
        user.phone_number = phone_number
        user.two_factor_enabled = True
        db.session.commit()
        
        return True, "Two-factor authentication enabled"
    
    except Exception as e:
        db.session.rollback()
        return False, f"Error enabling 2FA: {str(e)}"

def disable_two_factor(username):
    """Disable two-factor authentication for a user"""
    try:
        user = get_user_by_username(username)
        if not user:
            return False, "User not found"
        
        user.two_factor_enabled = False
        user.clear_otp()
        db.session.commit()
        
        return True, "Two-factor authentication disabled"
    
    except Exception as e:
        db.session.rollback()
        return False, f"Error disabling 2FA: {str(e)}"

def send_otp(user):
    """Generate OTP for user and prepare for sending"""
    try:
        otp = user.generate_otp()
        db.session.commit()
        return True, otp
    
    except Exception as e:
        db.session.rollback()
        return False, None

def verify_user_otp(username, otp):
    """Verify OTP for a user"""
    try:
        user = get_user_by_username(username)
        if not user:
            return False, "User not found"
        
        if user.verify_otp(otp):
            user.clear_otp()
            db.session.commit()
            return True, "OTP verified successfully"
        else:
            return False, "Invalid or expired OTP"
    
    except Exception as e:
        return False, f"Error verifying OTP: {str(e)}"

def get_all_users():
    """Get all users"""
    return User.query.all()

def get_user_login_attempts(username, limit=10):
    """Get recent login attempts for a user"""
    user = get_user_by_username(username)
    if not user:
        return []
    
    return LoginAttempt.query.filter_by(user_id=user.id)\
                            .order_by(LoginAttempt.timestamp.desc())\
                            .limit(limit).all()