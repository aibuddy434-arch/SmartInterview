import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { aiService } from '../services/aiService';
import { avatarService } from '../services/avatarService';
import { 
  Video, 
  Mic, 
  MicOff, 
  Camera, 
  CameraOff, 
  Play, 
  Pause, 
  Square,
  Send,
  Volume2,
  Settings,
  AlertCircle
} from 'lucide-react';
import toast from 'react-hot-toast';

const InterviewSession = () => {
  const { sessionId } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  
  // State
  const [isLoading, setIsLoading] = useState(true);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [sessionData, setSessionData] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentAudio, setCurrentAudio] = useState(null);
  const [avatarExpression, setAvatarExpression] = useState('neutral');
  
  // Refs
  const videoRef = useRef(null);
  const audioRef = useRef(null);
  const avatarRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const recordingIntervalRef = useRef(null);
  
  // Mock questions for demonstration
  const mockQuestions = [
    "Tell me about your experience with React and modern JavaScript frameworks.",
    "How do you handle state management in large applications?",
    "Describe a challenging project you've worked on and how you overcame obstacles.",
    "What's your approach to testing and code quality?",
    "How do you stay updated with the latest technologies?"
  ];

  useEffect(() => {
    initializeSession();
    return () => cleanup();
  }, []);

  const initializeSession = async () => {
    try {
      setIsLoading(true);
      
      // Initialize avatar
      if (avatarRef.current) {
        avatarService.initialize(avatarRef.current);
      }
      
      // Set mock questions
      setQuestions(mockQuestions);
      
      // Initialize media devices
      await initializeMediaDevices();
      
      setIsLoading(false);
    } catch (error) {
      console.error('Failed to initialize session:', error);
      toast.error('Failed to initialize interview session');
      setIsLoading(false);
    }
  };

  const initializeMediaDevices = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true
      });
      
      streamRef.current = stream;
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      
      if (audioRef.current) {
        audioRef.current.srcObject = stream;
      }
    } catch (error) {
      console.error('Failed to access media devices:', error);
      toast.error('Camera and microphone access required for interview');
    }
  };

  const startQuestion = async () => {
    if (currentQuestion >= questions.length) {
      // Interview completed
      toast.success('Interview completed!');
      navigate('/dashboard');
      return;
    }

    const question = questions[currentQuestion];
    
    try {
      // Set avatar expression
      avatarService.setExpression('serious');
      
      // Generate speech for the question
      const audioBlob = await aiService.generateSpeech(question);
      setCurrentAudio(audioBlob);
      
      // Start avatar speaking
      await avatarService.startSpeaking(audioBlob, question);
      
      // Play audio
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      audio.play();
      setIsPlaying(true);
      
      audio.onended = () => {
        setIsPlaying(false);
        avatarService.stopSpeaking();
        setAvatarExpression('neutral');
      };
      
    } catch (error) {
      console.error('Failed to start question:', error);
      toast.error('Failed to generate question audio');
    }
  };

  const startRecording = () => {
    if (!streamRef.current) {
      toast.error('Media stream not available');
      return;
    }

    try {
      const mediaRecorder = new MediaRecorder(streamRef.current, {
        mimeType: 'video/webm;codecs=vp9,opus'
      });
      
      mediaRecorderRef.current = mediaRecorder;
      
      const chunks = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunks.push(event.data);
        }
      };
      
      mediaRecorder.onstop = async () => {
        const blob = new Blob(chunks, { type: 'video/webm' });
        await submitAnswer(blob);
      };
      
      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);
      
      // Start recording timer
      recordingIntervalRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
      
    } catch (error) {
      console.error('Failed to start recording:', error);
      toast.error('Failed to start recording');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
        recordingIntervalRef.current = null;
      }
    }
  };

  const submitAnswer = async (mediaBlob) => {
    try {
      setIsLoading(true);
      
      // Create FormData for upload
      const formData = new FormData();
      formData.append('media', mediaBlob, `answer_${currentQuestion}.webm`);
      formData.append('question_number', currentQuestion);
      formData.append('question_text', questions[currentQuestion]);
      
      // Upload to backend (mock for now)
      console.log('Uploading answer:', {
        question: currentQuestion,
        duration: recordingTime,
        size: mediaBlob.size
      });
      
      // Simulate transcription
      setTimeout(() => {
        toast.success('Answer submitted successfully!');
        setCurrentQuestion(prev => prev + 1);
        setRecordingTime(0);
        setIsLoading(false);
      }, 2000);
      
    } catch (error) {
      console.error('Failed to submit answer:', error);
      toast.error('Failed to submit answer');
      setIsLoading(false);
    }
  };

  const cleanup = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
    }
    
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
    }
    
    if (recordingIntervalRef.current) {
      clearInterval(recordingIntervalRef.current);
    }
    
    avatarService.destroy();
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-lg text-gray-600">Initializing interview session...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">AI Interview Session</h1>
              <p className="text-gray-600">Question {currentQuestion + 1} of {questions.length}</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm text-gray-500">Session ID</p>
                <p className="font-mono text-sm">{sessionId}</p>
              </div>
              <button
                onClick={() => navigate('/dashboard')}
                className="btn-secondary"
              >
                Exit Session
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column - Avatar and Question */}
          <div className="space-y-6">
            {/* AI Avatar */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">AI Interviewer</h2>
              <div 
                ref={avatarRef}
                className="w-full h-64 bg-gradient-to-br from-blue-100 to-purple-100 rounded-lg flex items-center justify-center"
              >
                {/* Avatar will be rendered here by avatarService */}
              </div>
              
              {/* Avatar Controls */}
              <div className="mt-4 flex items-center justify-center space-x-2">
                <button
                  onClick={() => avatarService.setExpression('happy')}
                  className="px-3 py-1 text-sm bg-green-100 text-green-700 rounded-md hover:bg-green-200"
                >
                  Happy
                </button>
                <button
                  onClick={() => avatarService.setExpression('serious')}
                  className="px-3 py-1 text-sm bg-red-100 text-red-700 rounded-md hover:bg-red-200"
                >
                  Serious
                </button>
                <button
                  onClick={() => avatarService.setExpression('thinking')}
                  className="px-3 py-1 text-sm bg-yellow-100 text-yellow-700 rounded-md hover:bg-yellow-200"
                >
                  Thinking
                </button>
              </div>
            </div>

            {/* Current Question */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Current Question</h2>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-gray-800 text-lg">
                  {questions[currentQuestion] || "Interview completed!"}
                </p>
              </div>
              
              {currentQuestion < questions.length && (
                <div className="mt-4 flex items-center justify-center space-x-4">
                  <button
                    onClick={startQuestion}
                    disabled={isPlaying}
                    className="btn-primary flex items-center space-x-2"
                  >
                    <Volume2 className="h-4 w-4" />
                    <span>{isPlaying ? 'Playing...' : 'Ask Question'}</span>
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Right Column - Video and Recording */}
          <div className="space-y-6">
            {/* Video Preview */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Your Video</h2>
              <div className="relative">
                <video
                  ref={videoRef}
                  autoPlay
                  muted
                  playsInline
                  className="w-full h-64 bg-gray-900 rounded-lg object-cover"
                />
                
                {/* Recording Overlay */}
                {isRecording && (
                  <div className="absolute top-4 right-4 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-medium">
                    REC {formatTime(recordingTime)}
                  </div>
                )}
              </div>
              
              {/* Recording Controls */}
              <div className="mt-4 flex items-center justify-center space-x-4">
                {!isRecording ? (
                  <button
                    onClick={startRecording}
                    className="btn-primary flex items-center space-x-2"
                  >
                    <Mic className="h-4 w-4" />
                    <span>Start Recording</span>
                  </button>
                ) : (
                  <button
                    onClick={stopRecording}
                    className="btn-danger flex items-center space-x-2"
                  >
                    <Square className="h-4 w-4" />
                    <span>Stop Recording</span>
                  </button>
                )}
              </div>
            </div>

            {/* Session Progress */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Progress</h2>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Questions Completed</span>
                  <span className="font-medium">{currentQuestion}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Questions Remaining</span>
                  <span className="font-medium">{Math.max(0, questions.length - currentQuestion)}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${(currentQuestion / questions.length) * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Instructions */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5" />
            <div>
              <h3 className="text-sm font-medium text-blue-900">Interview Instructions</h3>
              <ul className="mt-2 text-sm text-blue-700 space-y-1">
                <li>• Click "Ask Question" to hear the AI interviewer ask the question</li>
                <li>• Click "Start Recording" when you're ready to answer</li>
                <li>• Speak clearly and look at the camera while answering</li>
                <li>• Click "Stop Recording" when you're done</li>
                <li>• Your answer will be automatically transcribed and submitted</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InterviewSession;
