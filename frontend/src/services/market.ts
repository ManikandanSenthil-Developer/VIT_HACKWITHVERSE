import { apiClient } from './api';
import {
  MarketResponseWrapper,
  MarketQuote,
  HistoricalPriceData,
  CompanyProfile,
  FundamentalData,
} from '../types';

export const marketService = {
  async getQuote(symbol: string): Promise<MarketResponseWrapper<MarketQuote>> {
    const res = await apiClient.get<MarketResponseWrapper<MarketQuote>>(`/market/quote/${symbol}`);
    return res.data;
  },

  async getHistory(
    symbol: string,
    period: '1d' | '5d' | '1mo' | '3mo' | '6mo' | '1y' = '1mo'
  ): Promise<MarketResponseWrapper<HistoricalPriceData>> {
    const res = await apiClient.get<MarketResponseWrapper<HistoricalPriceData>>(
      `/market/history/${symbol}?period=${period}`
    );
    return res.data;
  },

  async getCompany(symbol: string): Promise<MarketResponseWrapper<CompanyProfile>> {
    const res = await apiClient.get<MarketResponseWrapper<CompanyProfile>>(`/market/company/${symbol}`);
    return res.data;
  },

  async getFundamentals(symbol: string): Promise<MarketResponseWrapper<FundamentalData>> {
    const res = await apiClient.get<MarketResponseWrapper<FundamentalData>>(`/market/fundamentals/${symbol}`);
    return res.data;
  },
};
