import cv2
import numpy as np
import pickle
import os
import hashlib
import json
import logging
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from engine.config import FACE_RECOGNITION_CONFIG, SECURITY_CONFIG

# Optional imports with fallbacks
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    logging.warning("face_recognition not available, face recognition disabled")

try:
    from cryptography.fernet import Fernet
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    logging.warning("cryptography not available, encryption disabled")

class EnhancedFaceRecognition:
    def __init__(self):
        self.known_faces = {}
        self.known_face_encodings = []
        self.known_face_names = []
        self.encryption_key = None
        self.logger = logging.getLogger(__name__)
        self.setup_encryption()
        self.load_face_data()
        
    def setup_encryption(self):
        """Setup encryption for face data"""
        if not CRYPTOGRAPHY_AVAILABLE:
            self.logger.warning("Cryptography not available, encryption disabled")
            return
            
        if SECURITY_CONFIG['encrypt_database']:
            key_file = 'face_encryption.key'
            if os.path.exists(key_file):
                with open(key_file, 'rb') as f:
                    self.encryption_key = f.read()
            else:
                self.encryption_key = Fernet.generate_key()
                with open(key_file, 'wb') as f:
                    f.write(self.encryption_key)
            self.cipher = Fernet(self.encryption_key)
    
    def encrypt_data(self, data: bytes) -> bytes:
        """Encrypt face data"""
        if CRYPTOGRAPHY_AVAILABLE and SECURITY_CONFIG['encrypt_database']:
            return self.cipher.encrypt(data)
        return data
    
    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt face data"""
        if CRYPTOGRAPHY_AVAILABLE and SECURITY_CONFIG['encrypt_database']:
            return self.cipher.decrypt(encrypted_data)
        return encrypted_data
    
    def load_face_data(self):
        """Load existing face data from encrypted storage"""
        face_data_file = 'face_data.enc'
        if os.path.exists(face_data_file):
            try:
                with open(face_data_file, 'rb') as f:
                    encrypted_data = f.read()
                decrypted_data = self.decrypt_data(encrypted_data)
                face_data = pickle.loads(decrypted_data)
                
                self.known_faces = face_data.get('faces', {})
                self.known_face_encodings = face_data.get('encodings', [])
                self.known_face_names = face_data.get('names', [])
                
                self.logger.info(f"Loaded {len(self.known_faces)} known faces")
            except Exception as e:
                self.logger.error(f"Error loading face data: {e}")
    
    def save_face_data(self):
        """Save face data to encrypted storage"""
        face_data = {
            'faces': self.known_faces,
            'encodings': self.known_face_encodings,
            'names': self.known_face_names,
            'last_updated': datetime.now().isoformat()
        }
        
        try:
            encrypted_data = self.encrypt_data(pickle.dumps(face_data))
            with open('face_data.enc', 'wb') as f:
                f.write(encrypted_data)
            self.logger.info("Face data saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving face data: {e}")
    
    def add_user(self, name: str, face_images: List[str]) -> bool:
        """Add a new user with multiple face images"""
        if not FACE_RECOGNITION_AVAILABLE:
            self.logger.error("Face recognition not available")
            return False
            
        try:
            face_encodings = []
            
            for image_path in face_images:
                if not os.path.exists(image_path):
                    self.logger.warning(f"Image not found: {image_path}")
                    continue
                
                # Load and encode face
                image = face_recognition.load_image_file(image_path)
                encodings = face_recognition.face_encodings(image)
                
                if encodings:
                    face_encodings.extend(encodings)
                else:
                    self.logger.warning(f"No face found in {image_path}")
            
            if not face_encodings:
                self.logger.error("No valid faces found in provided images")
                return False
            
            # Store user data
            user_id = self.generate_user_id(name)
            self.known_faces[user_id] = {
                'name': name,
                'encodings': face_encodings,
                'added_date': datetime.now().isoformat(),
                'last_seen': None,
                'access_count': 0
            }
            
            # Update lists for recognition
            self.known_face_encodings.extend(face_encodings)
            self.known_face_names.extend([name] * len(face_encodings))
            
            self.save_face_data()
            self.logger.info(f"User {name} added successfully with {len(face_encodings)} face encodings")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding user {name}: {e}")
            return False
    
    def generate_user_id(self, name: str) -> str:
        """Generate unique user ID"""
        timestamp = datetime.now().isoformat()
        unique_string = f"{name}_{timestamp}"
        return hashlib.sha256(unique_string.encode()).hexdigest()[:16]
    
    def authenticate_face(self, tolerance: float = 0.6) -> Tuple[bool, Optional[str], float]:
        """Authenticate face with enhanced features"""
        if not FACE_RECOGNITION_AVAILABLE:
            self.logger.error("Face recognition not available")
            return False, None, 0.0
            
        try:
            # Initialize camera
            cap = cv2.VideoCapture(0)
            cap.set(3, 640)
            cap.set(4, 480)
            
            if not cap.isOpened():
                self.logger.error("Could not open camera")
                return False, None, 0.0
            
            self.logger.info("Starting face authentication...")
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    continue
                
                # Resize frame for faster processing
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = small_frame[:, :, ::-1]
                
                # Find faces in frame
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                
                face_names = []
                face_confidences = []
                
                for face_encoding in face_encodings:
                    # Compare with known faces
                    matches = face_recognition.compare_faces(
                        self.known_face_encodings, 
                        face_encoding, 
                        tolerance=tolerance
                    )
                    
                    if True in matches:
                        # Get best match
                        face_distances = face_recognition.face_distance(
                            self.known_face_encodings, 
                            face_encoding
                        )
                        best_match_index = np.argmin(face_distances)
                        
                        if matches[best_match_index]:
                            name = self.known_face_names[best_match_index]
                            confidence = 1.0 - face_distances[best_match_index]
                            
                            face_names.append(name)
                            face_confidences.append(confidence)
                            
                            # Check liveness detection
                            if FACE_RECOGNITION_CONFIG['liveness_detection']:
                                if not self.detect_liveness(frame):
                                    self.logger.warning("Liveness detection failed")
                                    continue
                            
                            # Update user access record
                            self.update_user_access(name)
                            
                            # Draw results on frame
                            self.draw_face_results(frame, face_locations, face_names, face_confidences)
                            
                            # Show frame
                            cv2.imshow('Face Authentication', frame)
                            
                            # Wait for key press
                            key = cv2.waitKey(1) & 0xFF
                            if key == 27:  # ESC
                                break
                            
                            if confidence > 0.7:  # High confidence threshold
                                cap.release()
                                cv2.destroyAllWindows()
                                return True, name, confidence
                
                # Draw results on frame
                self.draw_face_results(frame, face_locations, face_names, face_confidences)
                cv2.imshow('Face Authentication', frame)
                
                # Check for exit
                key = cv2.waitKey(1) & 0xFF
                if key == 27:  # ESC
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            return False, None, 0.0
            
        except Exception as e:
            self.logger.error(f"Error during face authentication: {e}")
            return False, None, 0.0
    
    def detect_liveness(self, frame) -> bool:
        """Basic liveness detection"""
        # This is a simplified implementation
        # In production, use more sophisticated liveness detection
        
        # Check for eye blink detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        eyes = eye_cascade.detectMultiScale(gray, 1.1, 5)
        
        # Simple check: if eyes are detected, consider it live
        return len(eyes) >= 2
    
    def draw_face_results(self, frame, face_locations, face_names, face_confidences):
        """Draw face recognition results on frame"""
        for (top, right, bottom, left), name, confidence in zip(face_locations, face_names, face_confidences):
            # Scale back up face locations
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            
            # Draw rectangle around face
            color = (0, 255, 0) if confidence > 0.7 else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            
            # Draw label
            label = f"{name} ({confidence:.2f})"
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
            cv2.putText(frame, label, (left + 6, bottom - 6), 
                       cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
    
    def update_user_access(self, name: str):
        """Update user access statistics"""
        for user_id, user_data in self.known_faces.items():
            if user_data['name'] == name:
                user_data['last_seen'] = datetime.now().isoformat()
                user_data['access_count'] += 1
                break
    
    def remove_user(self, name: str) -> bool:
        """Remove a user from the system"""
        try:
            user_to_remove = None
            for user_id, user_data in self.known_faces.items():
                if user_data['name'] == name:
                    user_to_remove = user_id
                    break
            
            if user_to_remove:
                # Remove from known_faces
                del self.known_faces[user_to_remove]
                
                # Rebuild encoding lists
                self.known_face_encodings = []
                self.known_face_names = []
                
                for user_data in self.known_faces.values():
                    self.known_face_encodings.extend(user_data['encodings'])
                    self.known_face_names.extend([user_data['name']] * len(user_data['encodings']))
                
                self.save_face_data()
                self.logger.info(f"User {name} removed successfully")
                return True
            else:
                self.logger.warning(f"User {name} not found")
                return False
                
        except Exception as e:
            self.logger.error(f"Error removing user {name}: {e}")
            return False
    
    def get_user_statistics(self) -> Dict:
        """Get user access statistics"""
        stats = {}
        for user_id, user_data in self.known_faces.items():
            stats[user_data['name']] = {
                'added_date': user_data['added_date'],
                'last_seen': user_data['last_seen'],
                'access_count': user_data['access_count']
            }
        return stats
    
    def list_users(self) -> List[str]:
        """List all registered users"""
        return [user_data['name'] for user_data in self.known_faces.values()] 