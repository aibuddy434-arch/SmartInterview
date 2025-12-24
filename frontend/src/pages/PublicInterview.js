import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardHeader, CardBody } from '../components/ui/Card';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import toast from 'react-hot-toast';
import { publicInterviewService } from '../services/publicInterviewService';
import { avatarService } from '../services/avatarService';
import { aiService } from '../services/aiService';
import {
  Mic,
  MicOff,
  CheckCircle,
  Clock,
  AlertCircle,
  Upload,
  FileText,
  Camera
} from 'lucide-react';

const PublicInterview = () => {
  const { interviewId } = useParams();
  const navigate = useNavigate();

  // --- State Management ---
  const [step, setStep] = useState('loading');
  const [interview, setInterview] = useState(null);
  const [candidate, setCandidate] = useState({ name: '', email: '', phone: '', resume: null });
  const [sessionId, setSessionId] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0); // Tracks preset Q's
  const [currentQuestionText, setCurrentQuestionText] = useState('');

  // --- FIX 2: Add new state for "creative" progress ---
  const [totalQuestionsAsked, setTotalQuestionsAsked] = useState(0);
  const [currentQuestionType, setCurrentQuestionType] = useState('Preset');
  // --- End Fix 2 ---

  // --- Timer State ---
  const [questionTimeRemaining, setQuestionTimeRemaining] = useState(null); // Seconds remaining for current question
  const [totalTimeRemaining, setTotalTimeRemaining] = useState(null); // Total interview time remaining in seconds
  const [timePerQuestion, setTimePerQuestion] = useState(null); // Seconds per question from config
  const [interviewStartTime, setInterviewStartTime] = useState(null); // When interview started
  const [isTimerActive, setIsTimerActive] = useState(false); // Whether timer is counting down
  const [isTimerPaused, setIsTimerPaused] = useState(true); // Timer paused during TTS/prep
  const [isSpeaking, setIsSpeaking] = useState(false); // Is avatar currently speaking?
  const [nextQuestionTime, setNextQuestionTime] = useState(null); // Dynamic time for next question from AI
  // --- End Timer State ---

  const [isRecording, setIsRecording] = useState(false);
  const [audioResponse, setAudioResponse] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [avatarElement, setAvatarElement] = useState(null);
  const [mediaStream, setMediaStream] = useState(null);
  const [permissions, setPermissions] = useState({ microphone: false, camera: false, screen: false });
  const [permissionError, setPermissionError] = useState(null);
  const [requestingPermissions, setRequestingPermissions] = useState(false);

  // --- Live Transcript State ---
  const [liveTranscript, setLiveTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const speechRecognitionRef = useRef(null);
  // --- End Live Transcript State ---

  // --- Refs ---
  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const questionTimerRef = useRef(null); // Interval ref for question timer
  const totalTimerRef = useRef(null); // Interval ref for total timer
  const autoSubmitTriggeredRef = useRef(false); // Prevent double auto-submit
  const startRecordingRef = useRef(null); // Ref for auto-start recording
  const startQuestionTimerRef = useRef(null); // Ref for starting timer after TTS
  const hasAskedFirstQuestionRef = useRef(false); // Prevent Q1 double-ask

  // --- Core Functions (wrapped in useCallback) ---

  const askQuestion = useCallback(async (questionText, dynamicTimeOverride = null) => {
    // NOTE: Avatar element is optional - TTS works without it
    if (!questionText || questionText.trim() === '') {
      console.warn('Empty question text provided.');
      return;
    }

    console.log("[ASK] Starting to ask question:", questionText.substring(0, 50) + "...");

    // PAUSE timer while speaking
    setIsSpeaking(true);
    setIsTimerPaused(true);

    try {
      console.log("[ASK] Calling TTS service...");
      const audioBlob = await aiService.generateTTS(questionText);
      if (!audioBlob) {
        console.error('[ASK] TTS returned null blob');
        toast.error('Could not generate speech audio.');
        setIsSpeaking(false);
        return;
      }
      console.log("[ASK] TTS blob received, size:", audioBlob.size);
      const audioUrl = URL.createObjectURL(audioBlob);
      const audio = new Audio(audioUrl);

      audio.onended = () => {
        URL.revokeObjectURL(audioUrl);
        console.log("[ASK] Avatar finished speaking. Prep time starting...");
        setIsSpeaking(false);

        // Show prep time toast with dynamic time info
        const timeToUse = dynamicTimeOverride || nextQuestionTime || timePerQuestion || 120;
        toast(`💡 Prepare your answer... (${Math.floor(timeToUse / 60)}:${(timeToUse % 60).toString().padStart(2, '0')})`, {
          icon: '⏱️',
          duration: 2000,
          style: { background: '#FFF3CD', color: '#856404' }
        });

        // After 2 sec prep time: start timer and recording
        setTimeout(() => {
          console.log(`[ASK] Prep time over. Starting timer with ${timeToUse}s and recording!`);

          // RESUME timer
          setIsTimerPaused(false);

          // Start the question timer NOW with dynamic time
          if (startQuestionTimerRef.current) {
            console.log(`[TIMER] Starting question timer now with ${timeToUse} seconds`);
            startQuestionTimerRef.current(timeToUse);
          }

          // Auto-start recording
          if (startRecordingRef.current && !isRecording) {
            console.log("[AUTO-RECORD] Starting recording automatically");
            startRecordingRef.current();
            toast("🎤 Recording started! Answer now...", {
              icon: '🎙️',
              duration: 2000,
              style: { background: '#E8F5E9', color: '#2E7D32' }
            });
          }
        }, 2000); // 2 second prep time after question is spoken
      };

      audio.onerror = (e) => {
        console.error('Audio playback error:', e);
        toast.error('An error occurred during audio playback.');
        URL.revokeObjectURL(audioUrl);
        setIsSpeaking(false);
        setIsTimerPaused(false);
      };

      await audio.play();
      console.log("[ASK] Audio playing now.");

    } catch (error) {
      console.error('Failed to ask question:', error);
      const errorMessage = error?.message || error?.toString() || 'Unknown error';
      toast.error(`TTS Error: ${errorMessage.substring(0, 100)}`);
      setIsSpeaking(false);
      setIsTimerPaused(false);
    }
  }, [isRecording, nextQuestionTime, timePerQuestion]);

  const completeInterview = useCallback(async (reason = 'normal') => {
    if (!sessionId) return;

    // Stop all timers
    if (questionTimerRef.current) {
      clearInterval(questionTimerRef.current);
      questionTimerRef.current = null;
    }
    if (totalTimerRef.current) {
      clearInterval(totalTimerRef.current);
      totalTimerRef.current = null;
    }
    setIsTimerActive(false);

    // Stop recording if active
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }

    setSubmitting(true);
    try {
      const result = await publicInterviewService.completeSession(sessionId);
      if (result && result.success) {
        setStep('complete');
        if (reason === 'timeout') {
          toast.success('Interview time limit reached. Interview completed!');
        } else {
          toast.success('Interview completed successfully!');
        }
      } else {
        toast.error(result?.error || 'Failed to complete the interview session.');
      }
    } catch (error) {
      console.error("Complete interview error:", error);
      toast.error(error?.response?.data?.detail || 'Failed to complete the interview.');
    } finally {
      setSubmitting(false);
    }
  }, [sessionId]);

  // --- Timer Helper Functions ---
  const formatTime = useCallback((seconds) => {
    if (seconds === null || seconds === undefined) return '--:--';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }, []);

  // Updated to accept optional customTime for dynamic AI-determined timing
  const startQuestionTimer = useCallback((customTime = null) => {
    const timeToUse = customTime || timePerQuestion;
    if (!timeToUse) return;

    // Clear existing timer
    if (questionTimerRef.current) {
      clearInterval(questionTimerRef.current);
    }

    console.log(`[TIMER] Starting question timer with ${timeToUse} seconds`);
    setQuestionTimeRemaining(timeToUse);
    autoSubmitTriggeredRef.current = false;

    questionTimerRef.current = setInterval(() => {
      setQuestionTimeRemaining(prev => {
        if (prev <= 1) {
          // Time's up for this question
          clearInterval(questionTimerRef.current);
          questionTimerRef.current = null;
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  }, [timePerQuestion]);

  // Updated to accept optional customTime parameter
  const resetQuestionTimer = useCallback((customTime = null) => {
    if (questionTimerRef.current) {
      clearInterval(questionTimerRef.current);
      questionTimerRef.current = null;
    }
    const timeToSet = customTime || timePerQuestion;
    if (timeToSet) {
      setQuestionTimeRemaining(timeToSet);
    }
  }, [timePerQuestion]);

  // Ref to hold latest submitResponse for auto-submit
  const submitResponseRef = useRef(null);

  // Auto-submit when question timer reaches 0
  const autoSubmitResponse = useCallback(async () => {
    if (autoSubmitTriggeredRef.current) return; // Prevent double trigger
    autoSubmitTriggeredRef.current = true;

    console.log("[autoSubmitResponse] Question timer expired, auto-submitting...");
    toast("Time's up! Submitting your response...", {
      icon: '⏰',
      style: { background: '#FEF3CD', color: '#856404' }
    });

    // Stop recording if active
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      // Wait a moment for the recording to finalize
      await new Promise(resolve => setTimeout(resolve, 800));
    }

    // Now we need to trigger submit
    // Use a timeout to allow state to update
    setTimeout(() => {
      if (submitResponseRef.current) {
        submitResponseRef.current(true); // true = isAutoSubmit
      }
    }, 200);
  }, []);
  // --- End Timer Helper Functions ---


  // --- FIX 2: Update submitResponse for new progress logic ---
  // --- FIX 3: Corrected submitResponse function ---
  const submitResponse = useCallback(async (isAutoSubmit = false) => {
    // For auto-submit, use empty blob if no audio
    let audioToSubmit = audioResponse;
    if (!audioToSubmit && isAutoSubmit) {
      console.log("[submitResponse] Auto-submit with no audio, creating empty blob");
      audioToSubmit = new Blob([new ArrayBuffer(44)], { type: 'audio/wav' }); // Minimal WAV header
    }

    if (!audioToSubmit) {
      toast.error("No audio recorded to submit.");
      return;
    }
    if (!sessionId) {
      toast.error("Session ID is missing.");
      return;
    }
    setSubmitting(true);

    try {
      const formData = new FormData();
      formData.append('question_number', currentQuestionIndex + 1);
      formData.append('audio_file', audioToSubmit, 'response.wav');

      // NEW: Send question metadata for proper report labeling
      if (currentQuestionText) {
        formData.append('question_text', currentQuestionText);
      }
      // Map frontend display types to backend format
      let qType = 'preset';
      if (currentQuestionType === 'Follow-up') {
        qType = 'follow_up';
      } else if (currentQuestionType === 'From Resume') {
        qType = 'resume';
      }
      formData.append('question_type', qType);

      // Send live transcript as fallback for transcription failures
      const fullTranscript = liveTranscript + (interimTranscript ? ' ' + interimTranscript : '');
      if (fullTranscript && fullTranscript.trim().length > 0) {
        formData.append('live_transcript', fullTranscript.trim());
        console.log(`[submitResponse] Including live transcript: ${fullTranscript.length} chars`);
      }

      console.log(`[submitResponse] Submitting response for question ${currentQuestionIndex + 1}, type: ${qType}...`);

      const result = await publicInterviewService.submitResponse(sessionId, formData);
      console.log("[submitResponse] Backend response received:", result);

      if (result && result.success === true && result.data) {
        toast.success("Response submitted!");
        setAudioResponse(null); // Clear previous audio blob

        const { action, question_text, next_index, suggested_time_seconds } = result.data;

        // Use AI-suggested time if available, otherwise default to 120 seconds
        const dynamicTime = suggested_time_seconds || 120;
        console.log(`[submitResponse] AI Decision - Action: ${action}, Next Index: ${next_index}, Time: ${dynamicTime}s`);

        // --- THIS IS THE FIX ---
        // The counter increment was moved from here...

        if (action === "complete") {
          console.log("[submitResponse] Interview completed by AI decision.");
          setStep('complete');
          toast.success('Interview completed!');

        } else if (action === "preset") {
          const newIndex = next_index - 1;
          console.log(`[submitResponse] Moving to preset question at index ${newIndex} (1-based: ${next_index}, time: ${dynamicTime}s)`);

          setTotalQuestionsAsked(prev => prev + 1); // <-- ...to inside here
          setCurrentQuestionIndex(newIndex);
          setCurrentQuestionText(question_text);
          setCurrentQuestionType('Preset');
          setNextQuestionTime(dynamicTime); // Store dynamic time for this question

          // Timer will start after TTS finishes in askQuestion() - don't start here
          resetQuestionTimer(dynamicTime); // Just reset the display with dynamic time

          // Ask next question immediately
          setTimeout(() => {
            if (question_text) {
              askQuestion(question_text, dynamicTime);
            }
          }, 200); // Minimal delay for instant questions


        } else if (action === "follow_up" || action === "resume") {
          console.log(`[submitResponse] Asking ${action} question: ${question_text} (time: ${dynamicTime}s)`);

          setTotalQuestionsAsked(prev => prev + 1); // <-- ...and inside here
          setCurrentQuestionText(question_text);
          setCurrentQuestionType(action === 'follow_up' ? 'Follow-up' : 'From Resume');
          setNextQuestionTime(dynamicTime); // Store dynamic time for follow-up

          // Timer will start after TTS finishes in askQuestion() - don't start here
          resetQuestionTimer(dynamicTime); // Just reset the display with dynamic time

          // Ask follow-up question immediately
          setTimeout(() => {
            if (question_text) {
              askQuestion(question_text, dynamicTime);
            }
          }, 200); // Minimal delay for instant questions

        } else {
          console.warn(`[submitResponse] Unknown action: ${action}`);
          toast.error("Unexpected response from server. Please try again.");
        }

      } else {
        console.error("[submitResponse] API call failed structure:", result);
        toast.error(result?.error || result?.message || "Failed to submit response.");
      }
    } catch (error) {
      console.error("[submitResponse] CRITICAL Error during API call:", error);
      toast.error(error?.response?.data?.detail || "Failed to submit response due to a network error.");
    } finally {
      setSubmitting(false);
    }
  }, [audioResponse, sessionId, currentQuestionIndex, liveTranscript, interimTranscript, askQuestion, setCurrentQuestionText, setCurrentQuestionType, setTotalQuestionsAsked, resetQuestionTimer]);

  // Keep ref updated with latest submitResponse for auto-submit
  useEffect(() => {
    submitResponseRef.current = submitResponse;
  }, [submitResponse]);


  const startInterview = useCallback(async () => {
    if (!sessionId) {
      toast.error("Session not initialized. Cannot start interview.");
      return;
    }

    setSubmitting(true);
    console.log("[startInterview] Clicked. Playing silent audio to unlock browser audio...");

    // IMPORTANT: This silent audio unlocks the browser's audio context
    try {
      const silentAudio = new Audio("data:audio/mp3;base64,SUQzBAAAAAABEVRYWFgAAAAtAAADY29tbWVudABCaWdTb3VuZEJhbmsuY29tIC8gTGFTb25vVGhlcXVlLm9yZwBURU5DAAAAHQAAA1N3aXRjaCBvZiB0aGUgUm9ja3VziciATTdXAAALEwAAGoGnP3sBCAADxI/e/wYGBgYHBwcHCAgICAkKCgwMDQ4ODxEREhMUFRYXGBkaGxwdHh8gISIjJCUmJygpKissLS4vMDEyMzQ1Njc4OTo7PD0+P0BBQkNERUZHSElKS0xNTk9QUVJTVFVWV1hZWltcXV5fYGFiY2RlZmdoaWprbG1ucHFyc3R1dnd4eXp7fH1+f4CBgoOEhYaHiImKi4yNjo+QkZKTlJWWl5iZmpucnZ6foKGio6SlpqeoqaqrrK2ur7CxsrO0tba3uLm6u7y9vr/AwcLDxMXGx8jJysvMzc7P0NHS09TV1tfY2drb3N3e3+Dh4uPk5ebn6Onq6+zt7u/w8fLz9PX29/j5+vv8/f7/AABm3GvrFVAFwAAB9wz/DBAA");
      await silentAudio.play();
      console.log("[startInterview] Audio context unlocked.");
    } catch (e) {
      console.warn("[startInterview] Silent audio playback failed (this is okay):", e);
    }

    try {
      console.log("[startInterview] Calling startSession API...");
      const result = await publicInterviewService.startSession(sessionId);

      if (result && result.success === true) {
        console.log("[startInterview] API SUCCESS. Setting step to interview...");
        setStep('interview');
        toast.success('Interview starting! First question coming...');

        // DIRECTLY ASK FIRST QUESTION HERE - Don't rely on useEffect
        if (interview?.questions?.length > 0) {
          const firstQuestion = interview.questions[0];
          const firstQuestionText = firstQuestion.text;
          const firstQuestionTime = firstQuestion.suggested_time_seconds || 120;

          console.log(`[startInterview] Asking first question directly: "${firstQuestionText.substring(0, 50)}..."`);
          setCurrentQuestionText(firstQuestionText);
          setTotalQuestionsAsked(1);
          setCurrentQuestionType('Preset');
          setNextQuestionTime(firstQuestionTime);
          hasAskedFirstQuestionRef.current = true; // Mark as asked

          // Call askQuestion immediately - minimal delay
          setTimeout(() => {
            askQuestion(firstQuestionText, firstQuestionTime);
          }, 100); // Reduced from 500ms to 100ms for faster start
        }
      } else {
        console.error("[startInterview] startSession API failed:", result?.error);
        toast.error(result?.error || 'Failed to start the interview session.');
      }
    } catch (err) {
      console.error("[startInterview] CRITICAL Error during startSession API call:", err);
      toast.error(err?.response?.data?.detail || err?.message || 'Failed to start interview.');
    } finally {
      setSubmitting(false);
    }
  }, [sessionId, interview, askQuestion, setCurrentQuestionText, setCurrentQuestionType, setTotalQuestionsAsked, setNextQuestionTime]);

  const loadInterview = useCallback(async () => {
    if (!interviewId) return;
    setLoading(true);
    try {
      const data = await publicInterviewService.getPublicInterview(interviewId);
      setInterview(data);
      setStep('register');
    } catch (error) {
      console.error("Load Interview Error:", error);
      toast.error(error?.response?.data?.detail || 'Failed to load interview. Check the link or network.');
      setStep('error');
    } finally {
      setLoading(false);
    }
  }, [interviewId]);

  const handleCandidateRegistration = useCallback(async (e) => {
    e.preventDefault();
    if (!interviewId) return;
    setSubmitting(true);
    try {
      const formData = new FormData();
      formData.append('name', candidate.name);
      formData.append('email', candidate.email);
      formData.append('phone', candidate.phone);
      if (candidate.resume) {
        formData.append('resume_file', candidate.resume);
      }
      const result = await publicInterviewService.registerCandidate(interviewId, formData);
      if (result && result.success && result.data?.session_id) {
        setSessionId(result.data.session_id); // Corrected typo here
        setCandidate(prev => ({ ...prev, id: result.data.candidate?.id }));
        toast.success('Registration successful! Please grant permissions.');
        setStep('permissions');
      } else {
        toast.error(result?.error || 'Registration failed.');
      }
    } catch (err) {
      console.error("Registration Error:", err);
      toast.error(err?.response?.data?.detail || 'An unexpected error occurred during registration.');
    } finally {
      setSubmitting(false);
    }
  }, [candidate, interviewId]);

  const requestAllPermissions = useCallback(async () => {
    setRequestingPermissions(true);
    setPermissionError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      setMediaStream(stream);
      setPermissions({ microphone: true, camera: true, screen: false });
      return true; // Indicate success
    } catch (error) {
      console.error('Media permission denied:', error);
      setPermissionError(error.message || "Camera and Microphone access denied.");
      setPermissions({ microphone: false, camera: false, screen: false });
      return false; // Indicate failure
    } finally {
      setRequestingPermissions(false);
    }
  }, []);

  const handlePermissionRequest = useCallback(async () => {
    const success = await requestAllPermissions();
    if (success) {
      setStep('ready');
      toast.success('Camera and Microphone permissions granted!');
    } else {
      toast.error('Camera and Microphone access are required to proceed.');
    }
  }, [requestAllPermissions]);

  const startRecording = useCallback(() => {
    if (!mediaStream) return toast.error('Microphone not available.');
    try {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
        mediaRecorderRef.current.stop();
      }
      mediaRecorderRef.current = new MediaRecorder(mediaStream);
      audioChunksRef.current = [];
      setAudioResponse(null);

      // Reset live transcript for new recording
      setLiveTranscript('');
      setInterimTranscript('');

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) audioChunksRef.current.push(event.data);
      };
      mediaRecorderRef.current.onstop = () => {
        // Use the actual MIME type from MediaRecorder
        const mimeType = mediaRecorderRef.current.mimeType || 'audio/webm';
        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType });
        setAudioResponse(audioBlob);
        console.log('Recording stopped, audio blob ready. MIME type:', mimeType);
      };
      mediaRecorderRef.current.onerror = (event) => {
        console.error('MediaRecorder error:', event.error);
        toast.error('An error occurred during recording.');
        setIsRecording(false);
      }
      mediaRecorderRef.current.start();
      setIsRecording(true);

      // --- Start Speech Recognition for Live Transcript ---
      try {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
          const recognition = new SpeechRecognition();
          recognition.continuous = true;
          recognition.interimResults = true;
          recognition.lang = 'en-US';

          recognition.onresult = (event) => {
            let interim = '';
            let final = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
              const transcript = event.results[i][0].transcript;
              if (event.results[i].isFinal) {
                final += transcript + ' ';
              } else {
                interim += transcript;
              }
            }

            if (final) {
              setLiveTranscript(prev => prev + final);
            }
            setInterimTranscript(interim);
          };

          recognition.onerror = (event) => {
            console.warn('Speech recognition error:', event.error);
            // Don't show error toast - continue without live transcript
          };

          recognition.onend = () => {
            // Restart if still recording
            if (isRecording && speechRecognitionRef.current) {
              try {
                speechRecognitionRef.current.start();
              } catch (e) {
                // Already started or stopped
              }
            }
          };

          speechRecognitionRef.current = recognition;
          recognition.start();
          console.log('[Speech Recognition] Started for live transcript');
        } else {
          console.warn('Web Speech API not supported in this browser');
        }
      } catch (speechError) {
        console.warn('Failed to start speech recognition:', speechError);
        // Continue without live transcript
      }
      // --- End Speech Recognition ---

    } catch (error) {
      console.error('Failed to start recording:', error);
      toast.error('Failed to start recording.');
      setIsRecording(false);
    }
  }, [mediaStream, isRecording]);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }

    // Stop speech recognition
    if (speechRecognitionRef.current) {
      try {
        speechRecognitionRef.current.stop();
        speechRecognitionRef.current = null;
        console.log('[Speech Recognition] Stopped');
      } catch (e) {
        // Already stopped
      }
    }
    // Clear interim transcript (keep final transcript)
    setInterimTranscript('');
  }, [isRecording]);

  // Keep startRecordingRef updated for auto-start recording
  useEffect(() => {
    startRecordingRef.current = startRecording;
  }, [startRecording]);

  // Keep startQuestionTimerRef updated for timer start after TTS
  useEffect(() => {
    startQuestionTimerRef.current = startQuestionTimer;
  }, [startQuestionTimer]);

  const handleResumeChange = (e) => {
    const file = e.target.files[0];
    if (file && (file.type === 'application/pdf' || file.type.includes('word'))) {
      setCandidate(prev => ({ ...prev, resume: file }));
    } else if (file) {
      toast.error('Please upload a PDF or Word document.');
    }
  };

  const initializeAvatar = useCallback(() => {
    if (avatarElement) return;
    const avatar = avatarService.createAvatarVisuals();
    if (avatar instanceof HTMLElement) {
      setAvatarElement(avatar);
      console.log("Avatar element created and stored in state.");
    } else {
      console.error("avatarService.createAvatarVisuals() did not return a valid HTML element.");
      toast.error("Failed to create avatar visuals.");
    }
  }, [avatarElement]);

  // --- useEffect Hooks ---

  // --- FIX 1: Make video stream attachment robust ---
  // This effect handles attaching the video stream
  useEffect(() => {
    // It runs when 'step' changes. If we just entered the 'interview' step,
    // and the stream exists, and the video element is rendered...
    if (step === 'interview' && mediaStream && videoRef.current) {
      console.log("Attaching media stream to video element.");
      videoRef.current.srcObject = mediaStream;
    }
    // We only need to run this when 'step' or 'mediaStream' changes.
  }, [step, mediaStream]);
  // --- End Fix 1 ---

  // --- FIX 2: Update "First Question" useEffect ---
  useEffect(() => {
    console.log(`[Q1 Effect Check] Step: ${step}, Avatar Ready: ${!!avatarElement}, Interview Ready: ${!!interview}, QIndex: ${currentQuestionIndex}, AlreadyAsked: ${hasAskedFirstQuestionRef.current}`);

    // Check if we've already asked Q1 (prevents double-ask bug)
    if (hasAskedFirstQuestionRef.current) {
      console.log("[Q1 Effect] Skipping - already asked first question");
      return;
    }

    if (step === 'interview' && avatarElement && interview?.questions?.length > 0 && currentQuestionIndex === 0) {

      const firstQuestion = interview.questions[0];
      const firstQuestionText = firstQuestion.text;
      // Get dynamic time from first question, default to 120s
      const firstQuestionTime = firstQuestion.suggested_time_seconds || 120;

      console.log(`[Q1 Effect Triggered] Will ask Question 1 with ${firstQuestionTime}s after 1.5s delay...`);

      // Mark as asked BEFORE asking to prevent race conditions
      hasAskedFirstQuestionRef.current = true;

      setCurrentQuestionText(firstQuestionText);
      setTotalQuestionsAsked(1);
      setCurrentQuestionType('Preset');
      setNextQuestionTime(firstQuestionTime); // Set dynamic time for Q1

      // Increased delay to 1.5s to allow TTS service to fully initialize
      // This is a common issue with browser audio context requiring user interaction
      const timer = setTimeout(() => {
        console.log(`[Q1 Effect] NOW calling askQuestion for: "${firstQuestionText.substring(0, 50)}..."`);
        askQuestion(firstQuestionText, firstQuestionTime);
      }, 1500); // Increased from 100ms to 1500ms

      return () => clearTimeout(timer);
    } else {
      if (step !== 'interview') console.log("[Q1 Effect] Not running: Step is not 'interview'.");
      else if (!avatarElement) console.log("[Q1 Effect] Not running: Avatar element not ready.");
      else if (!interview?.questions?.length > 0) console.log("[Q1 Effect] Not running: Interview/Questions not loaded.");
      else if (currentQuestionIndex !== 0) console.log("[Q1 Effect] Not running: Not the first question.");
    }
  }, [step, avatarElement, interview, currentQuestionIndex, askQuestion]);
  // --- End Fix 2 ---

  useEffect(() => {
    loadInterview();
  }, [loadInterview]);

  useEffect(() => {
    if (step === 'interview' && interview && !avatarElement) {
      initializeAvatar();
    }
  }, [step, interview, avatarElement, initializeAvatar]);

  useEffect(() => {
    return () => {
      if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
        console.log("Media stream tracks stopped on unmount.");
      }
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
        mediaRecorderRef.current.stop();
      }
    };
  }, [mediaStream]);

  // --- Timer Effects ---

  // Initialize timer values when interview starts (but don't start counting yet)
  useEffect(() => {
    if (step === 'interview' && interview?.time_per_question_seconds) {
      console.log("[Timer] Initializing timer values...");
      setTimePerQuestion(interview.time_per_question_seconds);
      setQuestionTimeRemaining(interview.time_per_question_seconds);
      setTotalTimeRemaining(interview.total_time_seconds);
      setInterviewStartTime(Date.now());
      setIsTimerActive(true);
      setIsTimerPaused(true); // Start paused until first question is asked
    }
  }, [step, interview?.time_per_question_seconds, interview?.total_time_seconds]);

  // Total interview timer - only counts down when NOT paused
  useEffect(() => {
    if (!isTimerActive || isTimerPaused) {
      // Timer is paused or not active - clear any existing interval
      if (totalTimerRef.current) {
        clearInterval(totalTimerRef.current);
        totalTimerRef.current = null;
      }
      return;
    }

    // Timer is active and NOT paused - start counting
    console.log("[Timer] Total timer RUNNING");
    totalTimerRef.current = setInterval(() => {
      setTotalTimeRemaining(prev => {
        if (prev <= 1) {
          clearInterval(totalTimerRef.current);
          totalTimerRef.current = null;
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => {
      if (totalTimerRef.current) {
        clearInterval(totalTimerRef.current);
        totalTimerRef.current = null;
      }
    };
  }, [isTimerActive, isTimerPaused]);

  // Handle question timer reaching 0 - auto submit
  useEffect(() => {
    if (questionTimeRemaining === 0 && isTimerActive && !submitting) {
      console.log("[Timer Effect] Question time expired, triggering auto-submit...");
      autoSubmitResponse();
    }
  }, [questionTimeRemaining, isTimerActive, submitting, autoSubmitResponse]);

  // Handle total interview time reaching 0 - HARD STOP
  useEffect(() => {
    if (totalTimeRemaining === 0 && isTimerActive) {
      console.log("[Timer Effect] Total interview time expired - HARD STOP");
      completeInterview('timeout');
    }
  }, [totalTimeRemaining, isTimerActive, completeInterview]);

  // Clean up timers on unmount
  useEffect(() => {
    return () => {
      if (questionTimerRef.current) {
        clearInterval(questionTimerRef.current);
      }
      if (totalTimerRef.current) {
        clearInterval(totalTimerRef.current);
      }
    };
  }, []);
  // --- End Timer Effects ---

  // --- UI RENDERING LOGIC --- 

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading interview...</p>
        </div>
      </div>
    );
  }

  if (step === 'error') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-50 to-pink-100">
        <Card className="max-w-md mx-auto">
          <CardBody className="text-center">
            <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Interview Not Found</h2>
            <p className="text-gray-600 mb-4">The interview link you're trying to access is invalid or has expired.</p>
            <Button onClick={() => navigate('/')} variant="primary">
              Go Home
            </Button>
          </CardBody>
        </Card>
      </div>
    );
  }

  if (step === 'register') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12">
        <div className="max-w-2xl mx-auto px-4">
          <Card className="shadow-xl">
            <CardHeader className="text-center">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Interview Registration</h1>
              <p className="text-gray-600">Please provide your details to start the interview</p>
            </CardHeader>
            <CardBody>
              <form onSubmit={handleCandidateRegistration} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Full Name *
                  </label>
                  <Input
                    type="text"
                    value={candidate.name}
                    onChange={(e) => setCandidate(prev => ({ ...prev, name: e.target.value }))}
                    required
                    placeholder="Enter your full name"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address *
                  </label>
                  <Input
                    type="email"
                    value={candidate.email}
                    onChange={(e) => setCandidate(prev => ({ ...prev, email: e.target.value }))}
                    required
                    placeholder="Enter your email"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Phone Number *
                  </label>
                  <Input
                    type="tel"
                    value={candidate.phone}
                    onChange={(e) => setCandidate(prev => ({ ...prev, phone: e.target.value }))}
                    required
                    placeholder="Enter your phone number"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Resume (Optional)
                  </label>
                  <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md hover:border-gray-400 transition-colors">
                    <div className="space-y-1 text-center">
                      <Upload className="mx-auto h-12 w-12 text-gray-400" />
                      <div className="flex text-sm text-gray-600">
                        <label htmlFor="resume-upload" className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500">
                          <span>Upload a file</span>
                          <input
                            id="resume-upload"
                            name="resume-upload"
                            type="file"
                            className="sr-only"
                            accept=".pdf,.doc,.docx,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            onChange={handleResumeChange}
                          />
                        </label>
                        <p className="pl-1">or drag and drop</p>
                      </div>
                      <p className="text-xs text-gray-500">PDF, DOC, DOCX up to 10MB</p>
                    </div>
                  </div>
                  {candidate.resume && (
                    <div className="mt-2 flex items-center text-sm text-green-600">
                      <FileText className="h-4 w-4 mr-2" />
                      {candidate.resume.name}
                    </div>
                  )}
                </div>

                <Button
                  type="submit"
                  variant="primary"
                  size="lg"
                  className="w-full"
                  loading={submitting}
                  disabled={submitting}
                >
                  Register for Interview
                </Button>
              </form>
            </CardBody>
          </Card>
        </div>
      </div>
    );
  }

  if (step === 'permissions') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12">
        <div className="max-w-2xl mx-auto px-4">
          <Card className="shadow-xl">
            <CardHeader className="text-center">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Permission Required</h1>
              <p className="text-gray-600">To conduct the interview, we need access to your microphone and camera.</p>
            </CardHeader>
            <CardBody className="text-center">
              <div className="space-y-6 mb-8">
                {/* Permission Status */}
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Mic className="h-6 w-6 text-blue-500" />
                      <span className="font-medium">Microphone</span>
                    </div>
                    <div className={`px-3 py-1 rounded-full text-sm ${permissions.microphone
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-600'
                      }`}>
                      {permissions.microphone ? 'Granted' : 'Required'}
                    </div>
                  </div>

                  <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Camera className="h-6 w-6 text-blue-500" />
                      <span className="font-medium">Camera</span>
                    </div>
                    <div className={`px-3 py-1 rounded-full text-sm ${permissions.camera
                      ? 'bg-green-100 text-green-800'
                      : 'bg-gray-100 text-gray-600'
                      }`}>
                      {permissions.camera ? 'Granted' : 'Required'}
                    </div>
                  </div>
                </div>

                {/* Error Message */}
                {permissionError && (
                  <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-red-700 text-sm">
                      <strong>Permission Error:</strong> {permissionError}
                    </p>
                  </div>
                )}

                {/* Instructions */}
                <div className="text-left bg-blue-50 p-4 rounded-lg">
                  <h3 className="font-semibold text-blue-900 mb-2">Instructions:</h3>
                  <ul className="text-sm text-blue-800 space-y-1">
                    <li>• Click "Grant Permissions" to allow access to your devices.</li>
                    <li>• Make sure to click "Allow" when prompted by your browser.</li>
                  </ul>
                </div>
              </div>

              <div className="space-y-3">
                <Button
                  onClick={handlePermissionRequest}
                  variant="primary"
                  size="lg"
                  className="w-full"
                  loading={requestingPermissions}
                  disabled={requestingPermissions}
                >
                  {requestingPermissions ? 'Requesting Permissions...' : 'Grant Permissions'}
                </Button>

                <Button
                  onClick={() => setStep('register')}
                  variant="secondary"
                  size="lg"
                  className="w-full"
                >
                  Back to Registration
                </Button>
              </div>
            </CardBody>
          </Card>
        </div>
      </div>
    );
  }

  if (step === 'ready') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 py-12">
        <div className="max-w-2xl mx-auto px-4">
          <Card className="shadow-xl">
            <CardHeader className="text-center">
              <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Ready to Start!</h1>
              <p className="text-gray-600">You're all set. Ensure you have a quiet environment.</p>
            </CardHeader>
            <CardBody className="text-center">
              <div className="space-y-4 mb-6">
                <div className="flex items-center justify-center space-x-2 text-gray-600">
                  <Camera className="h-5 w-5" />
                  <span>Camera Enabled</span>
                </div>
                <div className="flex items-center justify-center space-x-2 text-gray-600">
                  <Mic className="h-5 w-5" />
                  <span>Microphone Enabled</span>
                </div>
                <div className="flex items-center justify-center space-x-2 text-gray-600">
                  <Clock className="h-5 w-5" />
                  <span>Estimated Duration: {interview?.estimated_duration || 'N/A'} min</span>
                </div>
              </div>

              <Button
                onClick={startInterview}
                variant="primary"
                size="lg"
                className="w-full"
                loading={submitting}
                disabled={submitting}
              >
                Start Interview
              </Button>
            </CardBody>
          </Card>
        </div>
      </div>
    );
  }

  if (step === 'interview') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-100">
        <div className="container mx-auto px-4 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* AI Avatar */}
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <h3 className="text-lg font-semibold">AI Interviewer</h3>
                </CardHeader>
                <CardBody>
                  <div id="avatar-container" className="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
                    {avatarElement ? (
                      <div key="avatar-wrapper" ref={node => {
                        if (node) {
                          while (node.firstChild) {
                            node.removeChild(node.firstChild);
                          }
                          node.appendChild(avatarElement);
                        }
                      }} />
                    ) : (
                      <div className="text-gray-500">AI Avatar Loading...</div>
                    )}
                  </div>
                </CardBody>
              </Card>

              {/* --- FIX 2: Update "Current Question" Card --- */}
              <Card>
                <CardHeader>
                  {/* Title now shows the *type* of question */}
                  <h3 className="text-lg font-semibold">{currentQuestionType} Question</h3>
                </CardHeader>
                <CardBody>
                  <p className="text-gray-700">
                    {currentQuestionText || "Waiting for question..."}
                  </p>

                  {/* Show tags only if it's a preset question */}
                  {currentQuestionType === 'Preset' && interview?.questions[currentQuestionIndex]?.tags && (
                    <div className="mt-4 flex flex-wrap gap-2">
                      {interview.questions[currentQuestionIndex].tags.map((tag, index) => (
                        <span key={index} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                </CardBody>
              </Card>
              {/* --- End Fix 2 --- */}

              {/* --- Live Transcript Panel --- */}
              <Card className={isRecording ? 'border-green-500 border-2' : ''}>
                <CardHeader>
                  <h3 className="text-lg font-semibold flex items-center">
                    <Mic className={`h-5 w-5 mr-2 ${isRecording ? 'text-green-500 animate-pulse' : 'text-gray-400'}`} />
                    Your Response (Live)
                    {isRecording && (
                      <span className="ml-2 px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full">
                        Recording...
                      </span>
                    )}
                  </h3>
                </CardHeader>
                <CardBody>
                  <div className="min-h-[100px] max-h-[200px] overflow-y-auto bg-gray-50 rounded-lg p-4 border">
                    {(liveTranscript || interimTranscript) ? (
                      <p className="text-gray-700 leading-relaxed">
                        {liveTranscript}
                        <span className="text-gray-400 italic">{interimTranscript}</span>
                      </p>
                    ) : (
                      <p className="text-gray-400 italic text-center">
                        {isRecording
                          ? "Start speaking to see your transcript..."
                          : "Click 'Start Recording' and speak to see your response here"}
                      </p>
                    )}
                  </div>
                  {(liveTranscript || interimTranscript) && (
                    <p className="text-xs text-gray-500 mt-2">
                      💡 This is a preview. Your actual response will be transcribed by the server after submission.
                    </p>
                  )}
                </CardBody>
              </Card>
              {/* --- End Live Transcript Panel --- */}
            </div>

            {/* Candidate Video and Controls */}
            <div className="space-y-4">
              <Card>
                <CardHeader>
                  <h3 className="text-lg font-semibold">Your Video</h3>
                </CardHeader>
                <CardBody>
                  <video
                    ref={videoRef}
                    autoPlay
                    muted
                    className="w-full h-48 bg-gray-900 rounded-lg"
                  />
                </CardBody>
              </Card>

              {/* Recording Controls */}
              <Card>
                <CardHeader>
                  <h3 className="text-lg font-semibold">Record Your Response</h3>
                </CardHeader>
                <CardBody>
                  <div className="space-y-4">
                    <div className="flex justify-center space-x-4">
                      <Button
                        onClick={isRecording ? stopRecording : startRecording}
                        variant={isRecording ? "danger" : "primary"}
                        size="lg"
                        disabled={submitting}
                      >
                        {isRecording ? (
                          <>
                            <MicOff className="h-5 w-5 mr-2" />
                            Stop Recording
                          </>
                        ) : (
                          <>
                            <Mic className="h-5 w-5 mr-2" />
                            Start Recording
                          </>
                        )}
                      </Button>
                    </div>

                    {audioResponse && !isRecording && (
                      <div className="text-center mt-4">
                        <p className="text-sm text-green-600 mb-2">Recording complete! Ready to submit.</p>
                        <Button
                          onClick={() => submitResponse(false)}
                          variant="success"
                          loading={submitting}
                          disabled={submitting}
                        >
                          Submit Response
                        </Button>
                      </div>
                    )}

                    {/* End Interview Button */}
                    <div className="border-t pt-4 mt-4">
                      <div className="text-center">
                        <p className="text-xs text-gray-500 mb-2">Want to end the interview early?</p>
                        <Button
                          onClick={() => {
                            if (window.confirm('Are you sure you want to end the interview? Your responses so far will be saved.')) {
                              completeInterview('manual');
                            }
                          }}
                          variant="secondary"
                          size="sm"
                          disabled={submitting}
                          className="text-red-600 hover:bg-red-50"
                        >
                          End Interview
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardBody>
              </Card>

              {/* --- Timer Display Card --- */}
              {(timePerQuestion || totalTimeRemaining) && (
                <Card className={`${isTimerPaused
                  ? 'border-purple-500 border-2 bg-purple-50'
                  : questionTimeRemaining !== null && questionTimeRemaining <= 30
                    ? 'border-red-500 border-2'
                    : ''
                  }`}>
                  <CardHeader>
                    <h3 className="text-lg font-semibold flex items-center justify-between">
                      <span className="flex items-center">
                        <Clock className="h-5 w-5 mr-2" />
                        Time Remaining
                      </span>
                      {/* Timer Status Badge */}
                      {isTimerPaused ? (
                        <span className="px-3 py-1 bg-purple-100 text-purple-700 text-sm rounded-full flex items-center">
                          {isSpeaking ? '🔊 Listening...' : '⏸️ Paused'}
                        </span>
                      ) : (
                        <span className="px-3 py-1 bg-green-100 text-green-700 text-sm rounded-full flex items-center">
                          🎤 Recording
                        </span>
                      )}
                    </h3>
                  </CardHeader>
                  <CardBody>
                    {/* Speaking/Prep Message */}
                    {isTimerPaused && (
                      <div className="mb-4 p-3 bg-purple-100 rounded-lg text-center">
                        {isSpeaking ? (
                          <p className="text-purple-700 font-medium">🔊 Listen to the question...</p>
                        ) : (
                          <p className="text-purple-700 font-medium">💡 Prepare your answer...</p>
                        )}
                      </div>
                    )}

                    <div className="grid grid-cols-2 gap-4">
                      {/* Question Timer */}
                      <div className="text-center">
                        <p className="text-sm text-gray-500 mb-1">This Question</p>
                        <p className={`text-3xl font-bold ${isTimerPaused
                          ? 'text-purple-600'
                          : questionTimeRemaining !== null && questionTimeRemaining <= 30
                            ? 'text-red-600 animate-pulse'
                            : questionTimeRemaining !== null && questionTimeRemaining <= 60
                              ? 'text-orange-500'
                              : 'text-blue-600'
                          }`}>
                          {formatTime(questionTimeRemaining)}
                        </p>
                        {!isTimerPaused && questionTimeRemaining !== null && questionTimeRemaining <= 30 && (
                          <p className="text-xs text-red-500 mt-1">Hurry! Time almost up!</p>
                        )}
                      </div>
                      {/* Total Timer */}
                      <div className="text-center">
                        <p className="text-sm text-gray-500 mb-1">Total Interview</p>
                        <p className={`text-3xl font-bold ${isTimerPaused
                          ? 'text-purple-600'
                          : totalTimeRemaining !== null && totalTimeRemaining <= 60
                            ? 'text-red-600'
                            : 'text-green-600'
                          }`}>
                          {formatTime(totalTimeRemaining)}
                        </p>
                        {!isTimerPaused && totalTimeRemaining !== null && totalTimeRemaining <= 60 && (
                          <p className="text-xs text-red-500 mt-1">Interview ending soon!</p>
                        )}
                      </div>
                    </div>
                    {/* Question time progress bar */}
                    {timePerQuestion && questionTimeRemaining !== null && (
                      <div className="mt-4">
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full transition-all duration-1000 ${isTimerPaused
                              ? 'bg-purple-500'
                              : questionTimeRemaining <= 30
                                ? 'bg-red-500'
                                : 'bg-blue-500'
                              }`}
                            style={{ width: `${(questionTimeRemaining / timePerQuestion) * 100}%` }}
                          />
                        </div>
                      </div>
                    )}
                  </CardBody>
                </Card>
              )}
              {/* --- End Timer Display --- */}

              {/* --- FIX 2: Update "Progress" Card --- */}
              <Card>
                <CardHeader>
                  <h3 className="text-lg font-semibold">Interview Progress</h3>
                </CardHeader>
                <CardBody>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm font-medium">
                      {/* Shows preset question progress */}
                      <span>Core Question {currentQuestionIndex + 1} of {interview?.questions?.length || 0}</span>
                      {/* Shows total questions answered */}
                      <span>Total Asked: {totalQuestionsAsked}</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${((currentQuestionIndex + 1) / (interview?.questions?.length || 1)) * 100}%` }}
                      />
                    </div>
                  </div>
                </CardBody>
              </Card>
              {/* --- End Fix 2 --- */}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (step === 'complete') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 py-12">
        <div className="max-w-2xl mx-auto px-4">
          <Card className="shadow-xl">
            <CardHeader className="text-center">
              <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Interview Completed!</h1>
              <p className="text-gray-600">Thank you for completing the interview. Your responses have been recorded and will be reviewed.</p>
            </CardHeader>
            <CardBody className="text-center">
              <div className="space-y-4">
                <p className="text-gray-700">
                  We'll be in touch soon with the results. Thank you for your time and interest!
                </p>
                <Button onClick={() => navigate('/')} variant="primary">
                  Return Home
                </Button>
              </div>
            </CardBody>
          </Card>
        </div>
      </div>
    );
  }

  return null;
};

export default PublicInterview;