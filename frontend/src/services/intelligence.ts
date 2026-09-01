import { apiClient } from './api';
import {
  AnalysisResponse,
  AnalysisHistoryItem,
  AgentStatusInfo,
} from '../types';

export const intelligenceService = {
  async analyze(params: {
    query: string;
    symbol: string;
    analysis_type?: string;
  }): Promise<AnalysisResponse> {
    const res = await apiClient.post<AnalysisResponse>('/intelligence/analyze', params);
    return res.data;
  },

  async getHistory(limit: number = 20): Promise<AnalysisHistoryItem[]> {
    const res = await apiClient.get<AnalysisHistoryItem[]>(`/intelligence/history?limit=${limit}`);
    return res.data;
  },

  async getAnalysis(id: number): Promise<AnalysisHistoryItem> {
    const res = await apiClient.get<AnalysisHistoryItem>(`/intelligence/${id}`);
    return res.data;
  },

  async getAgents(): Promise<AgentStatusInfo[]> {
    const res = await apiClient.get<AgentStatusInfo[]>('/intelligence/agents');
    return res.data;
  },
};
