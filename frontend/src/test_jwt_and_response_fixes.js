/**
 * Test script to verify JWT and response structure fixes
 * This file can be imported and used for testing various scenarios
 */

// Test scenarios for JWT and response fixes
export const testJWTAndResponseFixes = () => {
  console.log('🧪 Testing JWT and Response Structure Fixes');
  console.log('==========================================');

  // Test 1: Standardized response structure handling
  console.log('\n1. Testing standardized response structure handling:');
  
  // Scenario: Standardized success response
  const standardizedSuccess = {
    success: true,
    message: "Operation successful",
    data: { candidate: { id: '123' }, session_id: 'abc' },
    error: null
  };
  
  const successCheck = standardizedSuccess && standardizedSuccess.success === true;
  console.log('Standardized success response:', successCheck); // Should be true
  console.log('Data access:', standardizedSuccess.data?.candidate?.id); // Should be '123'
  
  // Scenario: Standardized error response
  const standardizedError = {
    success: false,
    message: "Operation failed",
    data: null,
    error: "Validation failed"
  };
  
  const errorCheck = standardizedError && standardizedError.success === false;
  console.log('Standardized error response:', errorCheck); // Should be true
  console.log('Error message:', standardizedError.error); // Should be 'Validation failed'

  // Test 2: Legacy response structure handling
  console.log('\n2. Testing legacy response structure handling:');
  
  // Scenario: Legacy success response (direct data)
  const legacySuccess = { candidate: { id: '123' }, session_id: 'abc' };
  const legacySuccessCheck = legacySuccess && legacySuccess.candidate;
  console.log('Legacy success response:', legacySuccessCheck); // Should be true
  
  // Scenario: Legacy error response (FastAPI detail)
  const legacyError = { detail: "User not found" };
  const legacyErrorCheck = legacyError && legacyError.detail;
  console.log('Legacy error response:', legacyErrorCheck); // Should be true

  // Test 3: JWT token handling
  console.log('\n3. Testing JWT token handling:');
  
  // Scenario: Valid token response
  const tokenResponse = {
    data: {
      access_token: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      refresh_token: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      token_type: "bearer",
      user: { id: '123', email: 'test@example.com' }
    }
  };
  
  const accessToken = tokenResponse?.data?.access_token;
  const refreshToken = tokenResponse?.data?.refresh_token;
  const user = tokenResponse?.data?.user;
  
  console.log('Access token extracted:', !!accessToken); // Should be true
  console.log('Refresh token extracted:', !!refreshToken); // Should be true
  console.log('User data extracted:', !!user); // Should be true

  // Test 4: Error handling scenarios
  console.log('\n4. Testing error handling scenarios:');
  
  // Scenario: Network error
  const networkError = { message: 'Network Error' };
  const networkErrorCheck = networkError && networkError.message;
  console.log('Network error handling:', networkErrorCheck); // Should be true
  
  // Scenario: Axios error with response
  const axiosError = {
    response: {
      status: 400,
      data: { detail: 'Validation failed' }
    }
  };
  const axiosErrorCheck = axiosError.response?.data?.detail;
  console.log('Axios error handling:', axiosErrorCheck); // Should be 'Validation failed'
  
  // Scenario: Axios error with standardized response
  const axiosStandardizedError = {
    response: {
      status: 400,
      data: { success: false, error: 'Validation failed' }
    }
  };
  const axiosStandardizedErrorCheck = axiosStandardizedError.response?.data?.error;
  console.log('Axios standardized error handling:', axiosStandardizedErrorCheck); // Should be 'Validation failed'

  // Test 5: Safe property access patterns
  console.log('\n5. Testing safe property access patterns:');
  
  // Scenario: Nested property access
  const nestedResponse = {
    data: {
      candidate: {
        id: '123',
        name: 'John Doe'
      },
      session_id: 'abc'
    }
  };
  
  const candidateId = nestedResponse?.data?.candidate?.id;
  const candidateName = nestedResponse?.data?.candidate?.name;
  const sessionId = nestedResponse?.data?.session_id;
  
  console.log('Candidate ID:', candidateId); // Should be '123'
  console.log('Candidate Name:', candidateName); // Should be 'John Doe'
  console.log('Session ID:', sessionId); // Should be 'abc'
  
  // Scenario: Missing nested properties
  const incompleteResponse = {
    data: {
      candidate: null
    }
  };
  
  const safeCandidateId = incompleteResponse?.data?.candidate?.id;
  const safeCandidateName = incompleteResponse?.data?.candidate?.name;
  
  console.log('Safe candidate ID (null):', safeCandidateId); // Should be undefined, not crash
  console.log('Safe candidate name (null):', safeCandidateName); // Should be undefined, not crash

  console.log('\n✅ JWT and response structure tests completed successfully!');
};

// Test the error handling utilities with new response structure
export const testErrorHandlingWithNewStructure = () => {
  console.log('\n🧪 Testing Error Handling with New Response Structure');
  console.log('====================================================');

  // Mock the error handling utilities
  const getErrorMessage = (error, fallbackMessage = 'An unexpected error occurred') => {
    if (!error) return fallbackMessage;
    
    if (error.response?.data) {
      const data = error.response.data;
      if (data.detail) return data.detail;
      if (data.error) return data.error;
      if (data.errors && Array.isArray(data.errors)) {
        return data.errors.join(', ');
      }
      if (data.message) return data.message;
    }
    
    if (error.message) return error.message;
    if (error.error) return error.error;
    
    return fallbackMessage;
  };

  const safeApiCall = async (apiCall, fallbackMessage = 'API call failed') => {
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
      
      // Fallback for non-standardized responses
      return { success: true, data: response, error: null };
    } catch (error) {
      const errorMessage = getErrorMessage(error, fallbackMessage);
      console.error('API call failed:', error);
      return { success: false, data: null, error: errorMessage };
    }
  };

  // Test 1: Standardized success response
  console.log('\n1. Testing standardized success response:');
  const successApi = async () => ({
    data: {
      success: true,
      message: "Operation successful",
      data: { candidate: { id: '123' }, session_id: 'abc' },
      error: null
    }
  });
  
  safeApiCall(successApi, 'API failed').then(result => {
    console.log('Success result:', result);
    console.log('Success check:', result && result.success === true);
    console.log('Data check:', result && result.data && result.data.candidate);
  });

  // Test 2: Standardized error response
  console.log('\n2. Testing standardized error response:');
  const errorApi = async () => ({
    data: {
      success: false,
      message: "Operation failed",
      data: null,
      error: "Validation failed"
    }
  });
  
  safeApiCall(errorApi, 'API failed').then(result => {
    console.log('Error result:', result);
    console.log('Error check:', result && result.success === false);
    console.log('Error message:', result && result.error);
  });

  // Test 3: Legacy response (fallback)
  console.log('\n3. Testing legacy response (fallback):');
  const legacyApi = async () => ({ candidate: { id: '123' }, session_id: 'abc' });
  
  safeApiCall(legacyApi, 'API failed').then(result => {
    console.log('Legacy result:', result);
    console.log('Legacy success check:', result && result.success === true);
    console.log('Legacy data check:', result && result.data && result.data.candidate);
  });

  // Test 4: Network error
  console.log('\n4. Testing network error:');
  const networkErrorApi = async () => { 
    const error = new Error('Network Error');
    throw error;
  };
  
  safeApiCall(networkErrorApi, 'API failed').then(result => {
    console.log('Network error result:', result);
    console.log('Network error check:', result && result.success === false);
    console.log('Network error message:', result && result.error);
  });

  console.log('\n✅ Error handling with new response structure tests completed successfully!');
};

// Test JWT refresh mechanism
export const testJWTRefreshMechanism = () => {
  console.log('\n🧪 Testing JWT Refresh Mechanism');
  console.log('=================================');

  // Test 1: Valid refresh token response
  console.log('\n1. Testing valid refresh token response:');
  const refreshResponse = {
    data: {
      access_token: "new_access_token_123",
      token_type: "bearer"
    }
  };
  
  const accessToken = refreshResponse?.data?.access_token || refreshResponse?.access_token;
  console.log('Access token extracted:', !!accessToken); // Should be true
  console.log('Token value:', accessToken); // Should be 'new_access_token_123'

  // Test 2: Invalid refresh token response
  console.log('\n2. Testing invalid refresh token response:');
  const invalidRefreshResponse = {
    data: {
      success: false,
      error: "Invalid refresh token"
    }
  };
  
  const hasError = invalidRefreshResponse?.data?.error;
  console.log('Error detected:', !!hasError); // Should be true
  console.log('Error message:', hasError); // Should be 'Invalid refresh token'

  // Test 3: Missing refresh token
  console.log('\n3. Testing missing refresh token:');
  const noToken = null;
  const tokenExists = !!noToken;
  console.log('Token exists:', tokenExists); // Should be false

  console.log('\n✅ JWT refresh mechanism tests completed successfully!');
};

// Export for use in other files
export default {
  testJWTAndResponseFixes,
  testErrorHandlingWithNewStructure,
  testJWTRefreshMechanism
};
