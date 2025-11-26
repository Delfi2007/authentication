import cv2
import numpy as np
import os
import pickle
from PIL import Image
import io
from ultralytics import YOLO
import requests
from scipy.spatial.distance import cosine

class SimpleFaceRecognitionSystem:
    def __init__(self, user_faces_dir="user_faces"):
        self.user_faces_dir = user_faces_dir
        self.known_face_features = []
        self.known_face_names = []
        
        # Try to load YOLO model, fallback to OpenCV if not available
        try:
            self.yolo_model = YOLO('yolov8n-face.pt')  # You can also use 'yolov8n.pt' for general object detection
            self.use_yolo = True
            print("YOLO face detection model loaded successfully!")
        except:
            # Fallback to OpenCV Haar Cascade
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            self.use_yolo = False
            print("Using OpenCV Haar Cascade for face detection")
        
        self.load_known_faces()
    
    def load_known_faces(self):
        """Load all known face features from the user_faces directory"""
        self.known_face_features = []
        self.known_face_names = []
        
        if not os.path.exists(self.user_faces_dir):
            os.makedirs(self.user_faces_dir)
            return
        
        for filename in os.listdir(self.user_faces_dir):
            if filename.endswith('.pkl'):
                username = filename.replace('.pkl', '')
                filepath = os.path.join(self.user_faces_dir, filename)
                try:
                    with open(filepath, 'rb') as f:
                        face_features = pickle.load(f)
                        self.known_face_features.append(face_features)
                        self.known_face_names.append(username)
                        print(f"Loaded face features for user: {username}")
                except Exception as e:
                    print(f"Error loading face features for {username}: {str(e)}")
    
    def save_face_features(self, username, face_features):
        """Save face features to a pickle file"""
        if not os.path.exists(self.user_faces_dir):
            os.makedirs(self.user_faces_dir)
        
        filepath = os.path.join(self.user_faces_dir, f"{username}.pkl")
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(face_features, f)
            print(f"Face features saved for user: {username}")
            return True
        except Exception as e:
            print(f"Error saving face features for {username}: {str(e)}")
            return False
    
    def detect_faces_yolo(self, image):
        """Detect faces using YOLO"""
        try:
            results = self.yolo_model(image)
            faces = []
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        # Get bounding box coordinates
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        confidence = float(box.conf[0])
                        
                        # Only consider high confidence detections
                        if confidence > 0.5:
                            faces.append((x1, y1, x2-x1, y2-y1))  # Convert to (x, y, w, h)
            
            return faces
        except Exception as e:
            print(f"YOLO face detection error: {str(e)}")
            return []
    
    def detect_faces_opencv(self, image):
        """Detect faces using OpenCV Haar Cascade"""
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            else:
                gray = image
            
            # Enhance contrast
            gray = cv2.equalizeHist(gray)
            
            # Detect faces with multiple scale factors for better detection
            faces1 = self.face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(30, 30))
            faces2 = self.face_cascade.detectMultiScale(gray, 1.2, 3, minSize=(50, 50))
            faces3 = self.face_cascade.detectMultiScale(gray, 1.3, 3, minSize=(80, 80))
            
            # Combine all detections
            all_faces = []
            if len(faces1) > 0:
                all_faces.extend(faces1.tolist())
            if len(faces2) > 0:
                all_faces.extend(faces2.tolist())
            if len(faces3) > 0:
                all_faces.extend(faces3.tolist())
            
            if not all_faces:
                return []
            
            # Remove duplicate detections (non-maximum suppression)
            if len(all_faces) > 1:
                # Simple overlap removal
                final_faces = []
                for face in all_faces:
                    x, y, w, h = face
                    area = w * h
                    if area > 1000:  # Minimum face area
                        final_faces.append(face)
                
                # If multiple faces, return the largest one
                if len(final_faces) > 1:
                    largest_face = max(final_faces, key=lambda f: f[2] * f[3])
                    return [largest_face]
                elif len(final_faces) == 1:
                    return final_faces
                else:
                    return all_faces[:1] if all_faces else []
            else:
                return all_faces
            
        except Exception as e:
            print(f"OpenCV face detection error: {str(e)}")
            return []
    
    def detect_faces(self, image):
        """Detect faces using the available method"""
        if self.use_yolo:
            return self.detect_faces_yolo(image)
        else:
            return self.detect_faces_opencv(image)
    
    def extract_face_features(self, image_data):
        """Extract simple face features from image data"""
        try:
            # Convert image data to numpy array
            if isinstance(image_data, bytes):
                # Convert bytes to PIL Image
                image = Image.open(io.BytesIO(image_data))
                image = np.array(image)
            else:
                image = image_data
            
            # Convert BGR to RGB if necessary
            if len(image.shape) == 3 and image.shape[2] == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            faces = self.detect_faces(image)
            
            if not faces:
                return None, "No face detected in the image"
            
            if len(faces) > 1:
                return None, "Multiple faces detected. Please provide an image with only one face"
            
            # Extract the face region
            x, y, w, h = faces[0]
            face_image = image[y:y+h, x:x+w]
            
            # Resize face to standard size
            face_resized = cv2.resize(face_image, (100, 100))
            
            # Convert to grayscale and extract features
            face_gray = cv2.cvtColor(face_resized, cv2.COLOR_RGB2GRAY) if len(face_resized.shape) == 3 else face_resized
            
            # Simple feature extraction using histogram and texture
            features = {
                'histogram': cv2.calcHist([face_gray], [0], None, [256], [0, 256]).flatten(),
                'lbp_features': self.extract_lbp_features(face_gray),
                'face_dimensions': (w, h),
                'face_area': w * h
            }
            
            return features, "Face features extracted successfully"
                
        except Exception as e:
            return None, f"Error processing image: {str(e)}"
    
    def extract_lbp_features(self, gray_image):
        """Extract Local Binary Pattern features"""
        try:
            # Simple LBP implementation
            rows, cols = gray_image.shape
            lbp = np.zeros((rows-2, cols-2))
            
            for i in range(1, rows-1):
                for j in range(1, cols-1):
                    center = gray_image[i, j]
                    powers = [1, 2, 4, 8, 16, 32, 64, 128]
                    lbp_value = 0
                    
                    # 8-neighborhood
                    neighbors = [
                        gray_image[i-1, j-1], gray_image[i-1, j], gray_image[i-1, j+1],
                        gray_image[i, j+1], gray_image[i+1, j+1], gray_image[i+1, j],
                        gray_image[i+1, j-1], gray_image[i, j-1]
                    ]
                    
                    for k, neighbor in enumerate(neighbors):
                        if neighbor >= center:
                            lbp_value += powers[k]
                    
                    lbp[i-1, j-1] = lbp_value
            
            # Calculate histogram of LBP
            hist = np.histogram(lbp, bins=256, range=(0, 256))[0]
            return hist.astype(float)
            
        except Exception as e:
            print(f"LBP feature extraction error: {str(e)}")
            return np.zeros(256)
    
    def register_face(self, username, image_data):
        """Register a new face for authentication"""
        try:
            # Check if user already exists
            if username in self.known_face_names:
                return False, "User already exists. Use update_face to modify existing user."
            
            # Extract face features
            face_features, message = self.extract_face_features(image_data)
            
            if face_features is None:
                return False, message
            
            # Save face features
            if self.save_face_features(username, face_features):
                # Update in-memory data
                self.known_face_features.append(face_features)
                self.known_face_names.append(username)
                return True, f"Face registered successfully for user: {username}"
            else:
                return False, "Failed to save face features"
                
        except Exception as e:
            return False, f"Error registering face: {str(e)}"
    
    def compare_faces(self, features1, features2):
        """Compare two sets of face features"""
        try:
            # Compare histograms
            hist_similarity = cv2.compareHist(features1['histogram'], features2['histogram'], cv2.HISTCMP_CORREL)
            
            # Compare LBP features using cosine similarity
            lbp_similarity = 1 - cosine(features1['lbp_features'], features2['lbp_features'])
            
            # Compare face dimensions (simple ratio check)
            area1 = features1['face_area']
            area2 = features2['face_area']
            area_ratio = min(area1, area2) / max(area1, area2) if max(area1, area2) > 0 else 0
            
            # Weighted combination of similarities
            total_similarity = (hist_similarity * 0.4 + lbp_similarity * 0.4 + area_ratio * 0.2)
            
            return max(0, total_similarity)  # Ensure non-negative
            
        except Exception as e:
            print(f"Error comparing faces: {str(e)}")
            return 0.0
    
    def recognize_face(self, image_data, tolerance=0.4):
        """Recognize a face and return the username if found"""
        try:
            # Extract face features from the input image
            face_features, message = self.extract_face_features(image_data)
            
            if face_features is None:
                return None, 0.0, message
            
            if not self.known_face_features:
                return None, 0.0, "No registered users found"
            
            # Compare with known faces
            best_match_similarity = 0
            best_match_index = -1
            
            for i, known_features in enumerate(self.known_face_features):
                similarity = self.compare_faces(face_features, known_features)
                
                if similarity > best_match_similarity:
                    best_match_similarity = similarity
                    best_match_index = i
            
            print(f"Best match similarity: {best_match_similarity}, tolerance: {tolerance}")
            
            if best_match_similarity >= tolerance:
                username = self.known_face_names[best_match_index]
                confidence = best_match_similarity * 100  # Convert to percentage
                return username, confidence, f"Face recognized as {username}"
            else:
                return None, 0.0, "Face not recognized. Please register first."
                
        except Exception as e:
            return None, 0.0, f"Error recognizing face: {str(e)}"
    
    def update_face(self, username, image_data):
        """Update existing user's face features"""
        try:
            if username not in self.known_face_names:
                return False, "User not found. Use register_face to add new user."
            
            # Extract face features
            face_features, message = self.extract_face_features(image_data)
            
            if face_features is None:
                return False, message
            
            # Save face features
            if self.save_face_features(username, face_features):
                # Update in-memory data
                user_index = self.known_face_names.index(username)
                self.known_face_features[user_index] = face_features
                return True, f"Face features updated successfully for user: {username}"
            else:
                return False, "Failed to update face features"
                
        except Exception as e:
            return False, f"Error updating face: {str(e)}"
    
    def delete_user(self, username):
        """Delete a user's face features"""
        try:
            if username not in self.known_face_names:
                return False, "User not found"
            
            # Remove from file system
            filepath = os.path.join(self.user_faces_dir, f"{username}.pkl")
            if os.path.exists(filepath):
                os.remove(filepath)
            
            # Remove from in-memory data
            user_index = self.known_face_names.index(username)
            self.known_face_features.pop(user_index)
            self.known_face_names.pop(user_index)
            
            return True, f"User {username} deleted successfully"
            
        except Exception as e:
            return False, f"Error deleting user: {str(e)}"
    
    def get_registered_users(self):
        """Get list of all registered users"""
        return self.known_face_names.copy()
    
    def reload_faces(self):
        """Reload all face features from disk"""
        self.load_known_faces()
        return True, f"Reloaded {len(self.known_face_names)} registered users"

# For backward compatibility, create an alias
FaceRecognitionSystem = SimpleFaceRecognitionSystem