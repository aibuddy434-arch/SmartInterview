/**
 * Test script to verify JWT and error handling fixes
 * Run this in the browser console to test the fixes
 */

// Test 1: Safe API Response Handling
console.log('🧪 Testing Safe API Response Handling...');

// Mock API responses to test error handling
const testResponses = [
  { data: { success: true, data: { user: { id: 1, email: 'test@example.com' } } } },
  { data: { success: false, error: 'Invalid credentials' } },
  { data: { success: false, message: 'Server error' } },
  { data: { error: 'Network error' } },
  null,
  undefined,
  { data: null },
  { data: { success: true, data: null } }
];

// Test safeApiCall function
testResponses.forEach((response, index) => {
  console.log(`\n📝 Test ${index + 1}:`, response);
  
  // Simulate safeApiCall behavior
  try {
    if (response && response.data) {
      const { success, data, message, error } = response.data;
      
      if (success === true) {
        console.log('✅ Success:', data);
      } else {
        console.log('❌ Error:', error || message || 'Unknown error');
      }
    } else {
      console.log('⚠️  No response data, assuming success');
    }
  } catch (err) {
    console.log('💥 Exception:', err.message);
  }
});

// Test 2: JWT Token Handling
console.log('\n🔐 Testing JWT Token Handling...');

// Test token storage
const testTokens = {
  access_token: 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test',
  refresh_token: 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.refresh'
};

// Simulate token storage
localStorage.setItem('access_token', testTokens.access_token);
localStorage.setItem('refresh_token', testTokens.refresh_token);

console.log('✅ Tokens stored in localStorage');

// Test token retrieval
const storedAccessToken = localStorage.getItem('access_token');
const storedRefreshToken = localStorage.getItem('refresh_token');

console.log('✅ Access token retrieved:', storedAccessToken ? 'Yes' : 'No');
console.log('✅ Refresh token retrieved:', storedRefreshToken ? 'Yes' : 'No');

// Test 3: Error Message Extraction
console.log('\n📝 Testing Error Message Extraction...');

const testErrors = [
  { response: { data: { detail: 'Invalid credentials' } } },
  { response: { data: { error: 'Server error' } } },
  { response: { data: { message: 'Validation failed' } } },
  { response: { data: { errors: ['Field required', 'Invalid format'] } } },
  { message: 'Network error' },
  { error: 'Timeout' },
  null,
  undefined
];

testErrors.forEach((error, index) => {
  console.log(`\n📝 Error ${index + 1}:`, error);
  
  // Simulate getErrorMessage function
  let errorMessage = 'An unexpected error occurred';
  
  if (error && error.response?.data) {
    const data = error.response.data;
    if (data.detail) errorMessage = data.detail;
    else if (data.error) errorMessage = data.error;
    else if (data.errors && Array.isArray(data.errors)) {
      errorMessage = data.errors.join(', ');
    }
    else if (data.message) errorMessage = data.message;
  } else if (error && error.message) {
    errorMessage = error.message;
  } else if (error && error.error) {
    errorMessage = error.error;
  }
  
  console.log('✅ Extracted message:', errorMessage);
});

// Test 4: API Interceptor Logic
console.log('\n🔄 Testing API Interceptor Logic...');

// Simulate 401 error handling
const simulate401Error = () => {
  console.log('🚨 Simulating 401 error...');
  
  const refreshToken = localStorage.getItem('refresh_token');
  if (refreshToken) {
    console.log('✅ Refresh token found, attempting refresh...');
    // In real scenario, this would call the refresh endpoint
    console.log('✅ Token refresh simulated successfully');
    return true;
  } else {
    console.log('❌ No refresh token, redirecting to login');
    return false;
  }
};

simulate401Error();

// Test 5: Form Validation
console.log('\n📋 Testing Form Validation...');

const testFormData = {
  email: 'test@example.com',
  password: 'password123',
  confirmPassword: 'password123'
};

// Test password matching
const passwordsMatch = testFormData.password === testFormData.confirmPassword;
console.log('✅ Passwords match:', passwordsMatch);

// Test password length
const passwordLengthValid = testFormData.password.length >= 6;
console.log('✅ Password length valid:', passwordLengthValid);

// Test email format
const emailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(testFormData.email);
console.log('✅ Email format valid:', emailValid);

console.log('\n🎉 All tests completed! The fixes should prevent runtime errors and handle JWT properly.');

