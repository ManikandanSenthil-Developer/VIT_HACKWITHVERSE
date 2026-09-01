import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { portfolioService } from '../services/portfolio';
import { PieChart, Plus, Layers, SlidersHorizontal } from 'lucide-react';
import { ScenarioAnalysisModal } from '../components/dashboard/ScenarioAnalysisModal';

export const PortfolioPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedStressTestPortfolioId, setSelectedStressTestPortfolioId] = useState<number | null>(null);
  const [newPortfolioName, setNewPortfolioName] = useState('');
  const [newCashBalance, setNewCashBalance] = useState('25000');

  const { data: portfolios, isLoading } = useQuery({
    queryKey: ['portfolios'],
    queryFn: portfolioService.getPortfolios,
  });

  const createMutation = useMutation({
    mutationFn: portfolioService.createPortfolio,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['portfolios'] });
      setShowAddModal(false);
      setNewPortfolioName('');
    },
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newPortfolioName.trim()) return;
    createMutation.mutate({
      name: newPortfolioName,
      cash_balance: parseFloat(newCashBalance) || 10000,
    });
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <PieChart className="w-6 h-6 text-purple-400" />
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
              Portfolio Management
            </h1>
          </div>
          <p className="text-xs sm:text-sm text-gray-400 mt-1">
            Track asset allocations, cash reserves, and multi-agent hedging strategies
          </p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-orange-500 hover:from-purple-500 hover:to-orange-400 text-white font-semibold text-xs shadow-glow-purple flex items-center gap-2 transition-all self-start"
        >
          <Plus className="w-4 h-4" />
          <span>New Portfolio</span>
        </button>
      </div>

      {/* Loading state */}
      {isLoading ? (
        <div className="py-20 flex justify-center">
          <div className="w-8 h-8 border-2 border-purple-500/20 border-t-purple-500 rounded-full animate-spin" />
        </div>
      ) : (
        <div className="space-y-6">
          {portfolios && portfolios.length > 0 ? (
            portfolios.map((portfolio) => (
              <div
                key={portfolio.id}
                className="glass-panel rounded-2xl p-6 border border-white/5 space-y-6"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-white/5">
                  <div>
                    <h3 className="text-lg font-bold text-white flex items-center gap-2">
                      <span>{portfolio.name}</span>
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-purple-500/10 text-purple-300 border border-purple-500/20">
                        {portfolio.currency}
                      </span>
                    </h3>
                    <p className="text-xs text-gray-400 mt-0.5">
                      {portfolio.description || 'Active automated hedge portfolio'}
                    </p>
                  </div>

                  <div className="flex items-center gap-6">
                    <div>
                      <span className="text-[11px] uppercase tracking-wider text-gray-400">Total Value</span>
                      <div className="text-xl font-bold text-white font-mono-numbers">
                        ${portfolio.total_value?.toLocaleString()}
                      </div>
                    </div>
                    <div>
                      <span className="text-[11px] uppercase tracking-wider text-gray-400">Cash Reserves</span>
                      <div className="text-xl font-bold text-emerald-400 font-mono-numbers">
                        ${portfolio.cash_balance?.toLocaleString()}
                      </div>
                    </div>
                    <button
                      onClick={() => setSelectedStressTestPortfolioId(portfolio.id)}
                      className="px-3 py-1.5 rounded-xl bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 border border-purple-500/30 text-xs font-semibold flex items-center gap-1.5 transition-all self-end"
                      title="Run What-If Scenario Stress Testing"
                    >
                      <SlidersHorizontal className="w-3.5 h-3.5" />
                      <span>Stress Test</span>
                    </button>
                  </div>
                </div>

                {/* Holdings Table */}
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-gray-400">
                      Asset Holdings ({portfolio.holdings?.length || 0})
                    </h4>
                  </div>

                  {portfolio.holdings && portfolio.holdings.length > 0 ? (
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs font-mono-numbers">
                        <thead>
                          <tr className="border-b border-white/5 text-[11px] text-gray-400 uppercase">
                            <th className="pb-2">Symbol</th>
                            <th className="pb-2">Type</th>
                            <th className="pb-2">Quantity</th>
                            <th className="pb-2">Avg Buy Price</th>
                            <th className="pb-2 text-right">Current Valuation</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                          {portfolio.holdings.map((h) => (
                            <tr key={h.id} className="hover:bg-white/[0.02]">
                              <td className="py-2.5 font-bold text-white font-sans">{h.symbol}</td>
                              <td className="py-2.5 text-gray-400 font-sans">{h.asset_type}</td>
                              <td className="py-2.5 text-gray-300">{h.quantity}</td>
                              <td className="py-2.5 text-gray-300">${h.buy_price}</td>
                              <td className="py-2.5 text-right font-bold text-emerald-400">
                                ${h.current_value?.toLocaleString()}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : (
                    <div className="p-6 rounded-xl bg-black/20 text-center text-xs text-gray-500">
                      No holdings added yet. Ready for Phase 2 Market Data & Order Router integration.
                    </div>
                  )}
                </div>
              </div>
            ))
          ) : (
            <div className="glass-panel p-12 text-center rounded-2xl border border-white/5">
              <Layers className="w-10 h-10 text-gray-500 mx-auto mb-3" />
              <h3 className="text-base font-bold text-white">No Portfolios Found</h3>
              <p className="text-xs text-gray-400 mt-1 max-w-sm mx-auto">
                Create your first quantitative portfolio to begin tracking autonomous holdings.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Add Portfolio Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-md flex items-center justify-center p-4">
          <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-white/10 max-w-md w-full shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-2">Create New Portfolio</h3>
            <p className="text-xs text-gray-400 mb-6">
              Establish a new target allocation fund for autonomous agent surveillance.
            </p>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1.5">
                  Portfolio Name
                </label>
                <input
                  type="text"
                  required
                  value={newPortfolioName}
                  onChange={(e) => setNewPortfolioName(e.target.value)}
                  placeholder="e.g. Autonomous Macro Hedge"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-black/50 border border-white/10 text-sm text-white focus:outline-none focus:border-purple-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1.5">
                  Initial Cash Allocation (USD)
                </label>
                <input
                  type="number"
                  required
                  value={newCashBalance}
                  onChange={(e) => setNewCashBalance(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl bg-black/50 border border-white/10 text-sm text-white focus:outline-none focus:border-purple-500"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-white/5">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 rounded-xl text-xs text-gray-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createMutation.isPending}
                  className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-orange-500 text-white font-semibold text-xs shadow-glow-purple"
                >
                  {createMutation.isPending ? 'Creating...' : 'Create Portfolio'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Stress Test Modal */}
      {selectedStressTestPortfolioId && (
        <ScenarioAnalysisModal
          portfolioId={selectedStressTestPortfolioId}
          onClose={() => setSelectedStressTestPortfolioId(null)}
        />
      )}
    </div>
  );
};
