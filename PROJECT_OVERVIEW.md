# 📋 AI Interview System - Complete Project Overview

This document provides a comprehensive understanding of how the AI Interview Avatar System works, from end to end.

---

## 🎯 System Purpose

This is an **AI-powered interview platform** where:
1. **Admins** create interview configurations with job-specific questions
2. **Candidates** take interviews via a shareable link
3. **AI Avatar** conducts the interview (asks questions, follows up intelligently)
4. **System** generates detailed evaluation reports

---

## 🔄 Complete Interview Flow

### Phase 1: Interview Creation (Admin)

```
Admin logs in → Dashboard → Create Interview
                    ↓
┌─────────────────────────────────────────────────┐
│           INTERVIEW CONFIGURATION               │
├─────────────────────────────────────────────────┤
│  Job Role:        "Machine Learning Engineer"  │
│  Job Description: "Looking for ML expertise..."│
│  Difficulty:      "Hard"                        │
│  Focus Areas:     ["ML", "Python", "CV"]       │
│  Time Limit:      10 minutes                    │
│  Avatar:          "Professional Male"           │
│  Number of Q's:   3                             │
└─────────────────────────────────────────────────┘
                    ↓
          AI generates questions
                    ↓
┌─────────────────────────────────────────────────┐
│            GENERATED QUESTIONS                  │
├─────────────────────────────────────────────────┤
│  Q1: "Explain supervised vs unsupervised ML"   │
│  Q2: "How do you handle overfitting?"          │
│  Q3: "Describe a CV project you worked on"     │
└─────────────────────────────────────────────────┘
                    ↓
     Admin gets shareable link:
     → http://localhost:3000/interview/{interview_id}
```

**Backend Code Flow:**
- `routes/interviews.py` → `POST /api/interviews/create`
- `services/ai_question_service.py` → AI generates questions
- `app/repositories/interview_repository.py` → Saves to database

---

### Phase 2: Candidate Registration

```
Candidate opens link → Registration form
                    ↓
┌─────────────────────────────────────────────────┐
│           CANDIDATE REGISTRATION                │
├─────────────────────────────────────────────────┤
│  Name:   "John Doe"                             │
│  Email:  "john@example.com"                     │
│  Phone:  "+1234567890"                          │
│  Resume: [Upload PDF]                           │
└─────────────────────────────────────────────────┘
                    ↓
         Resume text extracted
                    ↓
      Interview session created
```

**Backend Code Flow:**
- `routes/public.py` → `POST /api/public/session/start`
- Creates `Candidate` record in database
- Creates `InterviewSession` record with `start_time`
- Extracts resume text for AI context

---

### Phase 3: Interview Execution

This is the **core interview loop**:

```
┌─────────────────────────────────────────────────────────────┐
│                    INTERVIEW LOOP                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  1. AI ASKS QUESTION                                 │   │
│  │     ↓                                                │   │
│  │  • Get question text                                 │   │
│  │  • Generate speech (Edge TTS)                        │   │
│  │  • Play audio + animate avatar                       │   │
│  │  • Timer PAUSED during speech                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                    ↓                                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  2. CANDIDATE ANSWERS                                │   │
│  │     ↓                                                │   │
│  │  • Timer STARTS (dynamic time from AI)               │   │
│  │  • Record audio (MediaRecorder API)                  │   │
│  │  • Live transcription displayed                      │   │
│  │  • Candidate clicks "Submit" or timer ends           │   │
│  └─────────────────────────────────────────────────────┘   │
│                    ↓                                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  3. SUBMIT TO BACKEND                                │   │
│  │     ↓                                                │   │
│  │  FormData:                                           │   │
│  │  • question_number: 1                                │   │
│  │  • question_text: "What is ML?"                      │   │
│  │  • question_type: "preset" | "follow_up" | "resume"  │   │
│  │  • audio_file: [blob]                                │   │
│  │  • live_transcript: "My answer..."                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                    ↓                                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  4. BACKEND PROCESSING                               │   │
│  │     ↓                                                │   │
│  │  • Transcribe audio (Google STT / Whisper)           │   │
│  │  • Save Response to database                         │   │
│  │  • Call AI for next decision                         │   │
│  └─────────────────────────────────────────────────────┘   │
│                    ↓                                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  5. AI DECISION                                      │   │
│  │     ↓                                                │   │
│  │  LLM analyzes:                                       │   │
│  │  • All previous Q&A history                          │   │
│  │  • Candidate's resume                                │   │
│  │  • Time remaining                                    │   │
│  │  • Questions still to ask                            │   │
│  │                                                      │   │
│  │  Returns one of:                                     │   │
│  │  • "preset" + next_index + suggested_time            │   │
│  │  • "follow_up" + question_text + suggested_time      │   │
│  │  • "resume" + question_text + suggested_time         │   │
│  │  • "complete"                                        │   │
│  └─────────────────────────────────────────────────────┘   │
│                    ↓                                         │
│         If NOT "complete", loop back to step 1              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Backend Code Flow:**
- `routes/public.py` → `POST /api/public/session/{id}/submit-response`
- `services/transcription_service.py` → Transcribe audio
- `services/ai_question_service.py` → AI decides next action
  - `_build_llm_prompt()` → Creates context for LLM
  - `_process_llm_decision()` → Validates and caps time
- Database: Saves `Response` with `question_text`, `question_type`

---

### Phase 4: Report Generation

```
Interview completes → Generate Report
                    ↓
┌─────────────────────────────────────────────────────────────┐
│                   REPORT GENERATION                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Fetch all responses (ordered by created_at)             │
│                    ↓                                         │
│  2. Build Q&A pairs with:                                   │
│     • display_label: "Q1", "Q1 Follow-up 1", "Resume Q"     │
│     • question_type: "preset" | "follow_up" | "resume"      │
│     • question_text (actual question asked)                 │
│     • candidate_answer (transcript)                         │
│                    ↓                                         │
│  3. Send to AI (OpenRouter → Groq fallback)                 │
│                    ↓                                         │
│  4. AI analyzes and returns:                                │
│     • Scores (0-100): communication, technical, etc.        │
│     • Per-answer: quality, key_points, improvement          │
│     • Overall: strengths, weaknesses, recommendation        │
│                    ↓                                         │
│  5. Generate final report JSON                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Backend Code Flow:**
- `routes/reports.py` → `GET /api/reports/session/{id}`
- `services/report_service.py` → `generate_interview_report()`
  - `_analyze_with_ai()` → Sends Q&A to LLM
  - `_process_ai_analysis()` → Extracts scores and insights

---

## 🧠 AI Decision Logic (Detailed)

The AI uses this context to decide what to do next:

```python
# ai_question_service.py → _build_llm_prompt()

PROMPT = """
**Context:**
- Job Role: Machine Learning Engineer
- Job Description: {job_desc}
- Focus Areas: ML, Python, Computer Vision

**TIME STATUS (CRITICAL):**
- Elapsed: 4.5 min (270s)
- Remaining: 5.5 min (330s)
- Time Urgency: NORMAL

**Interview Progress:**
- Questions asked: 3
- Preset questions answered: 2 of 3
- Follow-up questions asked: 1
- Max follow-ups allowed: 1 per preset

**Candidate Resume:**
- ML Engineer at Company X
- Worked on hyperspectral imaging
- Python, TensorFlow, PyTorch

**Interview History:**
Q1: What is supervised learning?
A1: "Supervised learning uses labeled data..."

Q2: Can you give an example? (follow-up)
A2: "For example, cancer detection..."

**Current Answer:**
Q3: How do you handle overfitting?
A3: "I use cross-validation and early stopping..."

**Decision Rules:**
1. "preset" - Move to next main question
2. "follow_up" - Probe deeper (max 1 per preset)
3. "resume" - Ask about their experience
4. "complete" - End interview

What's next?
"""
```

**Decision Output:**
```json
{
  "action": "preset",
  "question_text": "Describe a computer vision project you worked on",
  "next_index": 3,
  "suggested_time_seconds": 120
}
```

---

## 💾 Database Schema

```
┌─────────────────────────────────────────────────────────────┐
│                      DATABASE SCHEMA                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────┐     ┌─────────────────┐                │
│  │     users       │     │  interview_     │                │
│  │─────────────────│     │   configs       │                │
│  │ id (UUID)       │←────│─────────────────│                │
│  │ email           │     │ id (UUID)       │                │
│  │ password_hash   │     │ job_role        │                │
│  │ full_name       │     │ job_description │                │
│  │ role            │     │ time_limit      │                │
│  └─────────────────┘     │ created_by ──┘  │                │
│                          │ shareable_link  │                │
│                          └────────┬────────┘                │
│                                   │                          │
│                                   │ 1:N                      │
│                                   ↓                          │
│  ┌─────────────────┐     ┌─────────────────┐                │
│  │   candidates    │     │    questions    │                │
│  │─────────────────│     │─────────────────│                │
│  │ id (UUID)       │     │ id (UUID)       │                │
│  │ name            │     │ text            │                │
│  │ email           │     │ tags (JSON)     │                │
│  │ resume_path     │     │ interview_      │                │
│  └────────┬────────┘     │   config_id     │                │
│           │              └─────────────────┘                │
│           │ 1:N                                              │
│           ↓                                                  │
│  ┌─────────────────────────────────────────┐                │
│  │         interview_sessions              │                │
│  │─────────────────────────────────────────│                │
│  │ id (UUID)                               │                │
│  │ session_id (UUID, unique)               │                │
│  │ candidate_id ────────────────────┘      │                │
│  │ interview_config_id                     │                │
│  │ start_time                              │                │
│  │ end_time                                │                │
│  │ status: pending | in_progress | done    │                │
│  │ current_question                        │                │
│  └────────────────────┬────────────────────┘                │
│                       │ 1:N                                  │
│                       ↓                                      │
│  ┌─────────────────────────────────────────┐                │
│  │              responses                   │                │
│  │─────────────────────────────────────────│                │
│  │ id (UUID)                               │                │
│  │ session_id                              │                │
│  │ question_number                         │                │
│  │ question_text ← ACTUAL QUESTION ASKED   │                │
│  │ question_type ← preset|follow_up|resume │                │
│  │ transcript                              │                │
│  │ audio_path                              │                │
│  │ created_at                              │                │
│  └─────────────────────────────────────────┘                │
│                                                              │
│  ┌─────────────────────────────────────────┐                │
│  │               reports                    │                │
│  │─────────────────────────────────────────│                │
│  │ id (UUID)                               │                │
│  │ session_id                              │                │
│  │ candidate_id                            │                │
│  │ overall_score                           │                │
│  │ breakdown (JSON)                        │                │
│  │ summary                                 │                │
│  │ recommendations                         │                │
│  └─────────────────────────────────────────┘                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔌 API Endpoint Details

### 1. Start Interview Session

```http
POST /api/public/session/start
Content-Type: multipart/form-data

name: "John Doe"
email: "john@example.com"
phone: "+1234567890"
resume: [file]
interview_id: "abc-123-def"
```

**Response:**
```json
{
  "success": true,
  "data": {
    "session_id": "session-uuid-here",
    "first_question": "Tell me about yourself...",
    "time_per_question": 120,
    "total_questions": 3
  }
}
```

### 2. Submit Response

```http
POST /api/public/session/{session_id}/submit-response
Content-Type: multipart/form-data

question_number: 1
question_text: "Tell me about yourself"
question_type: "preset"
audio_file: [blob]
live_transcript: "I am a software engineer..."
```

**Response:**
```json
{
  "success": true,
  "data": {
    "action": "follow_up",
    "question_text": "Can you elaborate on your ML experience?",
    "suggested_time_seconds": 90
  }
}
```

### 3. Get Report

```http
GET /api/reports/session/{session_id}
Authorization: Bearer {token}
```

**Response:**
```json
{
  "session_id": "...",
  "candidate": { "name": "John Doe", ... },
  "scores": {
    "communication": 75,
    "technical": 80,
    "problem_solving": 70
  },
  "responses": [
    {
      "display_label": "Q1",
      "question_type": "preset",
      "question_text": "What is ML?",
      "candidate_answer": "...",
      "key_points": ["Supervised learning", "Training data"],
      "answer_quality": "Good"
    },
    {
      "display_label": "Q1 Follow-up 1",
      "question_type": "follow_up",
      "question_text": "Can you give an example?",
      ...
    }
  ],
  "overall_assessment": {
    "recommendation": "Recommend",
    "strengths": [...],
    "areas_for_improvement": [...]
  }
}
```

---

## ⚙️ Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | ✅ | MySQL connection string |
| `SECRET_KEY` | ✅ | JWT signing key |
| `GOOGLE_API_KEY` | ✅ | For Gemini AI & Google STT |
| `GROQ_API_KEY` | ✅ | For Llama AI (primary) |
| `OPENROUTER_API_KEY` | ⚪ | Optional backup AI provider |
| `HUGGINGFACE_API_KEY` | ⚪ | For fallback transcription |
| `TTS_PROVIDER` | ⚪ | Default: `edge` |
| `TRANSCRIPTION_PROVIDER` | ⚪ | Default: `whisper` |
| `HOST` | ⚪ | Default: `0.0.0.0` |
| `PORT` | ⚪ | Default: `8000` |
| `DEBUG` | ⚪ | Default: `True` |
| `ALLOWED_ORIGINS` | ⚪ | CORS origins (comma-separated) |

---

## 🎨 Frontend Component Structure

```
PublicInterview.js (Main Interview Page)
├── State Management
│   ├── currentQuestionIndex    (which preset we're on)
│   ├── currentQuestionText     (actual question being asked)
│   ├── currentQuestionType     (Preset | Follow-up | From Resume)
│   ├── totalQuestionsAsked     (count for progress display)
│   ├── questionTimeRemaining   (countdown for current Q)
│   └── totalTimeRemaining      (overall interview time)
│
├── Audio/Video
│   ├── mediaRecorderRef        (records candidate audio)
│   ├── audioChunksRef          (stores audio chunks)
│   └── recognitionRef          (live speech recognition)
│
├── AI Avatar
│   ├── isSpeaking              (avatar talking state)
│   └── avatarService           (lip-sync control)
│
└── Core Functions
    ├── askQuestion(text, time)  → TTS + play audio + animate
    ├── startRecording()         → Begin audio capture
    ├── stopRecording()          → End capture, create blob
    └── submitResponse()         → Upload audio, get next Q
```

---

## 🔒 Security Features

1. **JWT Authentication**: All protected routes require valid token
2. **Role-based Access**: Admin, Interviewer, Candidate roles
3. **File Validation**: Resume files validated for type/size
4. **CORS Protection**: Only allowed origins can access API
5. **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries

---

## 📊 Performance Considerations

1. **AI Provider Fallback**: OpenRouter → Gemini → Groq ensures reliability
2. **Async Processing**: All I/O operations are async for scalability
3. **Time Capping**: Prevents questions from exceeding available time
4. **Follow-up Limits**: Max 1 follow-up per preset prevents endless loops

---

*Last Updated: December 2024*
