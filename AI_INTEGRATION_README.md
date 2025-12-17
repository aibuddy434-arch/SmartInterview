# AI Integration for AI Interview Avatar System

This document describes the AI integration features added to the AI Interview Avatar System, including transcription, text-to-speech, and avatar animation capabilities.

## 🚀 Features Added

### Backend AI Services

#### 1. Transcription Service (`/api/ai/transcribe`)
- **Route**: `POST /api/ai/transcribe`
- **Input**: `media_id` (file identifier)
- **Providers**:
  - **OpenAI Whisper API**: High-quality transcription with API key
  - **Local Whisper**: Offline transcription using local model
  - **HuggingFace**: Alternative models for transcription
- **Output**: Transcript text + word-level timestamps
- **Configuration**: Set via `TRANSCRIPTION_PROVIDER` environment variable

#### 2. Text-to-Speech Service (`/api/ai/tts`)
- **Route**: `POST /api/ai/tts`
- **Input**: `{ text, voice }`
- **Providers**:
  - **Coqui TTS**: High-quality, customizable voices
  - **HuggingFace TTS**: Alternative TTS models
- **Output**: Audio file (WAV format)
- **Configuration**: Set via `TTS_PROVIDER` environment variable

#### 3. AI Services Health Check (`/api/ai/health`)
- **Route**: `GET /api/ai/health`
- **Purpose**: Monitor transcription and TTS service status
- **Output**: Health status for each AI service

### Frontend AI Integration

#### 1. AI Service Client (`aiService.js`)
- Handles communication with backend AI endpoints
- Manages file uploads and audio generation
- Error handling and retry logic

#### 2. Avatar Service (`avatarService.js`)
- **Real-time Lip Sync**: Audio-driven mouth animation
- **Expression Control**: Happy, serious, thinking expressions
- **Web Audio API Integration**: Real-time frequency analysis
- **Fallback Animations**: Text-based animation when audio unavailable

#### 3. Enhanced Interview Session
- **WebRTC Integration**: Live video/audio streaming
- **Media Recording**: Video + audio capture per question
- **Avatar Interaction**: AI interviewer with animated responses
- **Real-time Feedback**: Recording indicators and progress tracking

## 🛠️ Installation & Setup

### Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**New Dependencies Added**:
- `openai-whisper==20231117` - Local Whisper transcription
- `TTS==0.22.0` - Coqui TTS for speech synthesis
- `transformers==4.36.0` - HuggingFace models
- `torch==2.1.0` - PyTorch for ML models
- `torchaudio==2.1.0` - Audio processing
- `librosa==0.10.1` - Audio analysis
- `soundfile==0.12.1` - Audio file handling
- `celery==5.3.4` - Background task processing
- `redis==5.0.1` - Task queue backend

### Environment Configuration

Create `.env` file in backend directory:

```env
# AI Services Configuration
TRANSCRIPTION_PROVIDER=whisper  # whisper, hf
OPENAI_API_KEY=your-openai-api-key-here
HUGGINGFACE_API_KEY=your-huggingface-api-key-here
TTS_PROVIDER=coqui  # coqui, hf

# Redis Configuration (for background tasks)
REDIS_URL=redis://localhost:6379
```

### Frontend Dependencies

```bash
cd frontend
npm install
```

**New Services**:
- `aiService.js` - AI API communication
- `avatarService.js` - Avatar animation management

## 🔧 Configuration Options

### Transcription Providers

#### OpenAI Whisper API
- **Pros**: High accuracy, fast processing
- **Cons**: Requires API key, costs per request
- **Setup**: Set `OPENAI_API_KEY` and `TRANSCRIPTION_PROVIDER=whisper`

#### Local Whisper
- **Pros**: Free, offline, no API limits
- **Cons**: Slower, requires more memory
- **Setup**: Set `TRANSCRIPTION_PROVIDER=whisper` without API key

#### HuggingFace
- **Pros**: Free, multiple model options
- **Cons**: Variable quality, slower processing
- **Setup**: Set `TRANSCRIPTION_PROVIDER=hf` and optionally `HUGGINGFACE_API_KEY`

### TTS Providers

#### Coqui TTS
- **Pros**: High quality, customizable voices, fast
- **Cons**: Larger model size
- **Setup**: Set `TTS_PROVIDER=coqui`

#### HuggingFace TTS
- **Pros**: Multiple model options, lightweight
- **Cons**: Variable quality
- **Setup**: Set `TTS_PROVIDER=hf`

## 📱 Usage Examples

### Starting an Interview Question

```javascript
import { aiService } from '../services/aiService';
import { avatarService } from '../services/avatarService';

const startQuestion = async (questionText) => {
  try {
    // Generate speech for the question
    const audioBlob = await aiService.generateSpeech(questionText);
    
    // Start avatar speaking with lip sync
    await avatarService.startSpeaking(audioBlob, questionText);
    
    // Play the audio
    const audio = new Audio(URL.createObjectURL(audioBlob));
    audio.play();
  } catch (error) {
    console.error('Failed to start question:', error);
  }
};
```

### Recording and Transcribing Answers

```javascript
const submitAnswer = async (mediaBlob) => {
  try {
    // Upload media file
    const formData = new FormData();
    formData.append('media', mediaBlob);
    formData.append('question_number', currentQuestion);
    
    // Submit to backend
    await api.post('/sessions/answer', formData);
    
    // Transcribe the audio
    const transcript = await aiService.transcribeAudio(mediaId);
    
    console.log('Transcript:', transcript.text);
  } catch (error) {
    console.error('Failed to submit answer:', error);
  }
};
```

### Avatar Expression Control

```javascript
// Set avatar expression
avatarService.setExpression('happy');    // Happy expression
avatarService.setExpression('serious');  // Serious expression
avatarService.setExpression('thinking'); // Thinking expression
avatarService.setExpression('neutral');  // Reset to neutral
```

## 🎨 Avatar Customization

### Visual Elements
- **Head**: Circular gradient background
- **Eyes**: Animated blinking with expression changes
- **Mouth**: Real-time lip sync with audio frequency
- **Expressions**: Multiple emotional states

### Animation Features
- **Lip Sync**: Audio-driven mouth movement
- **Blinking**: Natural eye blinking animation
- **Expression Transitions**: Smooth transitions between states
- **Fallback Animations**: Text-based animation when audio unavailable

### CSS Customization
Avatar styles are defined in `frontend/src/index.css` under `.avatar-interviewer` classes. You can customize:
- Colors and gradients
- Sizes and proportions
- Animation timing
- Expression appearances

## 🔍 Troubleshooting

### Common Issues

#### 1. Transcription Fails
- **Check**: Provider configuration in `.env`
- **Verify**: API keys are valid
- **Ensure**: Audio file format is supported (WAV, MP3, M4A)

#### 2. TTS Generation Fails
- **Check**: TTS provider configuration
- **Verify**: Model files are downloaded
- **Ensure**: Text input is not empty

#### 3. Avatar Not Animating
- **Check**: Web Audio API support in browser
- **Verify**: Avatar element is properly referenced
- **Ensure**: Audio context is initialized

#### 4. Media Recording Issues
- **Check**: Camera/microphone permissions
- **Verify**: Browser supports MediaRecorder API
- **Ensure**: HTTPS context for production

### Performance Optimization

#### Backend
- Use GPU acceleration for TTS models
- Implement caching for repeated transcriptions
- Use background tasks for long-running operations

#### Frontend
- Optimize avatar animation frame rate
- Implement audio streaming for large files
- Add loading states for AI operations

## 🚀 Future Enhancements

### Planned Features
1. **Advanced Avatar Models**: 3D models with realistic animations
2. **Emotion Recognition**: Analyze candidate emotions during interview
3. **Real-time Translation**: Multi-language interview support
4. **Voice Cloning**: Custom interviewer voices
5. **Advanced Analytics**: Interview performance insights

### Integration Possibilities
- **OpenAI GPT**: Dynamic question generation
- **Azure Cognitive Services**: Alternative AI services
- **Google Cloud Speech**: Additional transcription options
- **Amazon Polly**: Alternative TTS provider

## 📚 API Reference

### AI Endpoints

#### POST `/api/ai/transcribe`
Transcribe audio file to text.

**Request**:
```json
{
  "media_id": "file_identifier"
}
```

**Response**:
```json
{
  "success": true,
  "transcript": "Transcribed text here",
  "segments": [
    {
      "start": 0.0,
      "end": 2.5,
      "text": "First segment"
    }
  ],
  "language": "en",
  "provider": "whisper"
}
```

#### POST `/api/ai/tts`
Generate speech from text.

**Request**:
```json
{
  "text": "Text to convert to speech",
  "voice": "default"
}
```

**Response**: Audio file (WAV format)

#### GET `/api/ai/voices`
Get available TTS voices.

**Response**:
```json
{
  "provider": "coqui",
  "voices": ["voice1", "voice2", "voice3"]
}
```

#### GET `/api/ai/health`
Check AI services health.

**Response**:
```json
{
  "status": "healthy",
  "services": {
    "transcription": {
      "provider": "whisper",
      "status": "healthy"
    },
    "tts": {
      "provider": "coqui",
      "status": "healthy"
    }
  }
}
```

## 🤝 Contributing

To contribute to the AI integration:

1. **Fork** the repository
2. **Create** a feature branch
3. **Implement** your changes
4. **Test** thoroughly
5. **Submit** a pull request

### Development Guidelines
- Follow existing code style
- Add comprehensive error handling
- Include unit tests for new services
- Update documentation for new features
- Ensure backward compatibility

## 📄 License

This AI integration is part of the AI Interview Avatar System and follows the same license terms.

---

**Built with ❤️ using FastAPI, React, and modern AI technologies**


