const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

class ApiClient {
  private baseUrl: string;
  private accessToken: string | null = null;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
    this.loadTokenFromStorage();
  }

  private loadTokenFromStorage() {
    if (typeof window !== 'undefined') {
      this.accessToken = localStorage.getItem('access_token');
    }
  }

  setAccessToken(token: string) {
    this.accessToken = token;
    localStorage.setItem('access_token', token);
  }

  setRefreshToken(token: string) {
    localStorage.setItem('refresh_token', token);
  }

  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.accessToken) {
      headers['Authorization'] = `Bearer ${this.accessToken}`;
    }

    return headers;
  }

  async request<T>(
    method: string,
    path: string,
    data?: unknown,
  ): Promise<ApiResponse<T>> {
    try {
      const options: RequestInit = {
        method,
        headers: this.getHeaders(),
      };

      if (data) {
        options.body = JSON.stringify(data);
      }

      const response = await fetch(`${this.baseUrl}${path}`, options);

      if (response.status === 401) {
        // Token expired — try refresh
        const refreshed = await this.refreshToken();
        if (!refreshed) {
          // Refresh failed — redirect to login
          if (typeof window !== 'undefined') {
            window.location.href = '/login';
          }
          return { status: 401, error: 'Unauthorized' };
        }

        // Retry original request
        options.headers = this.getHeaders();
        const retryResponse = await fetch(`${this.baseUrl}${path}`, options);
        return { status: retryResponse.status, data: await retryResponse.json() };
      }

      const result = await response.json();

      return {
        status: response.status,
        data: response.ok ? result : undefined,
        error: response.ok ? undefined : result.detail || 'Request failed',
      };
    } catch (error) {
      return {
        status: 0,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  async get<T>(path: string): Promise<ApiResponse<T>> {
    return this.request('GET', path);
  }

  async post<T>(path: string, data?: unknown): Promise<ApiResponse<T>> {
    return this.request('POST', path, data);
  }

  async put<T>(path: string, data?: unknown): Promise<ApiResponse<T>> {
    return this.request('PUT', path, data);
  }

  async delete<T>(path: string): Promise<ApiResponse<T>> {
    return this.request('DELETE', path);
  }

  private async refreshToken(): Promise<boolean> {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) return false;

      const response = await fetch(`${this.baseUrl}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (!response.ok) return false;

      const { access_token, refresh_token: newRefreshToken } = await response.json();
      this.setAccessToken(access_token);
      this.setRefreshToken(newRefreshToken);

      return true;
    } catch {
      return false;
    }
  }
}

export const api = new ApiClient();
