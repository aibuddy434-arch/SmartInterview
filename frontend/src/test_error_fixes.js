/**
 * Test script to verify error handling fixes
 * This file tests the enhanced error handling utilities
 */

import { 
  getErrorMessage, 
  validateResponse, 
  safeResponseHandler, 
  safeApiCall, 
  safeApiCallWithValidation,
  handleApiError,
  safeGet,
  resilientApiCall
} from './utils/errorHandler';

// Test the error handling utilities
export const testErrorFixes = () => {
  console.log('🧪 Testing Enhanced Error Handling Fixes');
  console.log('==========================================');

  // Test 1: safeGet utility
  console.log('\n1. Testing safeGet utility:');
  
  const testObj = {
    user: {
      profile: {
        name: 'John Doe',
        email: 'john@example.com'
      }
    },
    settings: {
      theme: 'dark'
    }
  };
  
  console.log('Safe access to existing property:', safeGet(testObj, 'user.profile.name', 'Default'));
  console.log('Safe access to non-existing property:', safeGet(testObj, 'user.profile.age', 'Default'));
  console.log('Safe access to undefined object:', safeGet(null, 'user.profile.name', 'Default'));
  console.log('Safe access to invalid path:', safeGet(testObj, 'invalid.path', 'Default'));

  // Test 2: handleApiError utility
  console.log('\n2. Testing handleApiError utility:');
  
  const axiosError = {
    response: {
      data: {
        detail: 'User not found'
      }
    }
  };
  console.log('Axios error:', handleApiError(axiosError, 'Default message'));
  
  const networkError = {
    code: 'NETWORK_ERROR',
    message: 'Network Error'
  };
  console.log('Network error:', handleApiError(networkError, 'Default message'));
  
  const timeoutError = {
    code: 'ECONNABORTED',
    message: 'timeout'
  };
  console.log('Timeout error:', handleApiError(timeoutError, 'Default message'));
  
  const genericError = {
    message: 'Something went wrong'
  };
  console.log('Generic error:', handleApiError(genericError, 'Default message'));

  // Test 3: validateResponse with edge cases
  console.log('\n3. Testing validateResponse with edge cases:');
  
  const validResponse = {
    candidate: { id: '123' },
    session_id: 'abc',
    message: 'Success'
  };
  console.log('Valid response:', validateResponse(validResponse, ['candidate.id', 'session_id']));
  
  const invalidResponse = {
    candidate: { id: '123' }
    // missing session_id
  };
  console.log('Invalid response:', validateResponse(invalidResponse, ['candidate.id', 'session_id']));
  
  const nullResponse = null;
  console.log('Null response:', validateResponse(nullResponse, ['candidate.id', 'session_id']));
  
  const undefinedResponse = undefined;
  console.log('Undefined response:', validateResponse(undefinedResponse, ['candidate.id', 'session_id']));

  // Test 4: safeApiCallWithValidation with undefined response
  console.log('\n4. Testing safeApiCallWithValidation with undefined response:');
  
  const mockApiCall = async () => {
    return undefined; // Simulate undefined response
  };
  
  safeApiCallWithValidation(mockApiCall, ['candidate.id', 'session_id'], 'Test failed')
    .then(result => {
      console.log('Undefined response result:', result);
    })
    .catch(error => {
      console.log('Undefined response error:', error);
    });

  // Test 5: safeApiCallWithValidation with null response
  console.log('\n5. Testing safeApiCallWithValidation with null response:');
  
  const mockApiCallNull = async () => {
    return null; // Simulate null response
  };
  
  safeApiCallWithValidation(mockApiCallNull, ['candidate.id', 'session_id'], 'Test failed')
    .then(result => {
      console.log('Null response result:', result);
    })
    .catch(error => {
      console.log('Null response error:', error);
    });

  // Test 6: safeApiCallWithValidation with error response
  console.log('\n6. Testing safeApiCallWithValidation with error response:');
  
  const mockApiCallError = async () => {
    return {
      data: {
        success: false,
        error: 'Test error message'
      }
    };
  };
  
  safeApiCallWithValidation(mockApiCallError, ['candidate.id', 'session_id'], 'Test failed')
    .then(result => {
      console.log('Error response result:', result);
    })
    .catch(error => {
      console.log('Error response error:', error);
    });

  // Test 7: safeApiCallWithValidation with successful response
  console.log('\n7. Testing safeApiCallWithValidation with successful response:');
  
  const mockApiCallSuccess = async () => {
    return {
      data: {
        success: true,
        data: {
          candidate: { id: '123' },
          session_id: 'abc'
        }
      }
    };
  };
  
  safeApiCallWithValidation(mockApiCallSuccess, ['candidate.id', 'session_id'], 'Test failed')
    .then(result => {
      console.log('Success response result:', result);
    })
    .catch(error => {
      console.log('Success response error:', error);
    });

  console.log('\n✅ All error handling tests completed!');
};

// Test the specific error scenario that was causing issues
export const testRegistrationErrorScenario = () => {
  console.log('\n🔍 Testing Registration Error Scenario');
  console.log('=====================================');
  
  // Simulate the exact error scenario
  const simulateRegistrationError = async () => {
    try {
      // This would be the result from safeApiCallWithValidation
      const result = undefined; // This is what was causing the error
      
      console.log('Registration result:', result);
      
      // This is the fixed error handling
      if (result && typeof result === 'object' && result.success === true && result.data) {
        console.log('✅ Registration would succeed');
        return { success: true, message: 'Registration successful' };
      } else {
        // Safe error message extraction with comprehensive checks
        let errorMessage = 'Registration failed. Please try again.';
        
        if (result && typeof result === 'object') {
          // Use safe property access
          errorMessage = safeGet(result, 'error') || 
                       safeGet(result, 'message') || 
                       safeGet(result, 'data') || 
                       errorMessage;
        } else if (result && typeof result === 'string') {
          errorMessage = result;
        } else if (!result) {
          errorMessage = 'No response received from server. Please try again.';
        }
        
        console.log('❌ Registration failed:', errorMessage);
        return { success: false, message: errorMessage };
      }
    } catch (error) {
      console.log('💥 Exception caught:', error.message);
      return { success: false, message: 'Something went wrong. Please try again.' };
    }
  };
  
  simulateRegistrationError().then(result => {
    console.log('Final result:', result);
  });
};

// Run the tests
if (typeof window !== 'undefined') {
  // Browser environment
  window.testErrorFixes = testErrorFixes;
  window.testRegistrationErrorScenario = testRegistrationErrorScenario;
  console.log('Error handling tests loaded. Run testErrorFixes() or testRegistrationErrorScenario() to test.');
} else {
  // Node.js environment
  testErrorFixes();
  testRegistrationErrorScenario();
}














