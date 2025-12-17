/**
 * Debug script to test registration error handling
 * Run this in the browser console to test the fixes
 */

console.log('🔍 Debugging Registration Error Handling...\n');

// Test 1: Test safeApiCallWithValidation with various scenarios
console.log('📝 Test 1: Testing safeApiCallWithValidation scenarios');
console.log('====================================================');

// Mock the safeApiCallWithValidation function behavior
const testSafeApiCall = (response, requiredFields = [], fallbackMessage = 'Request failed') => {
  try {
    // Handle standardized backend response structure
    if (response && response.data) {
      const { success, data, message, error } = response.data;
      
      if (success === true) {
        // Validate required fields in the data
        if (data && typeof data === 'object') {
          // Simple validation for required fields
          const isValid = requiredFields.every(field => {
            const fieldPath = field.split('.');
            let current = data;
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
            return { success: true, data: data, error: null };
          } else {
            return { success: false, data: null, error: fallbackMessage };
          }
        } else {
          return { success: false, data: null, error: 'Invalid data structure received from server' };
        }
      } else {
        return { success: false, data: null, error: error || message || fallbackMessage };
      }
    }
    
    // Fallback for non-standardized responses
    return { success: false, data: null, error: fallbackMessage };
  } catch (error) {
    console.error('API call failed:', error);
    return { success: false, data: null, error: fallbackMessage };
  }
};

// Test scenarios that could cause the TypeError
const testScenarios = [
  {
    name: 'Valid Success Response',
    response: { 
      data: { 
        success: true, 
        data: { 
          candidate: { id: 1 }, 
          session_id: 'abc123' 
        } 
      } 
    },
    expected: 'Should return success with data'
  },
  {
    name: 'Response with Error',
    response: { 
      data: { 
        success: false, 
        error: 'Registration failed' 
      } 
    },
    expected: 'Should return error message'
  },
  {
    name: 'Response with Undefined Data',
    response: { 
      data: { 
        success: true, 
        data: undefined 
      } 
    },
    expected: 'Should handle undefined data safely'
  },
  {
    name: 'Response with Null Data',
    response: { 
      data: { 
        success: true, 
        data: null 
      } 
    },
    expected: 'Should handle null data safely'
  },
  {
    name: 'Completely Undefined Response',
    response: undefined,
    expected: 'Should handle undefined response safely'
  },
  {
    name: 'Response without Data Property',
    response: { status: 200 },
    expected: 'Should handle missing data property safely'
  }
];

testScenarios.forEach((scenario, index) => {
  console.log(`\n${index + 1}. ${scenario.name}:`);
  console.log('   Input:', scenario.response);
  
  try {
    const result = testSafeApiCall(scenario.response, ['candidate.id', 'session_id'], 'Registration failed');
    console.log('   Result:', result);
    
    // Test the safe property access that was causing the error
    if (result && typeof result === 'object' && result.success === true && result.data) {
      console.log('   ✅ Success: Registration would proceed');
    } else {
      let errorMessage = 'Registration failed. Please try again.';
      if (result && typeof result === 'object') {
        if (result.error && typeof result.error === 'string') {
          errorMessage = result.error;
        } else if (result.message && typeof result.message === 'string') {
          errorMessage = result.message;
        }
      }
      console.log('   ✅ Error handled safely:', errorMessage);
    }
  } catch (error) {
    console.log('   ❌ Error:', error.message);
  }
  
  console.log('   Expected:', scenario.expected);
});

// Test 2: Test the specific error handling pattern from handleCandidateRegistration
console.log('\n\n📝 Test 2: Testing handleCandidateRegistration error handling pattern');
console.log('==================================================================');

const testHandleCandidateRegistration = (result) => {
  console.log('Testing with result:', result);
  
  try {
    // This is the exact pattern from the fixed handleCandidateRegistration function
    if (result && typeof result === 'object' && result.success === true && result.data) {
      // Additional safety check for nested data
      if (result.data.candidate && result.data.candidate.id && result.data.session_id) {
        console.log('✅ Registration would succeed');
        return { success: true, message: 'Registration successful' };
      } else {
        console.log('❌ Invalid data structure in registration response');
        return { success: false, message: 'Registration completed but received invalid data' };
      }
    } else {
      // Safe error message extraction with additional checks
      let errorMessage = 'Registration failed. Please try again.';
      
      if (result && typeof result === 'object') {
        if (result.error && typeof result.error === 'string') {
          errorMessage = result.error;
        } else if (result.message && typeof result.message === 'string') {
          errorMessage = result.message;
        }
      }
      
      console.log('❌ Registration failed:', errorMessage);
      return { success: false, message: errorMessage };
    }
  } catch (error) {
    console.log('💥 Exception caught:', error.message);
    return { success: false, message: 'Something went wrong. Please try again.' };
  }
};

// Test the error handling pattern
const testResults = [
  { success: true, data: { candidate: { id: 1 }, session_id: 'abc123' } },
  { success: false, error: 'Email already exists' },
  { success: false, message: 'Invalid phone number' },
  undefined,
  null,
  { success: true, data: null },
  { success: true, data: { candidate: null, session_id: 'abc123' } }
];

testResults.forEach((result, index) => {
  console.log(`\nTest ${index + 1}:`);
  const testResult = testHandleCandidateRegistration(result);
  console.log('   Result:', testResult);
});

console.log('\n🎉 Debug tests completed!');
console.log('\n📋 If you still see the TypeError, check:');
console.log('1. Make sure the changes were saved and the app was restarted');
console.log('2. Check the browser console for the debug log "Registration result:"');
console.log('3. Verify that safeApiCallWithValidation is being imported correctly');
console.log('4. Check if there are any other places in the code accessing result.error directly');

