import { apiClient } from './api';
import { InvestorProfile, Portfolio, Watchlist, Holding } from '../types';

export const portfolioService = {
  // Investor Profile
  async getProfile(): Promise<InvestorProfile> {
    const res = await apiClient.get<InvestorProfile>('/profile/');
    return res.data;
  },

  async updateProfile(data: Partial<InvestorProfile>): Promise<InvestorProfile> {
    const res = await apiClient.put<InvestorProfile>('/profile/', data);
    return res.data;
  },

  // Watchlists
  async getWatchlists(): Promise<Watchlist[]> {
    const res = await apiClient.get<Watchlist[]>('/watchlist/');
    return res.data;
  },

  async createWatchlist(data: { name: string; description?: string; symbols?: string }): Promise<Watchlist> {
    const res = await apiClient.post<Watchlist>('/watchlist/', data);
    return res.data;
  },

  async deleteWatchlist(id: number): Promise<void> {
    await apiClient.delete(`/watchlist/${id}`);
  },

  // Portfolios
  async getPortfolios(): Promise<Portfolio[]> {
    const res = await apiClient.get<Portfolio[]>('/portfolio/');
    return res.data;
  },

  async getPortfolio(id: number): Promise<Portfolio> {
    const res = await apiClient.get<Portfolio>(`/portfolio/${id}`);
    return res.data;
  },

  async createPortfolio(data: { name: string; description?: string; cash_balance?: number }): Promise<Portfolio> {
    const res = await apiClient.post<Portfolio>('/portfolio/', data);
    return res.data;
  },

  async addHolding(portfolioId: number, holding: {
    symbol: string;
    asset_type?: string;
    quantity: number;
    buy_price: number;
    current_value?: number;
    notes?: string;
  }): Promise<Holding> {
    const res = await apiClient.post<Holding>(`/portfolio/${portfolioId}/holdings`, holding);
    return res.data;
  },
};
