# AI Interview Avatar System

A full-stack AI-powered interview system with customizable avatars, real-time video/audio processing, and intelligent question generation.

## 🚀 Features

- **AI-Powered Interviews**: Generate custom interview questions based on job roles and descriptions
- **Avatar Interviewers**: Customizable AI avatars with lip-sync and TTS capabilities
- **Real-time Processing**: WebRTC integration for live video/audio streaming
- **Smart Evaluation**: AI-powered candidate assessment and report generation
- **Role-based Access**: Admin, Interviewer, and Candidate roles with secure authentication
- **Media Management**: File-based storage for resumes, audio, and video responses

## 🏗️ Architecture

- **Frontend**: React 18 + TailwindCSS + WebRTC
- **Backend**: FastAPI + SQLAlchemy + MySQL
- **AI Services**: Whisper (transcription), TTS (text-to-speech), Question Generation
- **Database**: MySQL with Alembic migrations
- **Authentication**: JWT-based with role-based access control

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- MySQL 8.0+
- Redis (for background tasks)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai-interview-avatar-system
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
cd backend
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

#### Database Setup

1. **Create MySQL Database**
```sql
CREATE DATABASE ai_interview CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ai_interview_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON ai_interview.* TO 'ai_interview_user'@'localhost';
FLUSH PRIVILEGES;
```

2. **Configure Environment Variables**
```bash
cp env.example .env
```

Edit `.env` with your database credentials:
```env
DATABASE_URL=mysql+aiomysql://ai_interview_user:your_password@localhost:3306/ai_interview
SECRET_KEY=your-super-secret-key-change-this-in-production
```

3. **Run Database Migrations**
```bash
# Initialize Alembic (first time only)
alembic init alembic

# Generate initial migration
alembic revision --autogenerate -m "Initial database schema"

# Apply migrations
alembic upgrade head
```

#### Create Uploads Directory
```bash
mkdir uploads
mkdir uploads/resumes
mkdir uploads/audio
mkdir uploads/video
```

### 3. Frontend Setup

```bash
cd ../frontend
npm install
```

## 🚀 Running the Application

### 1. Start MySQL and Redis

```bash
# Start MySQL (Windows)
net start mysql

# Start MySQL (macOS with Homebrew)
brew services start mysql

# Start Redis (Windows)
redis-server

# Start Redis (macOS with Homebrew)
brew services start redis
```

### 2. Start Backend Server

```bash
cd backend
# Activate virtual environment if not already active
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at: http://localhost:8000

### 3. Start Frontend Development Server

```bash
cd frontend
npm start
```

The frontend will be available at: http://localhost:3000

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📚 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh JWT token

### Interview Management
- `POST /api/interviews/create` - Create interview configuration
- `GET /api/interviews/configs` - Get user's interview configs
- `POST /api/interviews/generate-questions` - Generate AI questions
- `PUT /api/interviews/configs/{id}` - Update interview config
- `DELETE /api/interviews/configs/{id}` - Delete interview config

### AI Services
- `POST /api/ai/transcribe` - Transcribe audio/video
- `POST /api/ai/tts` - Text-to-speech conversion
- `POST /api/ai/generate-questions` - Generate interview questions

### Candidates
- `POST /api/candidates/register` - Candidate registration
- `POST /api/candidates/upload-resume` - Upload resume
- `GET /api/candidates/{id}` - Get candidate details

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | MySQL connection string | `mysql+aiomysql://username:password@localhost:3306/ai_interview` |
| `SECRET_KEY` | JWT secret key | `your-secret-key-here` |
| `DEBUG` | Debug mode | `True` |
| `UPLOAD_DIR` | File upload directory | `uploads` |
| `MAX_FILE_SIZE` | Maximum file size (bytes) | `10485760` (10MB) |

### AI Service Configuration

| Variable | Description | Options |
|----------|-------------|---------|
| `TRANSCRIPTION_PROVIDER` | Speech-to-text service | `whisper`, `openai`, `huggingface` |
| `TTS_PROVIDER` | Text-to-speech service | `coqui`, `huggingface` |
| `OPENAI_API_KEY` | OpenAI API key (optional) | Your OpenAI API key |

## 🗄️ Database Schema

### Core Tables

- **users**: User accounts with role-based access
- **interview_configs**: Interview configurations and settings
- **questions**: Interview questions with metadata
- **candidates**: Candidate information and resumes
- **interview_sessions**: Active interview sessions
- **responses**: Candidate responses with media
- **reports**: AI-generated evaluation reports

### Key Features

- **UUID Primary Keys**: All tables use UUIDs instead of auto-increment IDs
- **JSON Fields**: Flexible storage for tags, focus areas, and breakdowns
- **File Paths**: Media files stored on filesystem with database references
- **Relationships**: Proper foreign key constraints and cascading deletes

## 🔄 Database Migrations

### Creating New Migrations

```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

### Applying Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Rollback to specific revision
alembic downgrade <revision_id>

# Check current migration status
alembic current
```

### Migration Best Practices

1. **Always backup** your database before running migrations
2. **Test migrations** on a copy of production data
3. **Review generated migrations** before applying
4. **Use descriptive names** for migration messages

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**: Set `DEBUG=False` in production
2. **Database**: Use production MySQL instance with proper credentials
3. **File Storage**: Configure proper file paths and permissions
4. **Security**: Use strong SECRET_KEY and HTTPS
5. **Monitoring**: Set up logging and health checks

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d
```

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Verify MySQL is running
   - Check database credentials in `.env`
   - Ensure database exists

2. **Migration Errors**
   - Check MySQL version compatibility
   - Verify database user permissions
   - Review migration files for syntax errors

3. **File Upload Issues**
   - Check upload directory permissions
   - Verify file size limits
   - Check allowed file extensions

### Logs

- **Backend**: Check console output and application logs
- **Database**: Check MySQL error logs
- **Frontend**: Check browser console and network tab

## 📖 Development

### Code Structure

```
backend/
├── app/
│   ├── db.py              # Database configuration
│   ├── orm_models.py      # SQLAlchemy models
│   ├── repositories/      # Data access layer
│   └── config.py          # Configuration management
├── services/              # Business logic
├── routes/                # API endpoints
├── models/                # Pydantic models
└── utils/                 # Utility functions

frontend/
├── src/
│   ├── components/        # React components
│   ├── pages/            # Page components
│   ├── services/         # API services
│   └── contexts/         # React contexts
```

### Adding New Features

1. **Database**: Add models to `orm_models.py`
2. **API**: Create routes in `routes/` directory
3. **Business Logic**: Implement in `services/` directory
4. **Frontend**: Add components and pages
5. **Migrations**: Generate and test database changes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation at `/docs`

## 🔮 Roadmap

- [ ] Enhanced AI question generation
- [ ] Real-time collaboration features
- [ ] Advanced analytics dashboard
- [ ] Mobile application
- [ ] Multi-language support
- [ ] Integration with HR systems

---

**Note**: This system is designed for educational and development purposes. For production use, ensure proper security measures, data privacy compliance, and thorough testing.


