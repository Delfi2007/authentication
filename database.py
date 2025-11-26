from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

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
    
    # Relationship with login attempts
    login_attempts = db.relationship('LoginAttempt', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'is_active': self.is_active,
            'face_registered': self.face_registered,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
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

def get_user_login_attempts(username, limit=10):
    """Get recent login attempts for a user"""
    user = get_user_by_username(username)
    if not user:
        return []
    
    return LoginAttempt.query.filter_by(user_id=user.id)\
                            .order_by(LoginAttempt.timestamp.desc())\
                            .limit(limit).all()