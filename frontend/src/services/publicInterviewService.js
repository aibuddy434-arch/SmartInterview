import publicApi from './publicApi';

export const publicInterviewService = {
  // Get public interview configuration
  async getPublicInterview(interviewId) {
    try {
      const response = await publicApi.get(`/public/interview/${interviewId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Register candidate for interview
  async registerCandidate(interviewId, candidateData) {
    try {
      const response = await publicApi.post(`/public/interview/${interviewId}/register`, candidateData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Start interview session


// Start interview session
async startSession(sessionId) { // Parameter is now sessionId
  try {
    // The backend route is /session/{session_id}/start and doesn't need a request body.
    const response = await publicApi.post(`/public/session/${sessionId}/start`); // URL is now correct
    return response.data;
  } catch (error) {
    throw error;
  }
},

  // Get session details
  async getSession(sessionId) {
    try {
      const response = await publicApi.get(`/public/session/${sessionId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

// Replace the existing submitResponse function with this one

  // Submit response
  async submitResponse(sessionId, formData) { // Corrected: Accepts sessionId and formData
    try {
      // The formData already contains question_number and audio_file
      // The backend route is /public/session/{session_id}/submit-response
      const response = await publicApi.post(`/public/session/${sessionId}/submit-response`, formData, {
        headers: {
          // Content-Type is set automatically by browser for FormData
          // 'Content-Type': 'multipart/form-data', 
        },
      });
      return response.data; // Return the parsed JSON response from the backend
    } catch (error) {
       console.error("Error in submitResponse service:", error);
       // Rethrow the error so the component's catch block can handle it
       // This allows PublicInterview.js to show the toast message
       throw error; 
    }
  },

  // Complete session
  async completeSession(sessionId) {
    try {
      const response = await publicApi.post(`/public/session/${sessionId}/complete`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get session responses
  async getSessionResponses(sessionId) {
    try {
      const response = await publicApi.get(`/public/session/${sessionId}/responses`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

