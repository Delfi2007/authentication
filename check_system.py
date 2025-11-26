import os
import requests
import json

def check_system_status():
    """Check if the face recognition system is working properly"""
    
    print("🔍 Face Recognition System Status Check")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend Server: RUNNING")
            health_data = response.json()
            print(f"   Service: {health_data.get('service', 'Unknown')}")
        else:
            print(f"❌ Backend Server: ERROR (Status: {response.status_code})")
            return
    except Exception as e:
        print(f"❌ Backend Server: NOT RUNNING")
        print(f"   Error: {str(e)}")
        print("\n💡 Solution: Run 'py app.py' in the terminal")
        return
    
    # Check frontend accessibility
    try:
        response = requests.get("http://localhost:5000/", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend Interface: ACCESSIBLE")
        else:
            print(f"❌ Frontend Interface: ERROR (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Frontend Interface: ERROR - {str(e)}")
    
    # Check database
    try:
        response = requests.get("http://localhost:5000/users", timeout=5)
        if response.status_code == 200:
            users_data = response.json()
            print(f"✅ Database: WORKING")
            print(f"   Total Users: {users_data.get('total', 0)}")
        else:
            print(f"❌ Database: ERROR (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Database: ERROR - {str(e)}")
    
    # Check face storage directory
    user_faces_dir = "user_faces"
    if os.path.exists(user_faces_dir):
        face_files = [f for f in os.listdir(user_faces_dir) if f.endswith('.pkl')]
        print(f"✅ Face Storage: READY")
        print(f"   Location: {os.path.abspath(user_faces_dir)}")
        print(f"   Registered Faces: {len(face_files)}")
        if face_files:
            for face_file in face_files:
                username = face_file.replace('.pkl', '')
                print(f"   - {username}")
    else:
        print(f"❌ Face Storage: DIRECTORY MISSING")
    
    # Check uploads directory
    uploads_dir = "uploads"
    if os.path.exists(uploads_dir):
        print(f"✅ Upload Directory: READY")
    else:
        print(f"❌ Upload Directory: MISSING")
    
    print("\n" + "=" * 50)
    print("🌐 Access the system at: http://localhost:5000")
    print("📋 To register a user:")
    print("   1. Open the web interface")
    print("   2. Enter username and upload/capture face photo")
    print("   3. Click 'Register User'")
    print("   4. Check user_faces/ folder for .pkl file")
    print("\n🔑 To test login:")
    print("   1. Use face photo of registered user")
    print("   2. Click 'Login with Face'")
    print("   3. Should show recognition result")

if __name__ == "__main__":
    check_system_status()