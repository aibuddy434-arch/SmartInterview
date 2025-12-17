import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create a separate axios instance for public endpoints that don't require authentication
const publicApi = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for public API calls
publicApi.interceptors.request.use(
  (config) => {
    // Don't set Content-Type for FormData - let browser set it with boundary
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
publicApi.interceptors.response.use(
  (response) => {
    // Log successful responses for debugging
    console.log('Public API Response:', response.status, response.config.url);
    return response;
  },
  async (error) => {
    // Handle error responses
    if (error.response?.status === 404) {
      console.log('Resource not found:', error.config?.url);
    } else if (error.response?.status >= 500) {
      console.log('Server error:', error.config?.url);
    } else if (error.code === 'NETWORK_ERROR' || error.message === 'Network Error') {
      console.log('Network error:', error.config?.url);
    }
    
    // Log error for debugging
    console.error('Public API Error:', error.response?.status, error.config?.url, error.message);
    return Promise.reject(error);
  }
);

export default publicApi;
