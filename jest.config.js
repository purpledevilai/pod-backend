module.exports = {
  testEnvironment: 'node',
  roots: ['<rootDir>/test'],
  testMatch: ['**/*.test.ts'],
  transform: {
    '^.+\\.tsx?$': 'ts-jest'
  },
  setupFilesAfterEnv: ['<rootDir>/test/setup.ts'],
  testTimeout: 30000,
  verbose: true,
  // Explicitly disable watch mode
  watchman: false,
  // Disable any file watching
  watchPathIgnorePatterns: ['<rootDir>/node_modules/', '<rootDir>/cdk.out/', '<rootDir>/test/'],
  // Ensure no automatic test running
  collectCoverage: false,
  passWithNoTests: true
};
