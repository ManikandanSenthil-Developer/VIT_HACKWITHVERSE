import { apiClient } from './api';
import { RagSearchResponse, DocumentItem } from '../types';

export const ragService = {
  async search(params: {
    query: string;
    symbol?: string;
    top_k?: number;
    similarity_threshold?: number;
  }): Promise<RagSearchResponse> {
    const res = await apiClient.post<RagSearchResponse>('/rag/search', params);
    return res.data;
  },

  async ingest(data: {
    title: string;
    company_symbol: string;
    document_type?: string;
    content?: string;
    source_url?: string;
    source_identifier?: string;
  }): Promise<DocumentItem> {
    const res = await apiClient.post<DocumentItem>('/rag/ingest', data);
    return res.data;
  },

  async getDocuments(symbol?: string): Promise<DocumentItem[]> {
    const url = symbol ? `/rag/documents?symbol=${symbol}` : '/rag/documents';
    const res = await apiClient.get<DocumentItem[]>(url);
    return res.data;
  },

  async getDocument(id: number): Promise<DocumentItem> {
    const res = await apiClient.get<DocumentItem>(`/rag/document/${id}`);
    return res.data;
  },
};
