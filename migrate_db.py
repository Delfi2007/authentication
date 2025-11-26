"""
Database migration script to add Google OAuth support
Run this file to update your database with new columns
"""

import sqlite3

def migrate_database():
    """Add Google OAuth columns to users table"""
    try:
        # Connect to database
        conn = sqlite3.connect('instance/face_auth.db')
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add google_id column if it doesn't exist
        if 'google_id' not in columns:
            print("Adding google_id column...")
            cursor.execute("ALTER TABLE users ADD COLUMN google_id TEXT")
            print("✓ google_id column added")
        else:
            print("✓ google_id column already exists")
        
        # Add auth_method column if it doesn't exist
        if 'auth_method' not in columns:
            print("Adding auth_method column...")
            cursor.execute("ALTER TABLE users ADD COLUMN auth_method TEXT DEFAULT 'manual'")
            print("✓ auth_method column added")
        else:
            print("✓ auth_method column already exists")
        
        # Add avatar_url column if it doesn't exist
        if 'avatar_url' not in columns:
            print("Adding avatar_url column...")
            cursor.execute("ALTER TABLE users ADD COLUMN avatar_url TEXT")
            print("✓ avatar_url column added")
        else:
            print("✓ avatar_url column already exists")
        
        # Commit changes
        conn.commit()
        print("\n✅ Database migration completed successfully!")
        print("You can now use Google OAuth authentication.\n")
        
    except Exception as e:
        print(f"❌ Error during migration: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    print("🔄 Starting database migration for Google OAuth support...\n")
    migrate_database()
