import requests
import json
import base64
import os
from PIL import Image
import io

class FacePlusPlusAPI:
    def __init__(self):
        # Face++ API credentials
        self.api_key = "djHyv6nM7FXcsKmRO-65CrY_zvSA_qxH"  # Your actual API key
        self.api_secret = "QN0P-iayDif9UComBL34UQx94WkOhqQ9"  # Your actual API secret
        self.base_url = "https://api-us.faceplusplus.com/facepp/v3"
        
        # Local fallback if API fails
        self.user_faces_dir = "user_faces"
        self.known_face_tokens = {}  # Store face tokens for users
        
        if not os.path.exists(self.user_faces_dir):
            os.makedirs(self.user_faces_dir)
    
    def setup_api_credentials(self, api_key, api_secret):
        """Set up API credentials"""
        self.api_key = api_key
        self.api_secret = api_secret
    
    def convert_image_to_base64(self, image_data):
        """Convert image data to base64"""
        try:
            if isinstance(image_data, str) and image_data.startswith('data:image'):
                # Already base64 data URL
                image_data = image_data.split(',')[1]
                return image_data
            elif hasattr(image_data, 'read'):
                # File object
                image_bytes = image_data.read()
                return base64.b64encode(image_bytes).decode()
            else:
                # Numpy array or PIL image
                if hasattr(image_data, 'shape'):  # Numpy array
                    from PIL import Image
                    image = Image.fromarray(image_data)
                    buffer = io.BytesIO()
                    image.save(buffer, format='JPEG')
                    image_bytes = buffer.getvalue()
                else:
                    image_bytes = image_data
                return base64.b64encode(image_bytes).decode()
        except Exception as e:
            print(f"Error converting image to base64: {str(e)}")
            return None
    
    def detect_face(self, image_data):
        """Detect face using Face++ API"""
        try:
            if self.api_key == "YOUR_API_KEY_HERE":
                return False, "Please set up Face++ API credentials first"
            
            image_base64 = self.convert_image_to_base64(image_data)
            if not image_base64:
                return False, "Failed to convert image"
            
            url = f"{self.base_url}/detect"
            data = {
                'api_key': self.api_key,
                'api_secret': self.api_secret,
                'image_base64': image_base64,
                'return_attributes': 'age,gender,emotion'
            }
            
            response = requests.post(url, data=data, timeout=10)
            result = response.json()
            
            if 'faces' in result and len(result['faces']) > 0:
                face_info = result['faces'][0]
                return True, {
                    'face_token': face_info['face_token'],
                    'face_rectangle': face_info['face_rectangle'],
                    'attributes': face_info.get('attributes', {})
                }
            else:
                return False, "No face detected in image"
                
        except Exception as e:
            print(f"Face detection error: {str(e)}")
            return False, f"Face detection failed: {str(e)}"
    
    def register_face(self, username, image_data):
        """Register a face using Face++ API"""
        try:
            # Detect face first
            success, face_data = self.detect_face(image_data)
            
            if not success:
                return False, face_data
            
            # Store face token for this user
            face_token = face_data['face_token']
            self.known_face_tokens[username] = face_token
            
            # Save to local file as backup
            face_file_path = os.path.join(self.user_faces_dir, f"{username}_facetoken.txt")
            with open(face_file_path, 'w') as f:
                json.dump({
                    'username': username,
                    'face_token': face_token,
                    'face_data': face_data
                }, f)
            
            print(f"Face registered for {username} with token: {face_token}")
            return True, f"Face registered successfully for {username}"
            
        except Exception as e:
            print(f"Registration error: {str(e)}")
            return False, f"Registration failed: {str(e)}"
    
    def load_known_faces(self):
        """Load known face tokens from files"""
        self.known_face_tokens = {}
        
        if not os.path.exists(self.user_faces_dir):
            return
        
        for filename in os.listdir(self.user_faces_dir):
            if filename.endswith('_facetoken.txt'):
                filepath = os.path.join(self.user_faces_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        username = data['username']
                        face_token = data['face_token']
                        self.known_face_tokens[username] = face_token
                        print(f"Loaded face token for {username}")
                except Exception as e:
                    print(f"Error loading face token from {filename}: {str(e)}")
    
    def compare_faces(self, face_token1, face_token2):
        """Compare two faces using Face++ API"""
        try:
            if self.api_key == "YOUR_API_KEY_HERE":
                return False, 0, "Please set up Face++ API credentials first"
            
            url = f"{self.base_url}/compare"
            data = {
                'api_key': self.api_key,
                'api_secret': self.api_secret,
                'face_token1': face_token1,
                'face_token2': face_token2
            }
            
            response = requests.post(url, data=data, timeout=10)
            result = response.json()
            
            if 'confidence' in result:
                confidence = result['confidence']
                threshold = result.get('thresholds', {}).get('1e-3', 70)  # Default threshold
                is_same_person = confidence > threshold
                return is_same_person, confidence, "Comparison successful"
            else:
                return False, 0, f"Comparison failed: {result.get('error_message', 'Unknown error')}"
                
        except Exception as e:
            print(f"Face comparison error: {str(e)}")
            return False, 0, f"Comparison failed: {str(e)}"
    
    def recognize_face(self, image_data, tolerance=70):
        """Recognize face using Face++ API"""
        try:
            # Load known faces
            self.load_known_faces()
            
            if not self.known_face_tokens:
                return None, 0.0, "No registered users found"
            
            # Detect face in input image
            success, face_data = self.detect_face(image_data)
            
            if not success:
                return None, 0.0, face_data
            
            input_face_token = face_data['face_token']
            
            # Compare with all known faces
            best_match = None
            best_confidence = 0
            
            for username, known_face_token in self.known_face_tokens.items():
                is_same, confidence, message = self.compare_faces(input_face_token, known_face_token)
                
                print(f"Comparing with {username}: confidence = {confidence}")
                
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = username
            
            # Check if best match meets threshold
            if best_confidence >= tolerance:
                return best_match, best_confidence, f"Face recognized as {best_match}"
            else:
                return None, best_confidence, f"Face not recognized. Best match: {best_confidence:.1f}% (threshold: {tolerance}%)"
                
        except Exception as e:
            print(f"Recognition error: {str(e)}")
            return None, 0.0, f"Recognition failed: {str(e)}"
    
    def get_registered_users(self):
        """Get list of registered users"""
        self.load_known_faces()
        return list(self.known_face_tokens.keys())
    
    def delete_user(self, username):
        """Delete a user's face data"""
        try:
            # Remove from memory
            if username in self.known_face_tokens:
                del self.known_face_tokens[username]
            
            # Remove file
            face_file_path = os.path.join(self.user_faces_dir, f"{username}_facetoken.txt")
            if os.path.exists(face_file_path):
                os.remove(face_file_path)
            
            return True, f"User {username} deleted successfully"
            
        except Exception as e:
            return False, f"Error deleting user: {str(e)}"

# For backward compatibility
class FaceRecognitionSystem(FacePlusPlusAPI):
    pass