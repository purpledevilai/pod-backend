# API End-to-End Tests

Simple end-to-end tests for the ReBin API.

## Setup

1. Create a `.env` file in the test directory:
```bash
cd test
cp .env.example .env
# Edit .env with your actual API URL and test email
```

2. Required environment variables:
```
API_URL=https://your-api-gateway-url.amazonaws.com/prod
TEST_EMAIL=your-test-email@example.com
```

## Running Tests

```bash
# Run all tests
npm test

# Run specific test file
npm test -- send-email-verification.test.ts
```

## Test Structure

- `auth/` - Authentication endpoint tests
  - `send-email-verification.test.ts` - Email verification tests
  - `verify-email.test.ts` - Email verification code tests
  - `refresh-token.test.ts` - Token refresh tests
  - `get-user.test.ts` - Authenticated user retrieval tests
  - `auth-integration.test.ts` - Full authentication flow tests
- `utils/test-helpers.ts` - Common test utilities
- `setup.ts` - Global test setup (loads .env file)

## Notes

- Tests make real HTTP requests to your deployed API
- Tests do NOT run automatically on file changes
- Use `npm test -- --watch` if you want watch mode
