import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/authService';

const AuthContext = createContext();

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const accessToken = localStorage.getItem('access_token');
    if (accessToken) {
      console.log('Access token found, fetching user data...');
      authService.getCurrentUser()
        .then(userData => {
          console.log('User data fetched successfully:', userData);
          setUser(userData);
        })
        .catch((error) => {
          console.error('Failed to fetch user data:', error);
          // Handle 401 errors by clearing tokens
          if (error.response?.status === 401) {
            console.log('Token expired or invalid, clearing tokens');
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            setUser(null);
          } else {
            // For other errors, keep the user logged in but log the error
            console.warn('Non-401 error during user data fetch:', error);
          }
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      console.log('No access token found');
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    try {
      const response = await authService.login(email, password);
      
      // Handle both standardized and legacy response formats
      const responseData = response?.data || response;
      const access_token = responseData?.data?.access_token || responseData?.access_token;
      const refresh_token = responseData?.data?.refresh_token || responseData?.refresh_token;
      const userData = responseData?.data?.user || responseData?.user;
      
      if (access_token && refresh_token) {
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);
        setUser(userData);
        return { success: true, data: userData };
      } else {
        throw new Error('Invalid response format from login endpoint');
      }
    } catch (error) {
      console.error('Login error:', error);
      
      // Enhanced error message extraction
      let errorMessage = 'Login failed';
      if (error.response?.data) {
        const data = error.response.data;
        errorMessage = data.detail || data.error || data.message || errorMessage;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      return { 
        success: false, 
        error: errorMessage
      };
    }
  };

  const register = async (userData) => {
    try {
      const response = await authService.register(userData);
      
      // Handle both standardized and legacy response formats
      const responseData = response?.data || response;
      const user = responseData?.data || responseData;
      
      return { success: true, data: user };
    } catch (error) {
      console.error('Registration error:', error);
      
      // Enhanced error message extraction
      let errorMessage = 'Registration failed';
      if (error.response?.data) {
        const data = error.response.data;
        errorMessage = data.detail || data.error || data.message || errorMessage;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      return { 
        success: false, 
        error: errorMessage
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  };

  const updateUser = (userData) => {
    setUser(userData);
  };

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    updateUser
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}


