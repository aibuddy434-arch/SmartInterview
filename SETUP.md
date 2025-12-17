# Setup Guide - AI Interview Avatar System

This guide will walk you through setting up the AI Interview Avatar System step by step.

## 🚀 Quick Start (Recommended)

### For Unix/Linux/macOS:
```bash
chmod +x quick-start.sh
./quick-start.sh
```

### For Windows:
```cmd
quick-start.bat
```

## 📋 Manual Setup

If you prefer to set up manually or the quick start scripts don't work, follow these steps:

### 1. Prerequisites Installation

#### Python 3.8+
- **Windows**: Download from [python.org](https://python.org)
- **macOS**: `brew install python3`
- **Ubuntu/Debian**: `sudo apt install python3 python3-venv`

#### Node.js 16+
- **Windows**: Download from [nodejs.org](https://nodejs.org)
- **macOS**: `brew install node`
- **Ubuntu/Debian**: `curl -fsSL https://deb.nodesource.com/setup_16.x | sudo -E bash - && sudo apt-get install -y nodejs`

#### MySQL 8.0+
- **Windows**: Download MySQL Installer from [mysql.com](https://mysql.com)
- **macOS**: `brew install mysql`
- **Ubuntu/Debian**: `sudo apt install mysql-server`

#### Redis (Optional, for background tasks)
- **Windows**: Download from [redis.io](https://redis.io)
- **macOS**: `brew install redis`
- **Ubuntu/Debian**: `sudo apt install redis-server`

### 2. Database Setup

#### Create MySQL Database
```sql
-- Connect to MySQL as root
mysql -u root -p

-- Create database and user
CREATE DATABASE ai_interview CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ai_interview_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON ai_interview.* TO 'ai_interview_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### Test Connection
```bash
mysql -u ai_interview_user -p ai_interview
# Enter your password when prompted
# You should see the MySQL prompt
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Unix/Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your database credentials
# Use your favorite editor (nano, vim, notepad, etc.)
nano .env
```

#### Environment Variables (.env)
```env
# Database Configuration
DATABASE_URL=mysql+aiomysql://ai_interview_user:your_secure_password@localhost:3306/ai_interview

# JWT Configuration
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000

# File Upload Configuration
MAX_FILE_SIZE=10485760
UPLOAD_DIR=uploads
ALLOWED_EXTENSIONS=pdf,doc,docx,txt,mp3,mp4,wav,avi

# AI Services Configuration
TRANSCRIPTION_PROVIDER=whisper
OPENAI_API_KEY=your-openai-api-key-here
HUGGINGFACE_API_KEY=your-huggingface-api-key-here
TTS_PROVIDER=coqui

# Redis Configuration
REDIS_URL=redis://localhost:6379/0
```

#### Create Upload Directories
```bash
mkdir uploads
mkdir uploads/resumes
mkdir uploads/audio
mkdir uploads/video
```

#### Run Database Migrations
```bash
# Initialize Alembic (first time only)
alembic init alembic

# Generate initial migration
alembic revision --autogenerate -m "Initial database schema"

# Apply migrations
alembic upgrade head
```

### 4. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install
```

### 5. Start Services

#### Terminal 1 - Backend
```bash
cd backend
source venv/bin/activate  # Unix/Linux/macOS
# OR
venv\Scripts\activate     # Windows

uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Terminal 2 - Frontend
```bash
cd frontend
npm start
```

## 🔧 Configuration Options

### Database Configuration
- **Host**: Default is `localhost`
- **Port**: Default is `3306`
- **Database**: Default is `ai_interview`
- **Character Set**: `utf8mb4` for full Unicode support

### File Upload Settings
- **Max File Size**: Default is 10MB
- **Allowed Extensions**: PDF, DOC, DOCX, TXT, MP3, MP4, WAV, AVI
- **Upload Directory**: `uploads/` in backend directory

### AI Services
- **Transcription**: Whisper (default), OpenAI Whisper API, HuggingFace
- **TTS**: Coqui TTS (default), HuggingFace TTS
- **Question Generation**: HuggingFace Transformers

## 🐛 Troubleshooting

### Common Issues

#### 1. Database Connection Error
```
Error: (aiomysql.err.OperationalError) (2003, "Can't connect to MySQL server")
```
**Solution**: Ensure MySQL is running and credentials are correct

#### 2. Migration Errors
```
Error: (aiomysql.err.OperationalError) (1045, "Access denied for user")
```
**Solution**: Check database user permissions and credentials

#### 3. Port Already in Use
```
Error: [Errno 98] Address already in use
```
**Solution**: Change port in `.env` or stop conflicting service

#### 4. Module Not Found
```
ModuleNotFoundError: No module named 'sqlalchemy'
```
**Solution**: Activate virtual environment and install requirements

#### 5. Frontend Build Errors
```
npm ERR! code ELIFECYCLE
```
**Solution**: Clear node_modules and reinstall: `rm -rf node_modules package-lock.json && npm install`

### Debug Mode

Enable debug mode in `.env`:
```env
DEBUG=True
```

This will:
- Show detailed error messages
- Log SQL queries
- Enable auto-reload
- Show stack traces

### Logs

#### Backend Logs
- Check terminal output for errors
- SQL queries are logged when `DEBUG=True`

#### Database Logs
```bash
# MySQL error log (Linux)
sudo tail -f /var/log/mysql/error.log

# MySQL error log (macOS)
tail -f /usr/local/var/mysql/*.err
```

#### Frontend Logs
- Check browser console (F12)
- Check terminal output for build errors

## 🔒 Security Considerations

### Production Deployment

1. **Environment Variables**
   - Set `DEBUG=False`
   - Use strong, unique `SECRET_KEY`
   - Store sensitive data in environment variables

2. **Database Security**
   - Use dedicated database user with minimal privileges
   - Enable SSL connections
   - Regular backups

3. **File Uploads**
   - Validate file types and sizes
   - Scan for malware
   - Store files outside web root

4. **Network Security**
   - Use HTTPS in production
   - Configure firewall rules
   - Rate limiting

## 📊 Performance Tuning

### Database Optimization
```sql
-- Add indexes for common queries
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_interview_configs_created_by ON interview_configs(created_by);
CREATE INDEX idx_sessions_candidate_id ON interview_sessions(candidate_id);
```

### Backend Optimization
- Use connection pooling
- Implement caching (Redis)
- Background task processing

### Frontend Optimization
- Code splitting
- Lazy loading
- Image optimization

## 🔄 Updates and Maintenance

### Updating Dependencies
```bash
# Backend
cd backend
source venv/bin/activate
pip install --upgrade -r requirements.txt

# Frontend
cd ../frontend
npm update
```

### Database Migrations
```bash
cd backend
source venv/bin/activate

# Check for new migrations
alembic current

# Apply new migrations
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

### Backup and Restore
```bash
# Backup database
mysqldump -u ai_interview_user -p ai_interview > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database
mysql -u ai_interview_user -p ai_interview < backup_file.sql
```

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the logs for error messages
3. Check the API documentation at `/docs`
4. Create an issue in the repository
5. Ensure all prerequisites are met

## 🎯 Next Steps

After successful setup:

1. **Test the System**
   - Register an admin user
   - Create an interview configuration
   - Generate AI questions
   - Test candidate flow

2. **Customize Configuration**
   - Adjust AI service providers
   - Configure file upload limits
   - Set up email notifications

3. **Deploy to Production**
   - Set up production database
   - Configure web server (Nginx/Apache)
   - Set up SSL certificates
   - Configure monitoring

---

**Happy Interviewing! 🎉**

