import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { aiService } from '../services/aiService';
import { avatarService } from '../services/avatarService';
import { Video, Mic, Square, Play, Volume2 } from 'lucide-react';
import toast from 'react-hot-toast';

const InterviewSessionEnhanced = () => {
  const { sessionId } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [questions] = useState([
    "Tell me about your experience with React and modern JavaScript frameworks.",
    "How do you handle state management in large applications?",
    "Describe a challenging project you've worked on and how you overcame obstacles."
  ]);
  
  const videoRef = useRef(null);
  const avatarRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const streamRef = useRef(null);
  const recordingIntervalRef = useRef(null);

  useEffect(() => {
    initializeSession();
    return () => cleanup();
  }, []);

  const initializeSession = async () => {
    try {
      if (avatarRef.current) {
        avatarService.initialize(avatarRef.current);
      }
      await initializeMediaDevices();
    } catch (error) {
      console.error('Failed to initialize session:', error);
      toast.error('Failed to initialize interview session');
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
    } catch (error) {
      console.error('Failed to access media devices:', error);
      toast.error('Camera and microphone access required');
    }
  };

  const startQuestion = async () => {
    const question = questions[currentQuestion];
    
    try {
      avatarService.setExpression('serious');
      const audioBlob = await aiService.generateSpeech(question);
      await avatarService.startSpeaking(audioBlob, question);
      
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);
      audio.play();
      setIsPlaying(true);
      
      audio.onended = () => {
        setIsPlaying(false);
        avatarService.stopSpeaking();
        avatarService.setExpression('neutral');
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
        if (event.data.size > 0) chunks.push(event.data);
      };
      
      mediaRecorder.onstop = async () => {
        const blob = new Blob(chunks, { type: 'video/webm' });
        await submitAnswer(blob);
      };
      
      mediaRecorder.start();
      setIsRecording(true);
      setRecordingTime(0);
      
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
      console.log('Uploading answer:', {
        question: currentQuestion,
        duration: recordingTime,
        size: mediaBlob.size
      });
      
      setTimeout(() => {
        toast.success('Answer submitted successfully!');
        setCurrentQuestion(prev => prev + 1);
        setRecordingTime(0);
      }, 2000);
      
    } catch (error) {
      console.error('Failed to submit answer:', error);
      toast.error('Failed to submit answer');
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

  if (currentQuestion >= questions.length) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Interview Completed!</h1>
          <p className="text-gray-600 mb-6">Thank you for completing the interview.</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="btn-primary"
          >
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">AI Interview Session</h1>
              <p className="text-gray-600">Question {currentQuestion + 1} of {questions.length}</p>
            </div>
            <button
              onClick={() => navigate('/dashboard')}
              className="btn-secondary"
            >
              Exit Session
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column - Avatar and Question */}
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">AI Interviewer</h2>
              <div 
                ref={avatarRef}
                className="w-full h-64 bg-gradient-to-br from-blue-100 to-purple-100 rounded-lg flex items-center justify-center"
              />
              
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
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Current Question</h2>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-gray-800 text-lg">
                  {questions[currentQuestion]}
                </p>
              </div>
              
              <div className="mt-4 flex items-center justify-center">
                <button
                  onClick={startQuestion}
                  disabled={isPlaying}
                  className="btn-primary flex items-center space-x-2"
                >
                  <Volume2 className="h-4 w-4" />
                  <span>{isPlaying ? 'Playing...' : 'Ask Question'}</span>
                </button>
              </div>
            </div>
          </div>

          {/* Right Column - Video and Recording */}
          <div className="space-y-6">
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
                
                {isRecording && (
                  <div className="absolute top-4 right-4 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-medium">
                    REC {formatTime(recordingTime)}
                  </div>
                )}
              </div>
              
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

            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Progress</h2>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${(currentQuestion / questions.length) * 100}%` }}
                ></div>
              </div>
              <p className="text-sm text-gray-600 mt-2">
                {currentQuestion} of {questions.length} questions completed
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InterviewSessionEnhanced;


