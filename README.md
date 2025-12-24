# 🎤 AI Interview Avatar System

A full-stack AI-powered interview platform featuring dynamic AI interviewers, real-time transcription, intelligent follow-up questions, and comprehensive candidate evaluation reports.

## ⚡ Quick Setup (5 Minutes)

### Prerequisites
- **Python 3.10+** 
- **Node.js 18+**
- **MySQL 8.0+** (running)

### Step 1: Clone & Setup Backend

```bash
# Clone the repository
git clone https://github.com/dchintan80-rgb/AI_Interview.git
cd ai_avatar

# Setup backend
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

### Step 2: Configure Environment

Create `backend/.env` file:

```env
# Database (REQUIRED)
DATABASE_URL=mysql+aiomysql://root:Password@localhost:3306/ai_interview

# Security
SECRET_KEY=your-secret-key-change-in-production

# AI Services (Get FREE API keys)
GOOGLE_API_KEY=your_google_api_key          # https://aistudio.google.com/
GROQ_API_KEY=your_groq_api_key              # https://console.groq.com/
OPENROUTER_API_KEY=your_openrouter_key      # https://openrouter.ai/ (optional)

# TTS & Transcription
TTS_PROVIDER=edge
TRANSCRIPTION_PROVIDER=whisper
HUGGINGFACE_API_KEY=your_hf_key             # https://huggingface.co/

# Server Config
HOST=0.0.0.0
PORT=8000
DEBUG=True
ALLOWED_ORIGINS=http://localhost:3000
UPLOAD_DIR=uploads
```

### Step 3: Setup Database

```bash
# Create MySQL database
mysql -u root -p
```

```sql
CREATE DATABASE ai_interview CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit;
```

```bash
# Run migrations
cd backend
venv\Scripts\python add_question_columns.py   # Add required columns
```

### Step 4: Create Upload Directories

```bash
cd backend
mkdir uploads uploads\resumes uploads\audio uploads\video
```

### Step 5: Setup Frontend

```bash
cd ../frontend
npm install
```

### Step 6: Start Everything

**Terminal 1 (Backend):**
```bash
cd backend
venv\Scripts\activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm start
```

### 🎉 Access the App
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

---

## 🎯 How It Works

### Interview Flow

```
1. ADMIN creates interview config
   ↓
   - Sets job role, description, difficulty
   - AI generates preset questions
   - Sets time limit (e.g., 10 minutes)
   - Gets shareable link

2. CANDIDATE opens interview link
   ↓
   - Enters name, email, uploads resume
   - Starts interview session

3. AI AVATAR asks questions
   ↓
   - Text-to-Speech (Edge TTS)
   - Avatar lip-sync animation
   - Timer starts after question

4. CANDIDATE answers
   ↓
   - Audio recorded (MediaRecorder API)
   - Live transcription displayed
   - Timer counts down

5. AI DECIDES next action
   ↓
   - "preset": Ask next main question
   - "follow_up": Probe deeper (max 1 per question)
   - "resume": Ask about candidate's resume
   - "complete": End interview

6. REPORT generated
   ↓
   - AI analyzes all Q&A pairs
   - Scores: Communication, Technical, Problem-Solving
   - Per-answer key points & improvements
   - Overall recommendation
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│  React 18 + TailwindCSS + WebRTC                            │
├─────────────────────────────────────────────────────────────┤
│  Pages:                                                      │
│  ├── PublicInterview.js  (Candidate interview UI)           │
│  ├── InterviewCreator.js (Admin creates interviews)         │
│  ├── ReportDetail.js     (View interview reports)           │
│  └── Dashboard.js        (Admin dashboard)                  │
├─────────────────────────────────────────────────────────────┤
│  Services:                                                   │
│  ├── publicInterviewService.js  (Interview API calls)       │
│  ├── aiService.js               (TTS & transcription)       │
│  └── avatarService.js           (Avatar control)            │
└─────────────────────────────────────────────────────────────┘
                              ↕ HTTP API
┌─────────────────────────────────────────────────────────────┐
│                        BACKEND                               │
│  FastAPI + SQLAlchemy + MySQL                               │
├─────────────────────────────────────────────────────────────┤
│  Routes:                                                     │
│  ├── public.py       (Interview session endpoints)          │
│  ├── interviews.py   (Interview config CRUD)                │
│  ├── candidates.py   (Candidate management)                 │
│  └── auth.py         (Authentication)                       │
├─────────────────────────────────────────────────────────────┤
│  Services:                                                   │
│  ├── ai_question_service.py  (AI decision: next question)   │
│  ├── report_service.py       (Generate interview reports)   │
│  ├── tts_service.py          (Text-to-Speech)               │
│  └── transcription_service.py (Speech-to-Text)              │
├─────────────────────────────────────────────────────────────┤
│  AI Providers (with fallback):                              │
│  ├── OpenRouter → Gemini → Groq  (Question decisions)       │
│  ├── Google STT → Whisper        (Transcription)            │
│  └── Edge TTS                    (Voice synthesis)          │
└─────────────────────────────────────────────────────────────┘
                              ↕ ORM
┌─────────────────────────────────────────────────────────────┐
│                        DATABASE                              │
│  MySQL 8.0                                                  │
├─────────────────────────────────────────────────────────────┤
│  Tables:                                                     │
│  ├── users              (Admin/Interviewer accounts)        │
│  ├── interview_configs  (Interview settings & questions)    │
│  ├── candidates         (Candidate info & resumes)          │
│  ├── interview_sessions (Active/completed sessions)         │
│  ├── responses          (Q&A with question_text, type)      │
│  └── reports            (AI-generated evaluations)          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔑 Key Features

### 🤖 Dynamic AI Interviewer
- Asks preset questions + intelligent follow-ups
- Time-aware decisions (respects interview duration)
- Resume-based questions (probes candidate's experience)
- Max 1 follow-up per preset question

### ⏱️ Smart Time Management
- Timer pauses during AI speech
- Dynamic question timing based on remaining time
- Time capping: Never assigns more time than available

### 📊 Intelligent Reports
- Per-question analysis with unique key points
- Color-coded question types:
  - 🔵 Blue: Preset questions
  - 🟣 Purple: Follow-up questions  
  - 🟢 Green: Resume questions
- Questions displayed in exact interview order

### 🎙️ Real-time Transcription
- Live transcript display during answer
- Browser Speech API with fallback to Google STT
- Transcript saved with each response

---

## 📁 Project Structure

```
ai_avatar/
├── backend/
│   ├── main.py                 # FastAPI entry point
│   ├── app/
│   │   ├── db.py               # Database connection
│   │   ├── orm_models.py       # SQLAlchemy models
│   │   └── repositories/       # Data access layer
│   ├── routes/
│   │   ├── public.py           # Public interview endpoints
│   │   ├── interviews.py       # Interview management
│   │   └── auth.py             # Authentication
│   ├── services/
│   │   ├── ai_question_service.py   # AI decision logic
│   │   ├── report_service.py        # Report generation
│   │   ├── tts_service.py           # Text-to-Speech
│   │   └── transcription_service.py # Speech-to-Text
│   ├── models/                 # Pydantic schemas
│   ├── uploads/                # File storage
│   └── .env                    # Environment variables
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── PublicInterview.js  # Interview UI
│   │   │   ├── ReportDetail.js     # Report display
│   │   │   └── InterviewCreator.js # Create interviews
│   │   ├── components/
│   │   │   └── ui/             # Reusable UI components
│   │   └── services/
│   │       ├── publicInterviewService.js
│   │       └── aiService.js
│   └── public/
│
├── database/
│   └── README.md               # Database documentation
│
└── README.md                   # This file
```

---

## 🔧 API Quick Reference

### Public Interview Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/public/interview/{id}` | Get interview config |
| POST | `/api/public/session/start` | Start interview session |
| POST | `/api/public/session/{id}/submit-response` | Submit answer & get next question |
| GET | `/api/public/session/{id}` | Get session status |

### Report Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/reports/session/{id}` | Get interview report |
| GET | `/api/reports/` | List all reports |

---

## 🛠️ Troubleshooting

### "Database connection failed"
```bash
# Check MySQL is running
mysql -u root -p -e "SELECT 1"

# Verify .env DATABASE_URL is correct
```

### "AI not responding"
```bash
# Check API keys in .env
# Verify GROQ_API_KEY and GOOGLE_API_KEY are valid
```

### "No audio recorded"
```
# Browser needs microphone permission
# Check browser console for errors
# Ensure HTTPS (or localhost) for MediaRecorder
```

### "Report shows same key points"
```bash
# Restart backend after recent changes
cd backend
venv\Scripts\python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 📝 Recent Changes

- ✅ Max 1 follow-up per preset question
- ✅ Time capping for all question types
- ✅ Follow-up/Resume question labels in reports
- ✅ Unique key points per answer
- ✅ Questions ordered by interview sequence
- ✅ Live transcription display

---

## 📄 License

MIT License - See LICENSE file for details.
