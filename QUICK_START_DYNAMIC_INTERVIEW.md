# Quick Start Guide for Dynamic AI Interviews

## Installation Steps

### 1. Install New Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This installs:
- `PyPDF2==3.0.1` - PDF parsing
- `python-docx==1.1.2` - DOCX parsing  
- `openai==1.12.0` - OpenAI API client

### 2. Verify OpenAI API Key

Ensure your `backend/app/config.py` has a valid OpenAI API key:

```python
openai_api_key: str = "sk-proj-..."  # Your actual key
```

Or set via environment variable:
```bash
export OPENAI_API_KEY="sk-proj-..."
```

### 3. Test the System

#### Option A: Quick Test (Manual)
1. Start backend: `cd backend && python main.py`
2. Start frontend: `cd frontend && npm start`
3. Create an interview as an admin
4. Access the shareable link
5. Register with a resume (upload a PDF/DOCX)
6. Answer questions and observe AI decisions in browser console

#### Option B: Check Backend Logs
```bash
cd backend
tail -f logs/app.log  # or wherever your logs are
```

Look for these key messages:
```
INFO: Audio file saved
INFO: Transcribing audio
INFO: Resume parsed: XXX characters
INFO: Calling AI service to determine next step...
INFO: AI decision: {'action': 'follow_up', ...}
```

## Testing Scenarios

### Test 1: Follow-up Question Generation
**Goal**: Make AI ask a follow-up question

**Steps**:
1. Answer first question with a short, vague response
   - Example: "I have some experience with Python."
2. Wait for AI decision
3. **Expected**: AI asks follow-up like "Can you elaborate on your Python experience?"

### Test 2: Resume-based Questions
**Goal**: Make AI reference resume content

**Steps**:
1. Upload a resume with specific skills (e.g., "TensorFlow", "React", "AWS")
2. Answer general questions
3. **Expected**: AI generates questions about resume skills
   - Example: "I see you have TensorFlow experience. Can you describe a project?"

### Test 3: Early Interview Completion
**Goal**: Make AI end interview before all preset questions

**Steps**:
1. Provide very detailed, comprehensive answers
2. Cover multiple topics thoroughly
3. **Expected**: AI may decide to complete interview after 3-4 questions instead of all 5-10

### Test 4: Fallback Mode (No OpenAI)
**Goal**: Verify system works without OpenAI

**Steps**:
1. Temporarily set invalid API key: `openai_api_key: str = "invalid"`
2. Start interview
3. **Expected**: System falls back to sequential preset questions
4. Check logs for: `WARNING: OpenAI client not initialized, using fallback logic`

## Verification Checklist

✅ **Backend**
- [ ] New dependencies installed (`pip list | grep -E "PyPDF2|python-docx|openai"`)
- [ ] OpenAI API key is configured
- [ ] Server starts without errors
- [ ] `/session/{id}/submit-response` endpoint works

✅ **Resume Parsing**
- [ ] Upload PDF resume → check logs for "Resume parsed: XXX characters"
- [ ] Upload DOCX resume → check logs for "Resume parsed: XXX characters"
- [ ] No resume → system continues normally

✅ **Transcription**
- [ ] Audio recorded → check logs for "Transcription completed: XXX characters"
- [ ] Transcript appears in response record

✅ **AI Decision**
- [ ] Check logs for "AI decision: {'action': ...}"
- [ ] Actions vary (not always 'preset')
- [ ] Generated questions make sense in context

✅ **Frontend**
- [ ] Dynamic questions are asked via TTS
- [ ] Progress bar updates correctly
- [ ] Interview completes properly
- [ ] No JavaScript errors in console

## Common Issues & Solutions

### Issue: "OpenAI client not initialized"
**Solution**: Check API key in config.py

### Issue: "Resume parsed: 0 characters" 
**Solution**: 
- Ensure resume file exists at the path
- Check file format (PDF/DOCX)
- Try different resume file

### Issue: "Transcription failed"
**Solution**:
- Check Whisper is installed: `pip list | grep whisper`
- Ensure audio file is valid WAV format
- Check audio file permissions

### Issue: Frontend doesn't play next question
**Solution**:
- Check browser console for errors
- Verify TTS service is working: `POST /tts` with test text
- Check avatar element is initialized

### Issue: Always returns "preset" action
**Solution**:
- Ensure OpenAI API key is valid and has credits
- Check backend logs for OpenAI API errors
- Try with detailed candidate responses

## Expected Behavior

### Normal Interview Flow

```
┌─────────────────────────────────────────────────┐
│ Question 1 (Preset): "Tell me about yourself"  │
│ Candidate: "I'm a developer with 5 years..."    │
│ AI Decision: follow_up                           │
└─────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────┐
│ Question 2 (Follow-up): "What technologies?"    │
│ Candidate: "React, Node.js, Python..."          │
│ AI Decision: resume                              │
└─────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────┐
│ Question 3 (Resume): "I see AWS on your resume" │
│ Candidate: "Yes, I've worked with EC2, S3..."   │
│ AI Decision: preset                              │
└─────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────┐
│ Question 4 (Preset): "How do you debug?"        │
│ Candidate: "I use Chrome DevTools, logging..."  │
│ AI Decision: complete                            │
└─────────────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────────────┐
│          Interview Completed! 🎉                 │
└─────────────────────────────────────────────────┘
```

### Performance Metrics

**Expected Timings**:
- Audio save: <0.5s
- Transcription: 2-5s
- Resume parsing: <1s
- AI decision: 1-3s
- **Total per response**: ~3-8 seconds

## Monitoring Commands

### Check Backend Logs (Real-time)
```bash
cd backend
tail -f logs/app.log | grep -E "AI decision|Transcription|Resume parsed"
```

### Check OpenAI API Usage
Visit: https://platform.openai.com/usage

### Check File Uploads
```bash
ls -lh backend/uploads/audio/
ls -lh backend/uploads/resumes/
```

### Check Database Records
```sql
-- Check response records
SELECT id, session_id, question_number, LENGTH(transcript) as transcript_length 
FROM responses 
ORDER BY created_at DESC 
LIMIT 10;

-- Check session status
SELECT session_id, status, current_question, start_time, end_time 
FROM interview_sessions 
ORDER BY created_at DESC 
LIMIT 10;
```

## Need Help?

1. **Check Logs**: `backend/logs/app.log`
2. **Browser Console**: Press F12 in browser
3. **API Testing**: Use tools like Postman to test endpoints directly
4. **Documentation**: See `DYNAMIC_INTERVIEW_IMPLEMENTATION.md` for detailed architecture

## Success Indicators

✅ You'll know it's working when:
1. Backend logs show "AI decision: {action: 'follow_up', ...}"
2. Questions asked are different from preset list
3. AI references candidate's previous answers
4. AI mentions resume content in questions
5. Interview length varies based on candidate responses

---

**Ready to test?** Start your servers and begin an interview! 🚀


