import { makeApiRequest, expectSuccessResponse, expectErrorResponse } from '../utils/test-helpers';

describe('GET /user', () => {
  test('should reject request without authentication token', async () => {
    const response = await makeApiRequest('/user', {
      method: 'GET'
    });

    expectErrorResponse(response, 500);
    expect(response.data).toHaveProperty('error');
    expect(response.data.error).toContain('authentication');
  });

  test('should reject request with invalid token', async () => {
    const response = await makeApiRequest('/user', {
      method: 'GET',
      headers: {
        'Authorization': 'Bearer invalid-token-here'
      }
    });

    expectErrorResponse(response, 500);
    expect(response.data).toHaveProperty('error');
  });

  test('should reject request with malformed token', async () => {
    const response = await makeApiRequest('/user', {
      method: 'GET',
      headers: {
        'Authorization': 'Bearer not.a.valid.jwt.token'
      }
    });

    expectErrorResponse(response, 500);
    expect(response.data).toHaveProperty('error');
  });

  test('should reject request with refresh token instead of access token', async () => {
    // Mock refresh token (would need a valid one in real test)
    const mockRefreshToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMTIzIiwidG9rZW5fdHlwZSI6InJlZnJlc2hfdG9rZW4ifQ.invalid';
    
    const response = await makeApiRequest('/user', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${mockRefreshToken}`
      }
    });

    expectErrorResponse(response, 500);
    expect(response.data).toHaveProperty('error');
  });

  // Note: Testing successful user retrieval would require:
  // 1. Creating a test user account
  // 2. Getting a valid access token
  // 3. Using that token to fetch the user
  // This would typically be done in integration tests with proper setup
  
  test('should return user with resolved council and bin_system when authenticated', async () => {
    // This test requires a valid access token
    // In a real test environment, you would:
    // 1. Create a test user via /create-account
    // 2. Verify email and get access token
    // 3. Use that token here
    
    const validAccessToken = process.env.TEST_ACCESS_TOKEN;
    
    if (!validAccessToken) {
      console.log('⚠️  Skipping test: TEST_ACCESS_TOKEN not set in environment');
      return;
    }
    
    const response = await makeApiRequest('/user', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${validAccessToken}`
      }
    });

    expectSuccessResponse(response);
    
    // Verify response structure
    expect(response.data).toHaveProperty('id');
    expect(response.data).toHaveProperty('email');
    expect(response.data).toHaveProperty('council');
    expect(response.data).toHaveProperty('bin_system');
    expect(response.data).toHaveProperty('points');
    expect(response.data).toHaveProperty('created_at');
    expect(response.data).toHaveProperty('updated_at');
    
    // Verify council is resolved
    expect(response.data.council).toHaveProperty('id');
    expect(response.data.council).toHaveProperty('name');
    expect(response.data.council).toHaveProperty('mapId');
    
    // Verify bin_system is resolved
    expect(response.data.bin_system).toHaveProperty('id');
    expect(response.data.bin_system).toHaveProperty('bins');
    expect(Array.isArray(response.data.bin_system.bins)).toBe(true);
  });
});
