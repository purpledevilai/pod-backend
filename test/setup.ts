// Global test setup
import * as dotenv from 'dotenv';
import * as path from 'path';

// Load environment variables from test/.env file
const envPath = path.resolve(__dirname, '.env');
dotenv.config({ path: envPath });

// Set up global test configuration
beforeAll(() => {
  console.log('Starting API tests...');
  console.log(`API URL: ${process.env.API_URL}`);
  console.log(`Test Email: ${process.env.TEST_EMAIL}`);
});

afterAll(() => {
  console.log('API tests completed.');
});

// Global error handler for unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

// Increase timeout for all tests
jest.setTimeout(30000);
