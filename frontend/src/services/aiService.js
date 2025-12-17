// Replace the entire contents of frontend/src/services/aiService.js

import api from './api'; // For authenticated requests
import publicApi from './publicApi'; // For public requests

export const aiService = {
// Replace the existing generateTTS function in aiService.js with this one
  
  /**
   * Generate speech from text using the PUBLIC endpoint.
   * THIS IS THE FUNCTION USED BY THE PUBLIC INTERVIEW.
   * @param {string} text - Text to convert to speech
   * @returns {Promise<Blob>} Audio blob
   */
  async generateTTS(text) {
    // Basic validation
    if (!text || typeof text !== 'string' || text.trim() === '') {
      const errorMsg = 'TTS Error: Text input is invalid or empty.';
      console.error(errorMsg);
      return Promise.reject(new Error(errorMsg)); // Reject promise
    }

    try {
      console.log(`[aiService] Calling PUBLIC TTS endpoint (/api/public/tts) for text: "${text.substring(0, 50)}..."`);
      
      const response = await publicApi.post('/public/tts', 
        { text: text.trim() }, 
        { 
          responseType: 'blob', 
          timeout: 30000 // *** INCREASED TIMEOUT TO 30 SECONDS ***
        }
      );
      
      if (response.data instanceof Blob && response.data.type.startsWith('audio/')) {
        console.log("[aiService] Received valid audio blob from /public/tts. Size:", response.data.size);
        return response.data; 
      } else {
        console.error("[aiService] Received invalid data format from /public/tts:", response.data);
        throw new Error("Invalid audio data received from server.");
      }
      
    } catch (error) {
      // *** REMOVED toast.error CALL HERE ***
      // Log the detailed error
      console.error('[aiService] TTS generation via /public/tts failed:', error.response?.data || error.message || error);
      // Re-throw the error so the calling component (PublicInterview.js) can handle it (e.g., show its own toast)
      throw error; 
    }
  },

  // --- Functions below are likely for ADMIN/LOGGED-IN users ---
  // --- They should use the authenticated 'api' client ---

  /**
   * Generate speech from text using the SECURE endpoint (likely for admins).
   * @param {string} text - Text to convert to speech
   * @param {string} voice - Voice to use
   * @returns {Promise<Blob>} Audio blob
   */
  async generateSpeechSecure(text, voice = 'default') {
    try {
      const formData = new FormData();
      formData.append('text', text);
      formData.append('voice', voice);
      
      console.log("[aiService] Calling SECURE TTS endpoint (/api/ai/tts)");
      // Use the secure 'api' instance
      const response = await api.post('/ai/tts', formData, {
        // Secure endpoint might expect FormData
        headers: { 
         // 'Content-Type': 'multipart/form-data', // Often set automatically for FormData
        }, 
        responseType: 'blob',
        timeout: 15000 
      });
      return response.data;
    } catch (error) {
      console.error('[aiService] Secure TTS generation failed:', error);
      throw error;
    }
  },


  /**
   * Transcribe audio file using the SECURE endpoint.
   * @param {File} audioFile - Audio file to transcribe
   * @returns {Promise<Object>} Transcription result
   */
  async transcribeAudio(audioFile) {
    try {
      const formData = new FormData();
      formData.append('audio_file', audioFile);
      
      console.log("[aiService] Calling SECURE transcribe endpoint (/api/ai/transcribe)");
      // Use the secure 'api' instance
      const response = await api.post('/ai/transcribe', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      console.error('[aiService] Transcription failed:', error);
      throw error;
    }
  },

  /**
   * Get available voices using the SECURE endpoint.
   * @returns {Promise<Object>} Available voices
   */
  async getAvailableVoices() {
    try {
      console.log("[aiService] Calling SECURE voices endpoint (/api/ai/voices)");
      // Use the secure 'api' instance
      const response = await api.get('/ai/voices');
      return response.data;
    } catch (error) {
      console.error('[aiService] Failed to get voices:', error);
      throw error;
    }
  },
  
   /**
   * Check AI services health using the SECURE endpoint
   * @returns {Promise<Object>} Health status
   */
  async checkHealth() {
    try {
      console.log("[aiService] Calling SECURE health endpoint (/api/ai/health)");
      const response = await api.get('/ai/health');
      return response.data;
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  },
};