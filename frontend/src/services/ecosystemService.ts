import { apiClient } from './api';
import {
  UserAccessibilityPreference,
  ImpactMetrics,
  ProviderHealthItem,
  EducationConcept,
  SourceConflictReport,
  CsvImportResult,
} from '../types';

export const ecosystemService = {
  getAccessibilityPreferences: async (): Promise<UserAccessibilityPreference> => {
    const res = await apiClient.get<UserAccessibilityPreference>('/ecosystem/accessibility');
    return res.data;
  },

  updateAccessibilityPreferences: async (
    data: Partial<UserAccessibilityPreference>
  ): Promise<{ status: string; preferences: UserAccessibilityPreference }> => {
    const res = await apiClient.put('/ecosystem/accessibility', data);
    return res.data;
  },

  submitFeedback: async (data: {
    target_type: string;
    target_id: string;
    is_helpful: boolean;
    comment?: string;
  }): Promise<{ status: string; feedback_id: number }> => {
    const res = await apiClient.post('/ecosystem/feedback', data);
    return res.data;
  },

  getFeedbackAnalytics: async (): Promise<any> => {
    const res = await apiClient.get('/ecosystem/feedback/analytics');
    return res.data;
  },

  getImpactMetrics: async (): Promise<ImpactMetrics> => {
    const res = await apiClient.get<ImpactMetrics>('/ecosystem/impact');
    return res.data;
  },

  exportUserDataJson: async (): Promise<any> => {
    const res = await apiClient.get('/ecosystem/export', {
      params: { format: 'json' },
    });
    return res.data;
  },

  downloadUserDataCsv: async (): Promise<void> => {
    const res = await apiClient.get('/ecosystem/export', {
      params: { format: 'csv' },
      responseType: 'blob',
    });
    const blob = new Blob([res.data], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `mats_user_data_export_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  },

  getProvidersHealth: async (): Promise<ProviderHealthItem[]> => {
    const res = await apiClient.get<ProviderHealthItem[]>('/ecosystem/providers/health');
    return res.data;
  },

  syncMockBroker: async (accountId: string = 'ACC-DEMO-9942'): Promise<any> => {
    const res = await apiClient.post('/ecosystem/broker/sync', { account_id: accountId });
    return res.data;
  },

  getEducationConcept: async (concept: string, language: string = 'en'): Promise<EducationConcept> => {
    const res = await apiClient.get<EducationConcept>(`/ecosystem/education/${concept}`, {
      params: { language },
    });
    return res.data;
  },

  checkSourceConflict: async (payload: {
    symbol: string;
    metric: string;
    source_a_name: string;
    source_a_value: number;
    source_a_hierarchy?: string;
    source_b_name: string;
    source_b_value: number;
    source_b_hierarchy?: string;
  }): Promise<SourceConflictReport> => {
    const res = await apiClient.post<SourceConflictReport>('/ecosystem/source-conflict-check', payload);
    return res.data;
  },

  importPortfolioCsv: async (portfolioId: number, csvContent: string): Promise<CsvImportResult> => {
    const res = await apiClient.post<CsvImportResult>(`/portfolio/${portfolioId}/import-csv`, {
      csv_content: csvContent,
    });
    return res.data;
  },
};
