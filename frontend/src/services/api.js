import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
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

// Response interceptor to handle errors and token refresh
api.interceptors.response.use(
  (response) => {
    // Log successful responses for debugging
    console.log('API Response:', response.status, response.config.url);
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // Handle 401 Unauthorized errors with token refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          console.log('Attempting to refresh token...');
          
          // Use a separate axios instance to avoid infinite loops
          const refreshResponse = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken
          }, {
            headers: {
              'Content-Type': 'application/json'
            }
          });
          
          // Handle standardized response structure
          const responseData = refreshResponse.data;
          const access_token = responseData?.data?.access_token || responseData?.access_token;
          
          if (access_token) {
            localStorage.setItem('access_token', access_token);
            console.log('Token refreshed successfully');
            
            // Retry the original request with new token
            originalRequest.headers.Authorization = `Bearer ${access_token}`;
            return api(originalRequest);
          } else {
            throw new Error('No access token in refresh response');
          }
        } catch (refreshError) {
          console.log('Token refresh failed:', refreshError.message);
          
          // Clear all tokens and redirect to login
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          
          // Show user-friendly message
          if (window.toast) {
            window.toast.error('Session expired. Please log in again.');
          }
          
          // Only redirect if not already on login page and not on public interview page
          if (window.location.pathname !== '/login' && !window.location.pathname.includes('/interview/')) {
            window.location.href = '/login';
          }
        }
      } else {
        console.log('No refresh token available, redirecting to login');
        
        // Clear all tokens
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        
        // Show user-friendly message
        if (window.toast) {
          window.toast.error('Please log in to continue.');
        }
        
        // Only redirect if not already on login page
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
      }
    }
    
    // Handle other error types
    if (error.response?.status === 403) {
      console.log('Access denied:', error.config?.url);
      if (window.toast) {
        window.toast.error('Access denied. You do not have permission to perform this action.');
      }
    } else if (error.response?.status >= 500) {
      console.log('Server error:', error.config?.url);
      if (window.toast) {
        window.toast.error('Server error. Please try again later.');
      }
    } else if (error.code === 'NETWORK_ERROR' || error.message === 'Network Error') {
      console.log('Network error:', error.config?.url);
      if (window.toast) {
        window.toast.error('Network connection failed. Please check your internet connection.');
      }
    }
    
    // Log error for debugging
    console.error('API Error:', error.response?.status, error.config?.url, error.message);
    return Promise.reject(error);
  }
);

export default api;


