import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { riskService } from '../../services/risk';
import { portfolioService } from '../../services/portfolio';
import {
  ShieldAlert,
  HelpCircle,
  TrendingDown,
  Activity,
  SlidersHorizontal,
  PieChart,
  X,
  Scale,
} from 'lucide-react';
import { ScenarioAnalysisModal } from './ScenarioAnalysisModal';

export const PortfolioHealthWidget: React.FC = () => {
  const [showExplanationModal, setShowExplanationModal] = useState(false);
  const [showScenarioModal, setShowScenarioModal] = useState(false);

  // 1. Fetch user's primary portfolio
  const { data: portfolios } = useQuery({
    queryKey: ['portfolios'],
    queryFn: portfolioService.getPortfolios,
  });

  const activePortfolioId = portfolios && portfolios.length > 0 ? portfolios[0].id : null;

  // 2. Fetch portfolio risk health
  const { data: health, isLoading } = useQuery({
    queryKey: ['portfolioHealth', activePortfolioId],
    queryFn: () => (activePortfolioId ? riskService.getPortfolioHealth(activePortfolioId) : null),
    enabled: !!activePortfolioId,
  });

  if (isLoading || !health) {
    return (
      <div className="glass-panel p-6 rounded-2xl border border-white/5 animate-pulse flex items-center justify-between">
        <div className="space-y-2">
          <div className="w-32 h-4 bg-white/10 rounded" />
          <div className="w-48 h-3 bg-white/5 rounded" />
        </div>
        <div className="w-16 h-8 bg-white/10 rounded-full" />
      </div>
    );
  }

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'CRITICAL':
        return 'text-rose-400 bg-rose-500/10 border-rose-500/30';
      case 'HIGH':
        return 'text-orange-400 bg-orange-500/10 border-orange-500/30';
      case 'MODERATE':
        return 'text-purple-300 bg-purple-500/10 border-purple-500/30';
      default:
        return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30';
    }
  };

  const getGaugeColor = (score: number) => {
    if (score >= 80) return '#f43f5e';
    if (score >= 60) return '#f97316';
    if (score >= 35) return '#a855f7';
    return '#10b981';
  };

  return (
    <div className="glass-panel rounded-3xl p-6 sm:p-7 border border-white/10 shadow-2xl space-y-6 relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute -top-12 -right-12 w-64 h-64 bg-purple-600/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-gradient-to-tr from-purple-600 to-orange-500 p-0.5 shadow-glow-purple flex items-center justify-center">
            <div className="w-full h-full bg-[#0d091a] rounded-[14px] flex items-center justify-center">
              <ShieldAlert className="w-5 h-5 text-purple-300" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-bold text-white tracking-tight">
                Portfolio Risk Engine & Health
              </h3>
              <span
                className={`text-[10px] font-bold px-2 py-0.5 rounded-full border uppercase ${getRiskColor(
                  health.risk_level
                )}`}
              >
                {health.risk_level} RISK
              </span>
            </div>
            <p className="text-xs text-gray-400">
              Deterministic surveillance • Explainable factor attribution • Stress testing
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowExplanationModal(true)}
            className="px-3 py-1.5 rounded-xl bg-white/[0.03] hover:bg-white/[0.08] text-purple-300 border border-purple-500/20 text-xs font-semibold flex items-center gap-1.5 transition-all"
          >
            <HelpCircle className="w-3.5 h-3.5" />
            <span>Why is my risk {health.risk_level.toLowerCase()}?</span>
          </button>

          <button
            onClick={() => setShowScenarioModal(true)}
            className="px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-purple-600 to-orange-500 text-white font-semibold text-xs shadow-glow-purple flex items-center gap-1.5 transition-all"
          >
            <SlidersHorizontal className="w-3.5 h-3.5" />
            <span>Stress Test</span>
          </button>
        </div>
      </div>

      {/* Main KPI Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Risk Score */}
        <div className="p-4 rounded-2xl bg-black/40 border border-white/5 space-y-1">
          <div className="flex items-center justify-between text-xs text-gray-400">
            <span>Risk Score</span>
            <Activity className="w-3.5 h-3.5 text-purple-400" />
          </div>
          <div className="flex items-baseline gap-2">
            <span
              className="text-2xl font-extrabold font-mono-numbers"
              style={{ color: getGaugeColor(health.risk_score) }}
            >
              {health.risk_score}
            </span>
            <span className="text-xs text-gray-500">/ 100</span>
          </div>
          <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden mt-2">
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{
                width: `${health.risk_score}%`,
                backgroundColor: getGaugeColor(health.risk_score),
              }}
            />
          </div>
        </div>

        {/* Concentration */}
        <div className="p-4 rounded-2xl bg-black/40 border border-white/5 space-y-1">
          <div className="flex items-center justify-between text-xs text-gray-400">
            <span>Top Asset Exposure</span>
            <PieChart className="w-3.5 h-3.5 text-orange-400" />
          </div>
          <div className="text-2xl font-extrabold text-white font-mono-numbers">
            {health.concentration_top_asset_weight.toFixed(1)}%
          </div>
          <p className="text-[10px] text-gray-500 truncate">
            {health.concentration_top_asset_weight > 35 ? 'Heavy single-stock concentration' : 'Balanced allocation'}
          </p>
        </div>

        {/* Volatility */}
        <div className="p-4 rounded-2xl bg-black/40 border border-white/5 space-y-1">
          <div className="flex items-center justify-between text-xs text-gray-400">
            <span>Annualized Volatility</span>
            <Activity className="w-3.5 h-3.5 text-yellow-400" />
          </div>
          <div className="text-2xl font-extrabold text-white font-mono-numbers">
            {health.annualized_volatility.toFixed(1)}%
          </div>
          <p className="text-[10px] text-gray-500">Historical 30-day price dispersion</p>
        </div>

        {/* Drawdown */}
        <div className="p-4 rounded-2xl bg-black/40 border border-white/5 space-y-1">
          <div className="flex items-center justify-between text-xs text-gray-400">
            <span>Max Drawdown</span>
            <TrendingDown className="w-3.5 h-3.5 text-rose-400" />
          </div>
          <div className="text-2xl font-extrabold text-rose-400 font-mono-numbers">
            -{health.max_historical_drawdown.toFixed(1)}%
          </div>
          <p className="text-[10px] text-gray-500">Peak-to-trough retracement buffer</p>
        </div>
      </div>

      {/* Sector Breakdown & Primary Risk Factor */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 items-center">
        <div className="lg:col-span-8 space-y-2">
          <div className="flex items-center justify-between text-xs font-semibold text-gray-300">
            <span className="flex items-center gap-1.5">
              <Scale className="w-3.5 h-3.5 text-purple-400" />
              Sector Concentration Breakdown
            </span>
            <span className="text-[11px] text-gray-500">
              Primary: <strong className="text-white">{health.largest_risk_exposure}</strong>
            </span>
          </div>

          <div className="space-y-2 pt-1">
            {health.sector_breakdown.slice(0, 3).map((sec, i) => (
              <div key={i} className="space-y-1">
                <div className="flex items-center justify-between text-[11px] font-mono-numbers text-gray-400">
                  <span className="font-sans text-gray-300 truncate max-w-xs">{sec.sector}</span>
                  <span>
                    ${sec.value.toLocaleString()} ({sec.weight_percent.toFixed(1)}%)
                  </span>
                </div>
                <div className="w-full bg-white/5 h-1.5 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-purple-500 to-orange-400"
                    style={{ width: `${sec.weight_percent}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Explainability Callout Box */}
        <div className="lg:col-span-4 p-4 rounded-2xl bg-purple-950/20 border border-purple-500/20 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-purple-300">Leading Risk Factor</span>
            <span className="text-[10px] text-gray-400 font-mono-numbers">Deterministic</span>
          </div>
          <p className="text-xs text-gray-300 leading-relaxed">
            {health.risk_explanation.reasons[0] ||
              'Portfolio holdings are diversified across balanced historical return distributions.'}
          </p>
        </div>
      </div>

      {/* Why is my risk high? Explainability Modal */}
      {showExplanationModal && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-md flex items-center justify-center p-4">
          <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-white/10 max-w-lg w-full shadow-2xl space-y-6">
            <div className="flex items-center justify-between pb-4 border-b border-white/5">
              <div>
                <h4 className="text-base font-bold text-white">
                  Risk Score Explainability Breakdown
                </h4>
                <p className="text-xs text-gray-400">
                  Exact mathematical factor contributions (Total: {health.risk_score} / 100)
                </p>
              </div>
              <button
                onClick={() => setShowExplanationModal(false)}
                className="p-1 rounded-lg text-gray-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-3">
              {health.risk_explanation.factor_contributions.map((f, i) => (
                <div key={i} className="p-3 rounded-xl bg-black/40 border border-white/5 space-y-1.5">
                  <div className="flex items-center justify-between text-xs font-bold">
                    <span className="text-white">{f.factor}</span>
                    <span className="text-orange-400 font-mono-numbers">
                      +{f.contribution.toFixed(1)} pts ({(f.weight * 100).toFixed(0)}% weight)
                    </span>
                  </div>
                  <p className="text-[11px] text-gray-400 leading-relaxed">{f.description}</p>
                </div>
              ))}
            </div>

            <div className="p-3.5 rounded-xl bg-white/[0.02] border border-white/5 text-[11px] text-gray-400 leading-relaxed">
              <strong>Non-Hallucinatory Governance:</strong> All factor scores are computed deterministically from verified
              holding valuations, historical OHLCV variance, and company sector classifications. AI agents explain the
              factors; they never invent the underlying numbers.
            </div>

            <button
              onClick={() => setShowExplanationModal(false)}
              className="w-full py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white font-semibold text-xs transition-all"
            >
              Close Breakdown
            </button>
          </div>
        </div>
      )}

      {/* Scenario Analysis / Stress Test Modal */}
      {showScenarioModal && activePortfolioId && (
        <ScenarioAnalysisModal
          portfolioId={activePortfolioId}
          onClose={() => setShowScenarioModal(false)}
        />
      )}
    </div>
  );
};
