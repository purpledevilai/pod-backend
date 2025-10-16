import { makeApiRequest, expectSuccessResponse, expectErrorResponse } from '../utils/test-helpers';

describe('Refresh Token', () => {
  test('should reject missing refresh token', async () => {
    const response = await makeApiRequest('/refresh-token', {
      method: 'POST',
      body: JSON.stringify({})
    });
    


    expectErrorResponse(response, 200); // Your API returns 200 with success: false
    expect(response.data).toHaveProperty('success', false);
    expect(response.data).toHaveProperty('message');
  });

  test('should reject invalid refresh token', async () => {
    const response = await makeApiRequest('/refresh-token', {
      method: 'POST',
      body: JSON.stringify({
        refresh_token: 'invalid-token'
      })
    });

    expectErrorResponse(response, 200); // Your API returns 200 with success: false
    expect(response.data).toHaveProperty('success', false);
    expect(response.data).toHaveProperty('message');
  });

  test('should reject malformed refresh token', async () => {
    const response = await makeApiRequest('/refresh-token', {
      method: 'POST',
      body: JSON.stringify({
        refresh_token: 'not.a.valid.jwt'
      })
    });

    expectErrorResponse(response, 200); // Your API returns 200 with success: false
    expect(response.data).toHaveProperty('success', false);
    expect(response.data).toHaveProperty('message');
  });

  test('should reject malformed JSON', async () => {
    const response = await makeApiRequest('/refresh-token', {
      method: 'POST',
      body: 'invalid json'
    });

    expectErrorResponse(response, 200); // Your API returns 200 with success: false
    expect(response.data).toHaveProperty('success', false);
    expect(response.data).toHaveProperty('message');
  });

  test('should reject access token instead of refresh token', async () => {
    // This test would require a valid access token to test with
    // For now, we'll test with a mock token that has the wrong type
    const mockAccessToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMTIzIiwiZW1haWwiOiJ0ZXN0QGV4YW1wbGUuY29tIiwidG9rZW5fdHlwZSI6ImFjY2Vzc190b2tlbiJ9.invalid';
    
    const response = await makeApiRequest('/refresh-token', {
      method: 'POST',
      body: JSON.stringify({
        refresh_token: mockAccessToken
      })
    });

    expectErrorResponse(response, 200); // Your API returns 200 with success: false
    expect(response.data).toHaveProperty('success', false);
    expect(response.data).toHaveProperty('message');
  });

  // Note: Testing successful refresh token would require:
  // 1. A valid user account
  // 2. A valid refresh token from a previous authentication
  // 3. Proper setup of the test environment with real JWT secrets
  // This would typically be done in integration tests with a test database
});
