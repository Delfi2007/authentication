# Face Recognition Authentication System

This project implements a face recognition authentication system using Flask and the face_recognition library.

## Features

- **User Registration**: Register users with face encoding
- **Face Recognition Login**: Login using facial recognition
- **User Management**: Create, view, and manage users
- **Login Attempts Tracking**: Track all login attempts with timestamps
- **Web Interface**: Built-in web interface for testing
- **RESTful API**: Complete REST API for integration

## Project Structure

```
d:\authentication\
├── app.py                      # Main Flask application
├── face_recognition_system.py  # Face recognition logic
├── database.py                 # Database models and operations
├── requirements.txt            # Python dependencies
├── user_faces/                 # Directory for stored face encodings
├── uploads/                    # Directory for temporary uploads
└── face_auth.db               # SQLite database (created automatically)
```

## Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

Note: You may need to install Visual Studio Build Tools on Windows for dlib compilation.

## Usage

1. **Start the server:**
```bash
python app.py
```

2. **Open your browser and go to:** http://localhost:5000

3. **Test the system:**
   - Register a new user with a face image
   - Try logging in with the same face
   - View registered users and system statistics

## API Endpoints

### User Registration
- **POST** `/register`
- **Parameters:** username, email (optional), full_name (optional), image
- **Response:** Success/failure with user details

### Face Recognition Login
- **POST** `/login` 
- **Parameters:** image
- **Response:** Success/failure with user details and confidence score

### Get Users
- **GET** `/users`
- **Response:** List of all registered users

### Get User Details
- **GET** `/user/<username>`
- **Response:** User details and recent login attempts

### System Statistics
- **GET** `/stats`
- **Response:** System statistics (total users, users with face, etc.)

### Health Check
- **GET** `/health`
- **Response:** Service health status

## Testing with Terminal/Command Line

You can test the API using curl commands:

```bash
# Health check
curl http://localhost:5000/health

# Get system stats
curl http://localhost:5000/stats

# Get all users
curl http://localhost:5000/users
```

## Face Recognition Details

- Uses the `face_recognition` library built on dlib
- Stores face encodings as pickle files
- Supports confidence-based matching
- Default tolerance: 0.6 (adjustable)
- Handles multiple face detection errors

## Database Schema

### Users Table
- id, username, email, full_name
- is_active, face_registered
- created_at, last_login

### Login Attempts Table
- user_id, attempted_username, success
- confidence, method, ip_address
- timestamp, error_message

## Security Notes

- Change the SECRET_KEY in production
- Implement rate limiting for production use
- Add HTTPS in production
- Consider adding JWT tokens for session management
- Validate and sanitize all inputs

## Troubleshooting

1. **Camera issues**: Ensure browser permissions for camera access
2. **Face not detected**: Use well-lit photos with clear face visibility
3. **Low confidence**: Retrain with better quality images
4. **Installation issues**: Install Visual Studio Build Tools for Windows