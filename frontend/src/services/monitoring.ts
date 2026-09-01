import { apiClient } from './api';
import {
  MonitoringRunResponse,
  AlertItem,
  DailyBriefResponse,
} from '../types';

export const monitoringService = {
  async triggerMonitoring(): Promise<MonitoringRunResponse> {
    const res = await apiClient.post<MonitoringRunResponse>('/monitoring/run');
    return res.data;
  },

  async simulateDemoEvent(payload: {
    symbol: string;
    event_type?: string;
    price_change_pct?: number;
    volume_multiple?: number;
    title?: string;
    description?: string;
  }): Promise<AlertItem> {
    const res = await apiClient.post<AlertItem>('/monitoring/simulate-event', payload);
    return res.data;
  },

  async getLatestStatus(): Promise<MonitoringRunResponse | null> {
    const res = await apiClient.get<MonitoringRunResponse | null>('/monitoring/status');
    return res.data;
  },

  async getDailyBrief(): Promise<DailyBriefResponse> {
    const res = await apiClient.get<DailyBriefResponse>('/intelligence/daily-brief');
    return res.data;
  },

  async getIntelligenceFeed(limit: number = 20): Promise<AlertItem[]> {
    const res = await apiClient.get<AlertItem[]>(`/intelligence/feed?limit=${limit}`);
    return res.data;
  },
};
