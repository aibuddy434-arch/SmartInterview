# AI Interview Avatar System - Backend

This is the FastAPI backend for the AI Interview Avatar System, providing a robust API for managing interviews, candidates, and user authentication.

## Features

- **User Authentication**: JWT-based authentication with role-based access control
- **Interview Management**: Create, update, and manage interview sessions
- **Candidate Management**: Handle candidate registration and responses
- **File Uploads**: Support for resume and response file uploads
- **MongoDB Integration**: Async MongoDB operations using Motor
- **RESTful API**: Clean, documented API endpoints

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **MongoDB**: NoSQL database for flexible data storage
- **Motor**: Async MongoDB driver for Python
- **JWT**: JSON Web Tokens for authentication
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: ASGI server for running FastAPI

## Prerequisites

- Python 3.8+
- MongoDB (local or MongoDB Atlas)
- pip (Python package manager)

## Installation

1. **Clone the repository and navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Configure MongoDB:**
   - For local MongoDB: Ensure MongoDB is running on localhost:27017
   - For MongoDB Atlas: Update MONGODB_URL in .env with your connection string

## Configuration

Create a `.env` file with the following variables:

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=ai_interview_system

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server Configuration
HOST=0.0.0.0
PORT=8000

# CORS Configuration
ALLOWED_ORIGINS=["http://localhost:3000"]

# File Upload Configuration
MAX_FILE_SIZE=10485760
UPLOAD_FOLDER=uploads
```

## Running the Application

1. **Start the server:**
   ```bash
   python main.py
   ```

2. **Or using uvicorn directly:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Access the API:**
   - API Base URL: http://localhost:8000
   - Interactive API Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/refresh` - Refresh access token

### Admin Management
- `GET /api/admin/users` - Get all users (admin only)
- `POST /api/admin/users` - Create new user (admin only)
- `PUT /api/admin/users/{user_id}` - Update user (admin only)
- `DELETE /api/admin/users/{user_id}` - Delete user (admin only)
- `GET /api/admin/stats` - System statistics (admin only)

### Interview Management
- `POST /api/admin/interviews` - Create interview (admin/interviewer)
- `GET /api/admin/interviews` - Get all interviews (admin/interviewer)
- `GET /api/interviews/public/{interview_id}` - Public interview info
- `POST /api/interviews/join/{interview_id}` - Join interview as candidate
- `POST /api/interviews/sessions/{session_id}/start` - Start interview session
- `POST /api/interviews/sessions/{session_id}/submit-response` - Submit response
- `POST /api/interviews/sessions/{session_id}/complete` - Complete interview

### Candidate Management
- `GET /api/candidates` - Get all candidates (admin/interviewer)
- `GET /api/candidates/{candidate_id}` - Get candidate details
- `PUT /api/candidates/{candidate_id}` - Update candidate
- `POST /api/candidates/{candidate_id}/resume` - Upload resume
- `GET /api/candidates/{candidate_id}/report` - Get candidate report

## Database Schema

The system uses MongoDB with the following collections:

- **users**: User accounts and authentication
- **interviews**: Interview session configurations
- **candidates**: Candidate information and profiles
- **sessions**: Interview session instances
- **responses**: Candidate responses to interview questions

## File Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuration settings
│   └── database.py        # Database connection and setup
├── models/
│   ├── __init__.py
│   ├── user.py            # User data models
│   ├── interview.py       # Interview data models
│   └── candidate.py       # Candidate data models
├── routes/
│   ├── __init__.py
│   ├── auth.py            # Authentication endpoints
│   ├── admin.py           # Admin management endpoints
│   ├── interviews.py      # Interview endpoints
│   └── candidates.py      # Candidate endpoints
├── utils/
│   ├── __init__.py
│   └── auth.py            # Authentication utilities
├── main.py                # FastAPI application entry point
├── requirements.txt       # Python dependencies
├── env.example            # Environment variables template
└── README.md              # This file
```

## Development

### Adding New Endpoints

1. Create or update the appropriate model in `models/`
2. Add the endpoint logic in the corresponding route file
3. Update the main.py to include new routers if needed
4. Test the endpoint using the interactive API docs

### Database Migrations

The current implementation uses MongoDB which is schema-less, but you can add migration scripts in a `migrations/` directory if needed.

### Testing

Run tests using pytest:
```bash
pip install pytest
pytest
```

## Deployment

### Production Considerations

1. **Environment Variables**: Use strong, unique SECRET_KEY
2. **MongoDB**: Use MongoDB Atlas or secure MongoDB instance
3. **HTTPS**: Enable SSL/TLS in production
4. **Rate Limiting**: Implement rate limiting for API endpoints
5. **Monitoring**: Add logging and monitoring
6. **Backup**: Regular database backups

### Docker Deployment

Create a Dockerfile:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review the logs for error messages
3. Ensure all environment variables are set correctly
4. Verify MongoDB connection and permissions

## License

This project is part of the AI Interview Avatar System.

