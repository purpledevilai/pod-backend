export interface ApiResponse<T = any> {
  status: number;
  data: T;
  headers: Headers;
}

export class TestError extends Error {
  constructor(
    message: string,
    public status?: number,
    public response?: any
  ) {
    super(message);
    this.name = 'TestError';
  }
}

export async function makeApiRequest<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  const apiUrl = process.env.API_URL;
  const url = `${apiUrl}${endpoint}`;
  
  const defaultOptions: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, defaultOptions);
    const data = await response.json();
    
    return {
      status: response.status,
      data: data as T,
      headers: response.headers,
    };
  } catch (error) {
    throw new TestError(
      `Request failed: ${error instanceof Error ? error.message : 'Unknown error'}`,
      undefined,
      error
    );
  }
}

export function expectSuccessResponse(response: ApiResponse, expectedStatus = 200) {
  if (response.status !== expectedStatus) {
    throw new TestError(
      `Expected status ${expectedStatus}, got ${response.status}`,
      response.status,
      response.data
    );
  }
  
  if (response.data.error) {
    throw new TestError(
      `API returned error: ${response.data.error}`,
      response.status,
      response.data
    );
  }
}

export function expectErrorResponse(response: ApiResponse, expectedStatus: number) {
  if (response.status !== expectedStatus) {
    throw new TestError(
      `Expected error status ${expectedStatus}, got ${response.status}`,
      response.status,
      response.data
    );
  }
}

export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export function generateTestEmail(): string {
  const timestamp = Date.now();
  return `test-${timestamp}@example.com`;
}
