import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { riskService } from '../../services/risk';
import { X, SlidersHorizontal, AlertCircle, TrendingDown, TrendingUp } from 'lucide-react';
import { ScenarioResponse } from '../../types';

interface ScenarioModalProps {
  portfolioId: number;
  onClose: () => void;
}

export const ScenarioAnalysisModal: React.FC<ScenarioModalProps> = ({ portfolioId, onClose }) => {
  const [symbol, setSymbol] = useState('NVDA');
  const [shockType, setShockType] = useState('holding_shock');
  const [percentage, setPercentage] = useState(-10.0);
  const [scenarioResult, setScenarioResult] = useState<ScenarioResponse | null>(null);

  const scenarioMutation = useMutation({
    mutationFn: riskService.runScenario,
    onSuccess: (data) => {
      setScenarioResult(data);
    },
  });

  const handleSimulate = (e: React.FormEvent) => {
    e.preventDefault();
    scenarioMutation.mutate({
      portfolio_id: portfolioId,
      shock_type: shockType,
      target_symbol: symbol.trim().toUpperCase(),
      percentage_change: percentage,
    });
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-md flex items-center justify-center p-4">
      <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-white/10 max-w-2xl w-full shadow-2xl space-y-6 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between pb-4 border-b border-white/5">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
              <SlidersHorizontal className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">
                What-If Scenario Stress Testing
              </h3>
              <p className="text-xs text-gray-400">
                Mathematical portfolio sensitivity analysis • Non-predictive risk modeling
              </p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 rounded-lg text-gray-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Input Parameters */}
        <form onSubmit={handleSimulate} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
            <div>
              <label className="block text-xs font-semibold text-gray-400 mb-1">
                Shock Model
              </label>
              <select
                value={shockType}
                onChange={(e) => setShockType(e.target.value)}
                className="w-full px-2.5 py-2.5 rounded-xl bg-black/50 border border-white/10 text-xs text-white focus:outline-none focus:border-purple-500"
              >
                <option value="holding_shock">Single Stock Shock</option>
                <option value="sector_shock">Sector-wide Shift</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-400 mb-1">
                {shockType === 'sector_shock' ? 'Sector Name' : 'Target Symbol'}
              </label>
              <input
                type="text"
                required
                value={symbol}
                onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                placeholder={shockType === 'sector_shock' ? 'Technology' : 'NVDA'}
                className="w-full px-3 py-2.5 rounded-xl bg-black/50 border border-white/10 text-sm font-bold text-white uppercase font-mono-numbers focus:outline-none focus:border-purple-500"
              />
            </div>

            <div className="sm:col-span-2">
              <div className="flex items-center justify-between mb-1">
                <label className="text-xs font-semibold text-gray-400">
                  Hypothetical Price Shock
                </label>
                <span className="text-xs font-extrabold text-orange-400 font-mono-numbers">
                  {percentage > 0 ? `+${percentage}%` : `${percentage}%`}
                </span>
              </div>
              <input
                type="range"
                min="-30"
                max="30"
                step="1"
                value={percentage}
                onChange={(e) => setPercentage(parseFloat(e.target.value))}
                className="w-full accent-purple-500 cursor-pointer"
              />
              <div className="flex justify-between text-[10px] text-gray-500 font-mono-numbers">
                <span>-30%</span>
                <span>-10%</span>
                <span>0%</span>
                <span>+10%</span>
                <span>+30%</span>
              </div>
            </div>
          </div>

          {/* Quick Presets */}
          <div className="flex flex-wrap items-center gap-2 pt-1 text-[11px]">
            <span className="text-gray-500 font-semibold">Stress Presets:</span>
            {[-10, -5, 5, 10].map((p) => (
              <button
                key={p}
                type="button"
                onClick={() => setPercentage(p)}
                className={`px-2.5 py-1 rounded-lg border font-mono-numbers transition-all ${
                  percentage === p
                    ? 'bg-purple-500/20 text-purple-300 border-purple-500/40 font-bold'
                    : 'bg-white/[0.02] text-gray-400 border-white/5 hover:text-white'
                }`}
              >
                {p > 0 ? `+${p}%` : `${p}%`}
              </button>
            ))}
          </div>

          <button
            type="submit"
            disabled={scenarioMutation.isPending}
            className="w-full py-3 rounded-2xl bg-gradient-to-r from-purple-600 to-orange-500 hover:from-purple-500 hover:to-orange-400 text-white font-semibold text-xs shadow-glow-purple flex items-center justify-center gap-2 transition-all disabled:opacity-40"
          >
            {scenarioMutation.isPending ? (
              <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
            ) : (
              <span>Calculate Mathematical Portfolio Impact</span>
            )}
          </button>
        </form>

        {/* Results Display */}
        {scenarioResult && (
          <div className="p-5 rounded-2xl bg-black/40 border border-purple-500/20 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-white/5">
              <div>
                <span className="text-[10px] uppercase font-bold tracking-widest text-purple-400">
                  Simulation Outcome
                </span>
                <h4 className="text-sm font-bold text-white">{scenarioResult.scenario_name}</h4>
              </div>

              <div className="text-right">
                <span className="text-[10px] text-gray-400">Net Portfolio Shift</span>
                <div
                  className={`text-base font-extrabold font-mono-numbers flex items-center justify-end gap-1 ${
                    scenarioResult.total_difference_usd >= 0 ? 'text-emerald-400' : 'text-rose-400'
                  }`}
                >
                  {scenarioResult.total_difference_usd >= 0 ? (
                    <TrendingUp className="w-4 h-4" />
                  ) : (
                    <TrendingDown className="w-4 h-4" />
                  )}
                  <span>
                    {scenarioResult.total_difference_usd >= 0 ? '+' : ''}$
                    {scenarioResult.total_difference_usd.toLocaleString()} (
                    {scenarioResult.total_difference_percent >= 0 ? '+' : ''}
                    {scenarioResult.total_difference_percent.toFixed(2)}%)
                  </span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 text-xs font-mono-numbers">
              <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5">
                <span className="text-[10px] text-gray-500 font-sans block">Current Portfolio Value</span>
                <span className="text-base font-bold text-white">
                  ${scenarioResult.current_total_value.toLocaleString()}
                </span>
              </div>

              <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5">
                <span className="text-[10px] text-gray-500 font-sans block">Simulated Portfolio Value</span>
                <span className="text-base font-bold text-purple-300">
                  ${scenarioResult.scenario_total_value.toLocaleString()}
                </span>
              </div>
            </div>

            {/* Holdings Breakdown */}
            <div className="space-y-2">
              <span className="text-[11px] font-bold text-gray-400 uppercase tracking-wider">
                Position Sensitivity Breakdown:
              </span>
              <div className="space-y-1.5 text-xs font-mono-numbers">
                {scenarioResult.holdings_impact.map((h, idx) => (
                  <div
                    key={idx}
                    className={`p-2.5 rounded-xl border flex items-center justify-between ${
                      h.value_difference !== 0
                        ? 'bg-purple-950/20 border-purple-500/30 text-white'
                        : 'bg-black/20 border-white/5 text-gray-500'
                    }`}
                  >
                    <span className="font-bold font-sans">{h.symbol}</span>
                    <span>${h.current_value.toLocaleString()} → ${h.scenario_value.toLocaleString()}</span>
                    <span
                      className={`font-bold ${
                        h.value_difference > 0
                          ? 'text-emerald-400'
                          : h.value_difference < 0
                          ? 'text-rose-400'
                          : 'text-gray-500'
                      }`}
                    >
                      {h.value_difference >= 0 ? '+' : ''}${h.value_difference.toLocaleString()}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-3 rounded-xl bg-white/[0.01] border border-white/5 text-[10px] text-gray-400 flex items-start gap-2">
              <AlertCircle className="w-3.5 h-3.5 text-orange-400 shrink-0 mt-0.5" />
              <span>{scenarioResult.disclaimer}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
