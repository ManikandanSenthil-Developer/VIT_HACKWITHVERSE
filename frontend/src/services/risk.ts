import { apiClient } from './api';
import {
  PortfolioHealthResponse,
  ScenarioRequest,
  ScenarioResponse,
} from '../types';

export const riskService = {
  async getPortfolioHealth(portfolioId: number): Promise<PortfolioHealthResponse> {
    const res = await apiClient.get<PortfolioHealthResponse>(`/risk/portfolio/${portfolioId}`);
    return res.data;
  },

  async runScenario(request: ScenarioRequest): Promise<ScenarioResponse> {
    const res = await apiClient.post<ScenarioResponse>('/scenarios/run', request);
    return res.data;
  },
};
