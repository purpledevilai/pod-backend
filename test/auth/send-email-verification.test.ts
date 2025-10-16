import { makeApiRequest, expectSuccessResponse, expectErrorResponse, generateTestEmail } from '../utils/test-helpers';

describe('Send Email Verification', () => {
  test('should send verification email successfully', async () => {
    
    const response = await makeApiRequest('/send-email-verification', {
      method: 'POST',
      body: JSON.stringify({
        email: "keanu.interone@gmail.com"
      })
    });

    console.log(response);


    expectSuccessResponse(response);
    expect(response.data).toHaveProperty('challenge_id');
    expect(typeof response.data.challenge_id).toBe('string');
    expect(response.data.challenge_id.length).toBeGreaterThan(0);
  });

  test('should reject invalid email format', async () => {
    const response = await makeApiRequest('/send-email-verification', {
      method: 'POST',
      body: JSON.stringify({
        email: 'invalid-email'
      })
    });

    expectErrorResponse(response, 500);
    expect(response.data).toHaveProperty('error');
  });

  test('should reject empty email', async () => {
    const response = await makeApiRequest('/send-email-verification', {
      method: 'POST',
      body: JSON.stringify({
        email: ''
      })
    });

    expectErrorResponse(response, 500);
    expect(response.data).toHaveProperty('error');
  });

  test('should reject missing email field', async () => {
    const response = await makeApiRequest('/send-email-verification', {
      method: 'POST',
      body: JSON.stringify({})
    });

    expectErrorResponse(response, 500);
    expect(response.data).toHaveProperty('error');
  });

  test('should reject malformed JSON', async () => {
    const response = await makeApiRequest('/send-email-verification', {
      method: 'POST',
      body: 'invalid json'
    });

    expectErrorResponse(response, 500);
    expect(response.data).toHaveProperty('error');
  });
});
