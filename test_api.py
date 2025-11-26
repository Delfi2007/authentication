# Simple Test Script for Face Recognition Backend
# This script tests the basic functionality without requiring face recognition library

import requests
import json
import base64
from PIL import Image
import io
import sys
import os

# Test configuration
BASE_URL = "http://localhost:5000"

def create_test_image():
    """Create a simple test image"""
    # Create a simple colored image for testing
    img = Image.new('RGB', (200, 200), color='lightblue')
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    # Convert to base64
    img_b64 = base64.b64encode(img_bytes.getvalue()).decode()
    return f"data:image/png;base64,{img_b64}"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check: PASSED")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Health check: ERROR - {str(e)}")
        return False

def test_stats():
    """Test stats endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/stats")
        if response.status_code == 200:
            print("✅ Stats endpoint: PASSED")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Stats endpoint: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Stats endpoint: ERROR - {str(e)}")
        return False

def test_users():
    """Test users endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/users")
        if response.status_code == 200:
            print("✅ Users endpoint: PASSED")
            result = response.json()
            print(f"   Found {result.get('total', 0)} users")
            return True
        else:
            print(f"❌ Users endpoint: FAILED (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Users endpoint: ERROR - {str(e)}")
        return False

def test_user_registration():
    """Test user registration (will fail without face recognition, but tests API)"""
    try:
        test_image = create_test_image()
        
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'full_name': 'Test User',
            'image': test_image
        }
        
        response = requests.post(f"{BASE_URL}/register", data=data)
        result = response.json()
        
        if response.status_code == 200:
            print("✅ User registration: PASSED")
            print(f"   Response: {result}")
            return True
        else:
            print("⚠️  User registration: Expected to fail without face_recognition library")
            print(f"   Error: {result.get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ User registration: ERROR - {str(e)}")
        return False

def run_tests():
    """Run all tests"""
    print("🧪 Testing Face Recognition Authentication API")
    print("=" * 50)
    
    tests = [
        test_health,
        test_stats,
        test_users,
        test_user_registration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    elif passed > 0:
        print("⚠️  Some tests passed, face recognition features need proper setup")
    else:
        print("❌ All tests failed. Check if the server is running.")
    
    return passed, total

if __name__ == "__main__":
    print("Starting API tests...")
    print(f"Testing against: {BASE_URL}")
    print()
    
    # Check if server is likely running
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
        print("✅ Server appears to be running")
        print()
    except:
        print("❌ Server doesn't appear to be running")
        print("   Please start the server with: python app.py")
        print()
        sys.exit(1)
    
    passed, total = run_tests()
    
    if passed > 0:
        print("\n🌐 You can also test the web interface at:")
        print(f"   {BASE_URL}")