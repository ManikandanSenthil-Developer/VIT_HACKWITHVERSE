import { apiClient } from './api';
import { CopilotChatResponse, CopilotConversationItem, CopilotMessageItem } from '../types';

export const copilotService = {
  chat: async (message: string, conversationId?: number, language?: string): Promise<CopilotChatResponse> => {
    const res = await apiClient.post<CopilotChatResponse>('/copilot/chat', {
      message,
      conversation_id: conversationId,
      language,
    });
    return res.data;
  },

  getConversations: async (): Promise<CopilotConversationItem[]> => {
    const res = await apiClient.get<CopilotConversationItem[]>('/copilot/conversations');
    return res.data;
  },

  getConversationThread: async (conversationId: number): Promise<CopilotMessageItem[]> => {
    const res = await apiClient.get<CopilotMessageItem[]>(`/copilot/conversations/${conversationId}`);
    return res.data;
  },

  deleteConversation: async (conversationId: number): Promise<void> => {
    await apiClient.delete(`/copilot/conversations/${conversationId}`);
  },
};
