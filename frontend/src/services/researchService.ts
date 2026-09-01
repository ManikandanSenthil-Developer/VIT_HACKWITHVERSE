import { apiClient } from './api';
import {
  CompanyComparisonResponse,
  ThesisResponse,
  DecisionJournalItem,
  ScreenerResultItem,
  TimelineItem,
} from '../types';

export const researchService = {
  compare: async (symbolA: string, symbolB: string): Promise<CompanyComparisonResponse> => {
    const res = await apiClient.post<CompanyComparisonResponse>('/research/compare', {
      symbol_a: symbolA,
      symbol_b: symbolB,
    });
    return res.data;
  },

  buildThesis: async (symbol: string, saveToDb: boolean = false): Promise<ThesisResponse> => {
    const res = await apiClient.post<ThesisResponse>('/research/thesis', {
      symbol,
      save_to_db: saveToDb,
    });
    return res.data;
  },

  screen: async (params: {
    sector?: string;
    max_pe?: number;
    min_pe?: number;
    max_debt_to_equity?: number;
    min_change_percent?: number;
    limit?: number;
  }): Promise<ScreenerResultItem[]> => {
    const res = await apiClient.post<ScreenerResultItem[]>('/research/screen', params);
    return res.data;
  },

  getTimeline: async (symbol: string, limit: number = 15): Promise<TimelineItem[]> => {
    const res = await apiClient.get<TimelineItem[]>(`/research/timeline/${symbol}`, {
      params: { limit },
    });
    return res.data;
  },

  computeDiff: async (previousAnalysis: any, currentAnalysis: any): Promise<any> => {
    const res = await apiClient.post('/research/diff', {
      previous_analysis: previousAnalysis,
      current_analysis: currentAnalysis,
    });
    return res.data;
  },

  listDecisionJournal: async (symbol?: string): Promise<DecisionJournalItem[]> => {
    const res = await apiClient.get<DecisionJournalItem[]>('/research/decision-journal', {
      params: symbol ? { symbol } : {},
    });
    return res.data;
  },

  createJournalEntry: async (data: {
    symbol: string;
    thesis_title: string;
    reason: string;
    risk_assessment?: string;
    confidence: number;
    notes?: string;
  }): Promise<{ id: number; symbol: string; thesis_title: string; status: string; message: string }> => {
    const res = await apiClient.post('/research/decision-journal', data);
    return res.data;
  },

  reviewJournalEntry: async (entryId: number): Promise<any> => {
    const res = await apiClient.post(`/research/decision-journal/${entryId}/review`);
    return res.data;
  },
};
