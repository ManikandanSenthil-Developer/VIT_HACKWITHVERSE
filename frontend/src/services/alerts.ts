import { apiClient } from './api';
import { AlertItem } from '../types';

export const alertsService = {
  async getAlerts(params?: {
    status?: string;
    priority?: string;
    limit?: number;
  }): Promise<AlertItem[]> {
    const searchParams = new URLSearchParams();
    if (params?.status) searchParams.append('status', params.status);
    if (params?.priority) searchParams.append('priority', params.priority);
    if (params?.limit) searchParams.append('limit', params.limit.toString());

    const res = await apiClient.get<AlertItem[]>(`/alerts/?${searchParams.toString()}`);
    return res.data;
  },

  async updateAlert(
    alertId: number,
    payload: { status?: string; feedback?: string }
  ): Promise<AlertItem> {
    const res = await apiClient.patch<AlertItem>(`/alerts/${alertId}`, payload);
    return res.data;
  },

  async dismissAll(): Promise<{ message: string }> {
    const res = await apiClient.post<{ message: string }>('/alerts/dismiss-all');
    return res.data;
  },
};
