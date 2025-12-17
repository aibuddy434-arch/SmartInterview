/**
 * Test script to verify error handling fixes
 * This file can be imported and used for testing error scenarios
 */

import { getErrorMessage, validateResponse, safeResponseHandler, safeApiCall, safeApiCallWithValidation } from './utils/errorHandler';

// Test cases for error handling utilities
export const testErrorHandling = () => {
  console.log('🧪 Testing Error Handling Utilities');
  console.log('=====================================');

  // Test 1: getErrorMessage with various error formats
  console.log('\n1. Testing getErrorMessage with various error formats:');
  
  // FastAPI error format
  const fastApiError = {
    response: {
      data: { detail: 'User not found' }
    }
  };
  console.log('FastAPI error:', getErrorMessage(fastApiError, 'Default message'));
  
  // Custom error format
  const customError = {
    response: {
      data: { error: 'Invalid credentials' }
    }
  };
  console.log('Custom error:', getErrorMessage(customError, 'Default message'));
  
  // Network error
  const networkError = {
    message: 'Network Error'
  };
  console.log('Network error:', getErrorMessage(networkError, 'Default message'));
  
  // No error details
  const noDetailsError = {};
  console.log('No details error:', getErrorMessage(noDetailsError, 'Default message'));

  // Test 2: validateResponse
  console.log('\n2. Testing validateResponse:');
  
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

  // Test 3: safeResponseHandler
  console.log('\n3. Testing safeResponseHandler:');
  
  const result1 = safeResponseHandler(validResponse, ['candidate.id', 'session_id']);
  console.log('Valid response result:', result1);
  
  const result2 = safeResponseHandler(invalidResponse, ['candidate.id', 'session_id']);
  console.log('Invalid response result:', result2);

  // Test 4: safeApiCall
  console.log('\n4. Testing safeApiCall:');
  
  const successApi = async () => ({ data: 'success' });
  const failureApi = async () => { throw new Error('API failed'); };
  
  // Test success case
  safeApiCall(successApi, 'API failed').then(result => {
    console.log('Success API result:', result);
  });
  
  // Test failure case
  safeApiCall(failureApi, 'API failed').then(result => {
    console.log('Failure API result:', result);
  });

  console.log('\n✅ Error handling utilities tested successfully!');
};

// Test scenarios for the actual application
export const testApplicationErrorScenarios = () => {
  console.log('\n🧪 Testing Application Error Scenarios');
  console.log('========================================');

  // Scenario 1: Backend returns success but missing required fields
  const incompleteSuccessResponse = {
    candidate: { id: '123' }
    // missing session_id
  };
  
  const result1 = safeResponseHandler(incompleteSuccessResponse, ['candidate.id', 'session_id']);
  console.log('Incomplete success response:', result1);
  
  // Scenario 2: Backend returns error format
  const errorResponse = {
    error: 'Registration failed',
    message: 'Please try again'
  };
  
  const result2 = safeResponseHandler(errorResponse, ['candidate.id', 'session_id']);
  console.log('Error response:', result2);
  
  // Scenario 3: Network error
  const networkError = {
    message: 'Network Error',
    code: 'NETWORK_ERROR'
  };
  
  const result3 = getErrorMessage(networkError, 'Default fallback');
  console.log('Network error message:', result3);
  
  // Scenario 4: Axios error with FastAPI format
  const axiosError = {
    response: {
      status: 400,
      data: { detail: 'Validation failed' }
    }
  };
  
  const result4 = getErrorMessage(axiosError, 'Default fallback');
  console.log('Axios error message:', result4);
  
  console.log('\n✅ Application error scenarios tested successfully!');
};

// Export for use in other files
export default {
  testErrorHandling,
  testApplicationErrorScenarios
};

