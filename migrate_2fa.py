"""
Database Migration Script for Two-Factor Authentication
Adds 2FA fields to the users table
"""

from flask import Flask
from database import db
import sqlite3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///face_auth.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

def migrate_database():
    """Add 2FA fields to existing users table"""
    try:
        conn = sqlite3.connect('instance/face_auth.db')
        cursor = conn.cursor()
        
        print("🔄 Starting 2FA database migration...")
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add phone_number column if it doesn't exist
        if 'phone_number' not in columns:
            print("  ➕ Adding phone_number column...")
            cursor.execute('ALTER TABLE users ADD COLUMN phone_number VARCHAR(20)')
            print("  ✅ phone_number column added")
        else:
            print("  ⚠️  phone_number column already exists")
        
        # Add two_factor_enabled column if it doesn't exist
        if 'two_factor_enabled' not in columns:
            print("  ➕ Adding two_factor_enabled column...")
            cursor.execute('ALTER TABLE users ADD COLUMN two_factor_enabled BOOLEAN DEFAULT 0')
            print("  ✅ two_factor_enabled column added")
        else:
            print("  ⚠️  two_factor_enabled column already exists")
        
        # Add otp_secret column if it doesn't exist
        if 'otp_secret' not in columns:
            print("  ➕ Adding otp_secret column...")
            cursor.execute('ALTER TABLE users ADD COLUMN otp_secret VARCHAR(10)')
            print("  ✅ otp_secret column added")
        else:
            print("  ⚠️  otp_secret column already exists")
        
        # Add otp_created_at column if it doesn't exist
        if 'otp_created_at' not in columns:
            print("  ➕ Adding otp_created_at column...")
            cursor.execute('ALTER TABLE users ADD COLUMN otp_created_at DATETIME')
            print("  ✅ otp_created_at column added")
        else:
            print("  ⚠️  otp_created_at column already exists")
        
        conn.commit()
        conn.close()
        
        print("✅ 2FA database migration completed successfully!")
        print("\n📝 New 2FA fields added:")
        print("  • phone_number - Store user's phone number")
        print("  • two_factor_enabled - Enable/disable 2FA per user")
        print("  • otp_secret - Store current OTP code")
        print("  • otp_created_at - Track OTP expiration")
        
        return True
    
    except Exception as e:
        print(f"❌ Error during migration: {str(e)}")
        return False

if __name__ == '__main__':
    print("="*60)
    print("🔐 TWO-FACTOR AUTHENTICATION DATABASE MIGRATION")
    print("="*60)
    
    migrate_database()
    
    print("\n" + "="*60)
    print("Migration complete! You can now use 2FA features.")
    print("="*60)
