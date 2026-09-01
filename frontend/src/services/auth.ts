import { apiClient } from './api';
import { AuthTokens, User } from '../types';

export const authService = {
  async register(data: { email: string; password: string; full_name?: string }): Promise<AuthTokens> {
    const res = await apiClient.post<AuthTokens>('/auth/register', data);
    return res.data;
  },

  async login(data: { email: string; password: string }): Promise<AuthTokens> {
    const res = await apiClient.post<AuthTokens>('/auth/login', data);
    return res.data;
  },

  async getMe(): Promise<User> {
    const res = await apiClient.get<User>('/auth/me');
    return res.data;
  },

  async updateMe(data: { full_name?: string; password?: string }): Promise<User> {
    const res = await apiClient.put<User>('/user/me', data);
    return res.data;
  },
};
