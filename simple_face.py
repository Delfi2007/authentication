import cv2
import numpy as np
import os
import pickle
from PIL import Image
import io
import hashlib

class SimpleFaceSystem:
    """Simple face recognition system using basic image comparison"""
    
    def __init__(self, user_faces_dir="user_faces"):
        self.user_faces_dir = user_faces_dir
        self.known_face_hashes = {}
        self.known_face_names = []
        
        # Initialize OpenCV face cascade
        try:
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            print("OpenCV face detection initialized")
        except Exception as e:
            print(f"Error initializing face detection: {str(e)}")
            self.face_cascade = None
        
        self.load_known_faces()
    
    def load_known_faces(self):
        """Load all known face hashes from the user_faces directory"""
        self.known_face_hashes = {}
        self.known_face_names = []
        
        if not os.path.exists(self.user_faces_dir):
            os.makedirs(self.user_faces_dir)
            return
        
        for filename in os.listdir(self.user_faces_dir):
            if filename.endswith('_simple.pkl'):
                username = filename.replace('_simple.pkl', '')
                filepath = os.path.join(self.user_faces_dir, filename)
                try:
                    with open(filepath, 'rb') as f:
                        face_data = pickle.load(f)
                        self.known_face_hashes[username] = face_data
                        self.known_face_names.append(username)
                        print(f"Loaded face data for user: {username}")
                except Exception as e:
                    print(f"Error loading face data for {username}: {str(e)}")
    
    def process_image(self, image_data):
        """Convert image data to numpy array"""
        try:
            if isinstance(image_data, str) and image_data.startswith('data:image'):
                # Remove data URL prefix
                image_data = image_data.split(',')[1]
                import base64
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
            elif hasattr(image_data, 'read'):
                image_bytes = image_data.read()
                image = Image.open(io.BytesIO(image_bytes))
            else:
                return image_data
            
            # Convert to RGB and resize
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize to standard size
            image = image.resize((200, 200), Image.Resampling.LANCZOS)
            image_array = np.array(image)
            
            return image_array
            
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return None
    
    def detect_face(self, image_array):
        """Detect face in image"""
        if self.face_cascade is None:
            return None
        
        try:
            # Convert to grayscale
            if len(image_array.shape) == 3:
                gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = image_array
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, 1.3, 5, minSize=(30, 30))
            
            if len(faces) == 0:
                return None
            
            # Get the largest face
            largest_face = max(faces, key=lambda face: face[2] * face[3])
            x, y, w, h = largest_face
            
            # Extract face region
            face_region = gray[y:y+h, x:x+w]
            face_region = cv2.resize(face_region, (100, 100))
            
            return face_region
            
        except Exception as e:
            print(f"Face detection error: {str(e)}")
            return None
    
    def create_face_signature(self, image_array):
        """Create a simple face signature"""
        try:
            face_region = self.detect_face(image_array)
            
            if face_region is None:
                return None, "No face detected"
            
            # Create multiple features
            features = {
                'histogram': cv2.calcHist([face_region], [0], None, [64], [0, 256]).flatten(),
                'avg_intensity': np.mean(face_region),
                'std_intensity': np.std(face_region),
                'face_hash': hashlib.md5(face_region.tobytes()).hexdigest(),
                'shape': face_region.shape,
                'corners': face_region[0:10, 0:10].flatten(),  # Top-left corner
                'center': face_region[40:60, 40:60].flatten()   # Center region
            }
            
            return features, "Face signature created"
            
        except Exception as e:
            return None, f"Error creating face signature: {str(e)}"
    
    def compare_faces(self, features1, features2):
        """Compare two face feature sets"""
        try:
            score = 0
            total_weight = 0
            
            # Histogram comparison (weight: 40%)
            if 'histogram' in features1 and 'histogram' in features2:
                hist_corr = cv2.compareHist(features1['histogram'], features2['histogram'], cv2.HISTCMP_CORREL)
                score += hist_corr * 40
                total_weight += 40
            
            # Intensity comparison (weight: 20%)
            if 'avg_intensity' in features1 and 'avg_intensity' in features2:
                intensity_diff = abs(features1['avg_intensity'] - features2['avg_intensity'])
                intensity_sim = max(0, 1 - intensity_diff / 255)
                score += intensity_sim * 20
                total_weight += 20
            
            # Corner comparison (weight: 20%)
            if 'corners' in features1 and 'corners' in features2:
                corner_corr = np.corrcoef(features1['corners'], features2['corners'])[0, 1]
                if not np.isnan(corner_corr):
                    score += max(0, corner_corr) * 20
                    total_weight += 20
            
            # Center comparison (weight: 20%)
            if 'center' in features1 and 'center' in features2:
                center_corr = np.corrcoef(features1['center'], features2['center'])[0, 1]
                if not np.isnan(center_corr):
                    score += max(0, center_corr) * 20
                    total_weight += 20
            
            if total_weight > 0:
                final_score = score / total_weight
                return max(0, min(1, final_score))  # Ensure between 0 and 1
            else:
                return 0
                
        except Exception as e:
            print(f"Face comparison error: {str(e)}")
            return 0
    
    def register_face(self, username, image_data):
        """Register a face"""
        try:
            if username in self.known_face_names:
                return False, "User already exists"
            
            image_array = self.process_image(image_data)
            if image_array is None:
                return False, "Failed to process image"
            
            features, message = self.create_face_signature(image_array)
            if features is None:
                return False, message
            
            # Save features
            filepath = os.path.join(self.user_faces_dir, f"{username}_simple.pkl")
            with open(filepath, 'wb') as f:
                pickle.dump(features, f)
            
            # Update in-memory data
            self.known_face_hashes[username] = features
            self.known_face_names.append(username)
            
            print(f"Face registered for {username}")
            return True, f"Face registered successfully for {username}"
            
        except Exception as e:
            return False, f"Registration error: {str(e)}"
    
    def recognize_face(self, image_data, tolerance=0.5):
        """Recognize a face"""
        try:
            if not self.known_face_hashes:
                return None, 0.0, "No registered users found"
            
            image_array = self.process_image(image_data)
            if image_array is None:
                return None, 0.0, "Failed to process image"
            
            features, message = self.create_face_signature(image_array)
            if features is None:
                return None, 0.0, message
            
            # Compare with all known faces
            best_match = None
            best_score = 0
            
            for username, known_features in self.known_face_hashes.items():
                score = self.compare_faces(features, known_features)
                print(f"Comparing with {username}: score = {score:.3f}")
                
                if score > best_score:
                    best_score = score
                    best_match = username
            
            confidence = best_score * 100
            print(f"Best match: {best_match}, confidence: {confidence:.1f}%, threshold: {tolerance*100}%")
            
            if best_score >= tolerance:
                return best_match, confidence, f"Face recognized as {best_match}"
            else:
                return None, confidence, f"Face not recognized. Best match: {confidence:.1f}% (needed: {tolerance*100}%)"
                
        except Exception as e:
            return None, 0.0, f"Recognition error: {str(e)}"
    
    def get_registered_users(self):
        """Get registered users"""
        return self.known_face_names.copy()
    
    def delete_user(self, username):
        """Delete a user"""
        try:
            # Remove from memory
            if username in self.known_face_hashes:
                del self.known_face_hashes[username]
            if username in self.known_face_names:
                self.known_face_names.remove(username)
            
            # Remove file
            filepath = os.path.join(self.user_faces_dir, f"{username}_simple.pkl")
            if os.path.exists(filepath):
                os.remove(filepath)
            
            return True, f"User {username} deleted successfully"
            
        except Exception as e:
            return False, f"Error deleting user: {str(e)}"