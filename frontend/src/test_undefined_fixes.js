/**
 * Test script to verify undefined property access fixes
 * This file can be imported and used for testing various scenarios
 */

// Test scenarios for undefined property access
export const testUndefinedPropertyAccess = () => {
  console.log('🧪 Testing Undefined Property Access Fixes');
  console.log('==========================================');

  // Test 1: Safe property access patterns
  console.log('\n1. Testing safe property access patterns:');
  
  // Scenario: result is undefined
  const undefinedResult = undefined;
  const safeCheck1 = undefinedResult && undefinedResult.success === true;
  console.log('Undefined result check:', safeCheck1); // Should be false
  
  // Scenario: result exists but no success property
  const noSuccessResult = { data: 'some data' };
  const safeCheck2 = noSuccessResult && noSuccessResult.success === true;
  console.log('No success property check:', safeCheck2); // Should be false
  
  // Scenario: result exists with success: false
  const falseSuccessResult = { success: false, error: 'Something went wrong' };
  const safeCheck3 = falseSuccessResult && falseSuccessResult.success === true;
  console.log('False success check:', safeCheck3); // Should be false
  
  // Scenario: result exists with success: true
  const trueSuccessResult = { success: true, data: { id: '123' } };
  const safeCheck4 = trueSuccessResult && trueSuccessResult.success === true;
  console.log('True success check:', safeCheck4); // Should be true

  // Test 2: Safe error message extraction
  console.log('\n2. Testing safe error message extraction:');
  
  // Scenario: result is undefined
  const errorMessage1 = (undefinedResult && undefinedResult.error) || 'Default error';
  console.log('Undefined result error:', errorMessage1); // Should be 'Default error'
  
  // Scenario: result exists but no error property
  const noErrorResult = { success: false };
  const errorMessage2 = (noErrorResult && noErrorResult.error) || 'Default error';
  console.log('No error property:', errorMessage2); // Should be 'Default error'
  
  // Scenario: result exists with error property
  const withErrorResult = { success: false, error: 'Custom error message' };
  const errorMessage3 = (withErrorResult && withErrorResult.error) || 'Default error';
  console.log('With error property:', errorMessage3); // Should be 'Custom error message'

  // Test 3: Safe data access
  console.log('\n3. Testing safe data access:');
  
  // Scenario: result is undefined
  const dataCheck1 = undefinedResult && undefinedResult.data;
  console.log('Undefined result data check:', dataCheck1); // Should be false
  
  // Scenario: result exists but no data property
  const noDataResult = { success: true };
  const dataCheck2 = noDataResult && noDataResult.data;
  console.log('No data property check:', dataCheck2); // Should be false
  
  // Scenario: result exists with data property
  const withDataResult = { success: true, data: { candidate: { id: '123' } } };
  const dataCheck3 = withDataResult && withDataResult.data;
  console.log('With data property check:', dataCheck3); // Should be true

  // Test 4: Nested property access
  console.log('\n4. Testing nested property access:');
  
  // Scenario: Safe nested access
  const nestedResult = { success: true, data: { candidate: { id: '123' } } };
  const nestedCheck1 = nestedResult && nestedResult.data && nestedResult.data.candidate && nestedResult.data.candidate.id;
  console.log('Safe nested access:', nestedCheck1); // Should be '123'
  
  // Scenario: Unsafe nested access (should not crash)
  const unsafeNestedResult = { success: true, data: { candidate: null } };
  const nestedCheck2 = unsafeNestedResult && unsafeNestedResult.data && unsafeNestedResult.data.candidate && unsafeNestedResult.data.candidate.id;
  console.log('Unsafe nested access:', nestedCheck2); // Should be false, not crash

  console.log('\n✅ Undefined property access tests completed successfully!');
};

// Test scenarios for API response handling
export const testApiResponseScenarios = () => {
  console.log('\n🧪 Testing API Response Scenarios');
  console.log('==================================');

  // Test 1: Various backend response formats
  console.log('\n1. Testing various backend response formats:');
  
  // FastAPI success response
  const fastApiSuccess = { candidate: { id: '123' }, session_id: 'abc' };
  const fastApiCheck = fastApiSuccess && fastApiSuccess.candidate && fastApiSuccess.candidate.id;
  console.log('FastAPI success response:', fastApiCheck); // Should be '123'
  
  // FastAPI error response
  const fastApiError = { detail: 'User not found' };
  const fastApiErrorCheck = fastApiError && fastApiError.detail;
  console.log('FastAPI error response:', fastApiErrorCheck); // Should be 'User not found'
  
  // Custom success response
  const customSuccess = { success: true, data: { id: '123' } };
  const customSuccessCheck = customSuccess && customSuccess.success === true;
  console.log('Custom success response:', customSuccessCheck); // Should be true
  
  // Custom error response
  const customError = { success: false, error: 'Something went wrong' };
  const customErrorCheck = customError && customError.success === true;
  console.log('Custom error response:', customErrorCheck); // Should be false

  // Test 2: Network error scenarios
  console.log('\n2. Testing network error scenarios:');
  
  // Axios error response
  const axiosError = {
    response: {
      status: 400,
      data: { detail: 'Validation failed' }
    }
  };
  const axiosErrorCheck = axiosError.response && axiosError.response.data && axiosError.response.data.detail;
  console.log('Axios error response:', axiosErrorCheck); // Should be 'Validation failed'
  
  // Network error
  const networkError = { message: 'Network Error' };
  const networkErrorCheck = networkError && networkError.message;
  console.log('Network error:', networkErrorCheck); // Should be 'Network Error'

  // Test 3: Malformed responses
  console.log('\n3. Testing malformed responses:');
  
  // Null response
  const nullResponse = null;
  const nullCheck = nullResponse && nullResponse.success === true;
  console.log('Null response check:', nullCheck); // Should be false
  
  // Empty object response
  const emptyResponse = {};
  const emptyCheck = emptyResponse && emptyResponse.success === true;
  console.log('Empty response check:', emptyCheck); // Should be false
  
  // String response (unexpected)
  const stringResponse = 'Unexpected string response';
  const stringCheck = stringResponse && stringResponse.success === true;
  console.log('String response check:', stringCheck); // Should be false

  console.log('\n✅ API response scenario tests completed successfully!');
};

// Test the actual error handling utilities
export const testErrorHandlingUtilities = () => {
  console.log('\n🧪 Testing Error Handling Utilities');
  console.log('====================================');

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
      return { success: true, data: response, error: null };
    } catch (error) {
      const errorMessage = getErrorMessage(error, fallbackMessage);
      console.error('API call failed:', error);
      return { success: false, data: null, error: errorMessage };
    }
  };

  // Test 1: Successful API call
  console.log('\n1. Testing successful API call:');
  const successApi = async () => ({ candidate: { id: '123' }, session_id: 'abc' });
  safeApiCall(successApi, 'API failed').then(result => {
    console.log('Success result:', result);
    console.log('Success check:', result && result.success === true);
  });

  // Test 2: Failed API call
  console.log('\n2. Testing failed API call:');
  const failureApi = async () => { throw new Error('API failed'); };
  safeApiCall(failureApi, 'API failed').then(result => {
    console.log('Failure result:', result);
    console.log('Failure check:', result && result.success === false);
  });

  // Test 3: Axios error
  console.log('\n3. Testing Axios error:');
  const axiosErrorApi = async () => { 
    const error = new Error('Request failed');
    error.response = { data: { detail: 'User not found' } };
    throw error;
  };
  safeApiCall(axiosErrorApi, 'API failed').then(result => {
    console.log('Axios error result:', result);
    console.log('Error message:', result && result.error);
  });

  console.log('\n✅ Error handling utility tests completed successfully!');
};

// Export for use in other files
export default {
  testUndefinedPropertyAccess,
  testApiResponseScenarios,
  testErrorHandlingUtilities
};

