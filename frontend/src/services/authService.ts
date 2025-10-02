import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  full_name?: string;
  role?: 'viewer' | 'hiring_manager' | 'recruiter' | 'admin';
}

export interface User {
  id: string;
  username: string;
  email: string;
  full_name?: string;
  role: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
  last_login?: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

class AuthService {
  private accessToken: string | null = null;
  private refreshToken: string | null = null;

  constructor() {
    // Load tokens from localStorage on initialization
    this.accessToken = localStorage.getItem('access_token');
    this.refreshToken = localStorage.getItem('refresh_token');
  }

  async login(data: LoginRequest): Promise<TokenResponse> {
    const response = await axios.post<TokenResponse>(`${API_URL}/auth/login`, data);
    this.setTokens(response.data.access_token, response.data.refresh_token);
    return response.data;
  }

  async register(data: RegisterRequest): Promise<User> {
    const response = await axios.post<User>(`${API_URL}/auth/register`, data);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await axios.get<User>(`${API_URL}/auth/me`, {
      headers: this.getAuthHeaders()
    });
    return response.data;
  }

  async updateProfile(data: Partial<User>): Promise<User> {
    const response = await axios.put<User>(`${API_URL}/auth/me`, data, {
      headers: this.getAuthHeaders()
    });
    return response.data;
  }

  async changePassword(oldPassword: string, newPassword: string): Promise<void> {
    await axios.post(
      `${API_URL}/auth/change-password`,
      { old_password: oldPassword, new_password: newPassword },
      { headers: this.getAuthHeaders() }
    );
  }

  async refreshAccessToken(): Promise<void> {
    if (!this.refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await axios.post<TokenResponse>(`${API_URL}/auth/refresh`, {
      refresh_token: this.refreshToken
    });

    this.setTokens(response.data.access_token, response.data.refresh_token);
  }

  private setTokens(accessToken: string, refreshToken: string): void {
    this.accessToken = accessToken;
    this.refreshToken = refreshToken;
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
  }

  logout(): void {
    this.accessToken = null;
    this.refreshToken = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  isAuthenticated(): boolean {
    return !!this.accessToken;
  }

  getAuthHeaders(): Record<string, string> {
    if (!this.accessToken) {
      throw new Error('Not authenticated');
    }
    return {
      'Authorization': `Bearer ${this.accessToken}`
    };
  }

  getAccessToken(): string | null {
    return this.accessToken;
  }
}

export const authService = new AuthService();
