/**
 * Utility functions for consistent error handling across the application
 */

/**
 * Safely access nested object properties without throwing errors
 * @param {Object} obj - The object to access
 * @param {string} path - The property path (e.g., 'user.profile.name')
 * @param {*} defaultValue - Default value if property doesn't exist
 * @returns {*} - The property value or default value
 */
export const safeGet = (obj, path, defaultValue = undefined) => {
  if (!obj || typeof obj !== 'object') return defaultValue;
  
  const keys = path.split('.');
  let current = obj;
  
  for (const key of keys) {
    if (current && typeof current === 'object' && key in current) {
      current = current[key];
    } else {
      return defaultValue;
    }
  }
  
  return current !== undefined ? current : defaultValue;
};

/**
 * Safely extracts error message from various error response formats
 * @param {Error} error - The error object from try/catch
 * @param {string} fallbackMessage - Default message if no error details found
 * @returns {string} - Safe error message to display to user
 */




export const getErrorMessage = (error, fallbackMessage = 'An unexpected error occurred') => {
  if (!error) return fallbackMessage;

  // Handle Axios error responses
  if (error.response?.data) {
    const data = error.response.data;
    if (data.detail) return data.detail;
    if (data.error) return data.error;
    if (data.errors && Array.isArray(data.errors)) {
      return data.errors.join(', ');
    }
    if (data.message) return data.message;
  }

  // Handle network errors
  if (error.code === 'NETWORK_ERROR' || error.message === 'Network Error') {
    return 'Network connection failed. Please check your internet connection.';
  }

  // Handle timeout errors
  if (error.code === 'ECONNABORTED') {
    return 'Request timeout. Please try again.';
  }

  // Handle JWT/authentication errors
  if (error.response?.status === 401) {
    return 'Session expired. Please log in again.';
  }

  if (error.response?.status === 403) {
    return 'Access denied. You do not have permission to perform this action.';
  }

  if (error.response?.status === 404) {
    return 'Resource not found. Please check the URL and try again.';
  }

  if (error.response?.status >= 500) {
    return 'Server error. Please try again later.';
  }

  // Handle other error types
  if (error.message) return error.message;
  if (error.error) return error.error;

  return fallbackMessage;
};

// Validate required fields inside response
export const validateResponse = (response, requiredFields = [], fallbackMessage = 'Invalid response from server') => {
  if (!response || typeof response !== 'object') {
    return { success: false, data: null, error: fallbackMessage };
  }

  const isValid = requiredFields.every(field => {
    const fieldPath = field.split('.');
    let current = response;

    for (const key of fieldPath) {
      if (current && typeof current === 'object' && key in current) {
        current = current[key];
      } else {
        return false;
      }
    }
    return current !== null && current !== undefined;
  });

  if (isValid) {
    return { success: true, data: response, error: null };
  } else {
    return { success: false, data: null, error: fallbackMessage };
  }
};

// Handle raw responses safely
export const safeResponseHandler = (response, requiredFields = [], errorMessage = 'Invalid response from server') => {
  const validationResult = validateResponse(response, requiredFields, errorMessage);
  if (validationResult.success) {
    return validationResult;
  } else {
    console.error('Response validation failed:', response);
    return validationResult;
  }
};

// API call wrapper without validation
export const safeApiCall = async (apiCall, fallbackMessage = 'API call failed') => {
  try {
    const response = await apiCall();

    // Handle standardized backend response structure
    if (response && response.data) {
      const { success, data, message, error } = response.data;
      
      if (success === true) {
        return { success: true, data: data, error: null };
      } else {
        return { success: false, data: null, error: error || message || fallbackMessage };
      }
    }
    
    // Fallback for non-standardized responses (assume success)
    return { success: true, data: response, error: null };
  } catch (error) {
    const errorMessage = getErrorMessage(error, fallbackMessage);
    console.error('API call failed:', error);
    return { success: false, data: null, error: errorMessage };
  }
};

// API call wrapper WITH validation
export const safeApiCallWithValidation = async (apiCall, requiredFields = [], fallbackMessage = 'Request failed') => {
  try {
    const response = await apiCall();

    // Handle null/undefined response
    if (!response) {
      console.error('API call returned null/undefined response');
      return { success: false, data: null, error: 'No response received from server' };
    }

    // Handle standardized backend response structure
    if (response && response.data) {
      const { success, data, message, error } = response.data;
      
      if (success === true) {
        // Validate required fields in the data
        if (data && typeof data === 'object') {
          const validationResult = validateResponse(data, requiredFields, fallbackMessage);
          if (validationResult && validationResult.success) {
            return { success: true, data: data, error: null };
          } else {
            return validationResult || { success: false, data: null, error: fallbackMessage };
          }
        } else {
          return { success: false, data: null, error: 'Invalid data structure received from server' };
        }
      } else {
        return { success: false, data: null, error: error || message || fallbackMessage };
      }
    }
    
    // Fallback for non-standardized responses
    const fallbackResult = safeResponseHandler(response, requiredFields, fallbackMessage);
    return fallbackResult || { success: false, data: null, error: fallbackMessage };
  } catch (error) {
    const errorMessage = getErrorMessage(error, fallbackMessage);
    console.error('API call failed:', error);
    return { success: false, data: null, error: errorMessage };
  }
};

// Enhanced API call wrapper with comprehensive error handling
export const robustApiCall = async (apiCall, options = {}) => {
  const {
    requiredFields = [],
    fallbackMessage = 'Request failed',
    showToast = true,
    retryOn401 = true,
    maxRetries = 1
  } = options;

  let retryCount = 0;
  
  const attemptCall = async () => {
    try {
      const response = await apiCall();
      
      // Handle HTTP errors
      if (response.status >= 400) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      // Handle standardized backend response structure
      if (response && response.data) {
        const { success, data, message, error } = response.data;
        
        if (success === true) {
          // Validate required fields if specified
          if (requiredFields.length > 0) {
            const validationResult = validateResponse(data, requiredFields, fallbackMessage);
            if (validationResult.success) {
              return { success: true, data: data, error: null };
            } else {
              return validationResult;
            }
          }
          return { success: true, data: data, error: null };
        } else {
          return { success: false, data: null, error: error || message || fallbackMessage };
        }
      }
      
      // Fallback for non-standardized responses
      return { success: true, data: response, error: null };
    } catch (error) {
      // Handle 401 errors with retry logic
      if (error.response?.status === 401 && retryOn401 && retryCount < maxRetries) {
        retryCount++;
        console.log(`Retrying API call (attempt ${retryCount})...`);
        // Wait a bit before retry
        await new Promise(resolve => setTimeout(resolve, 1000));
        return attemptCall();
      }
      
      const errorMessage = getErrorMessage(error, fallbackMessage);
      console.error('API call failed:', error);
      return { success: false, data: null, error: errorMessage };
    }
  };

  return attemptCall();
};



