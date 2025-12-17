import api from './api';

export const interviewService = {
  // Create a new interview configuration
  async createInterviewConfig(configData) {
    try {
      const response = await api.post('/interviews/create', configData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Generate AI questions
  async generateQuestions(params) {
    try {
      const formData = new FormData();
      formData.append('job_role', params.job_role);
      formData.append('job_description', params.job_description);
      formData.append('difficulty', params.difficulty);
      formData.append('number_of_questions', params.number_of_questions);
      
      // Add focus areas as separate form fields
      params.focus.forEach(focus => {
        formData.append('focus_areas', focus);
      });

      const response = await api.post('/interviews/generate-questions', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get all interview configurations for the current user
  async getInterviewConfigs() {
    try {
      const response = await api.get('/interviews/configs');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get a specific interview configuration
  async getInterviewConfig(configId) {
    try {
      const response = await api.get(`/interviews/configs/${configId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Update an interview configuration
  async updateInterviewConfig(configId, updateData) {
    try {
      const response = await api.put(`/interviews/configs/${configId}`, updateData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Delete an interview configuration
  async deleteInterviewConfig(configId) {
    try {
      const response = await api.delete(`/interviews/configs/${configId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Add questions to an interview configuration
  async addQuestionsToConfig(configId, questions) {
    try {
      const response = await api.post(`/interviews/configs/${configId}/questions`, {
        questions: questions
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Public interview methods
  async getPublicInterview(interviewId) {
    try {
      const response = await api.get(`/public/interview/${interviewId}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  async registerCandidate(interviewId, candidateData) {
    try {
      const response = await api.post(`/public/interview/${interviewId}/register`, candidateData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  async startInterviewSession(sessionId) {
    try {
      const response = await api.post(`/public/session/${sessionId}/start`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  async submitResponse(sessionId, responseData) {
    try {
      const response = await api.post(`/public/session/${sessionId}/submit-response`, responseData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  async completeSession(sessionId) {
    try {
      const response = await api.post(`/public/session/${sessionId}/complete`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get available avatars (stub data for now)
  getAvailableAvatars() {
    return [
      { value: 'friendly', label: 'Friendly', description: 'Warm and approachable avatar' },
      { value: 'professional', label: 'Professional', description: 'Formal and business-like avatar' },
      { value: 'technical', label: 'Technical', description: 'Tech-focused and analytical avatar' },
      { value: 'casual', label: 'Casual', description: 'Relaxed and informal avatar' }
    ];
  },

  // Get available voices (stub data for now)
  getAvailableVoices() {
    return [
      { value: 'male_1', label: 'Male Voice 1', description: 'Deep and authoritative' },
      { value: 'male_2', label: 'Male Voice 2', description: 'Clear and professional' },
      { value: 'female_1', label: 'Female Voice 1', description: 'Warm and engaging' },
      { value: 'female_2', label: 'Female Voice 2', description: 'Clear and confident' },
      { value: 'neutral', label: 'Neutral Voice', description: 'Balanced and professional' }
    ];
  },

  // Get focus area options
  getFocusAreas() {
    return [
      { value: 'communication', label: 'Communication Skills' },
      { value: 'technical', label: 'Technical Skills' },
      { value: 'overall', label: 'Overall Assessment' }
    ];
  },

  // Get difficulty levels
  getDifficultyLevels() {
    return [
      { value: 'easy', label: 'Easy' },
      { value: 'medium', label: 'Medium' },
      { value: 'hard', label: 'Hard' }
    ];
  },

  // Get interview types
  getInterviewTypes() {
    return [
      { value: 'general', label: 'General Interviewer', description: 'AI-generated follow-up questions' },
      { value: 'specific', label: 'Specific Interviewer', description: 'Predefined questions only' }
    ];
  }
};


