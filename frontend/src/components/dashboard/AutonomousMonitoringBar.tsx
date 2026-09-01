import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { monitoringService } from '../../services/monitoring';
import { RefreshCw, Sparkles, Activity, X } from 'lucide-react';

export const AutonomousMonitoringBar: React.FC = () => {
  const queryClient = useQueryClient();
  const [showDemoModal, setShowDemoModal] = useState(false);
  const [demoSymbol, setDemoSymbol] = useState('NVDA');
  const [demoShift, setDemoShift] = useState(-4.5);

  const sweepMutation = useMutation({
    mutationFn: monitoringService.triggerMonitoring,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      queryClient.invalidateQueries({ queryKey: ['dailyBrief'] });
      queryClient.invalidateQueries({ queryKey: ['portfolioHealth'] });
    },
  });

  const demoMutation = useMutation({
    mutationFn: monitoringService.simulateDemoEvent,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      queryClient.invalidateQueries({ queryKey: ['dailyBrief'] });
      queryClient.invalidateQueries({ queryKey: ['portfolioHealth'] });
      setShowDemoModal(false);
    },
  });

  const handleRunDemo = (e: React.FormEvent) => {
    e.preventDefault();
    demoMutation.mutate({
      symbol: demoSymbol.trim().toUpperCase(),
      price_change_pct: demoShift,
      volume_multiple: 2.2,
      title: `[DEMO] ${demoSymbol.toUpperCase()} experienced abnormal ${demoShift > 0 ? '+' : ''}${demoShift.toFixed(1)}% price move`,
    });
  };

  return (
    <div className="glass-panel p-4 rounded-2xl border border-white/5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-lg">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
          <Activity className="w-4 h-4" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <h4 className="text-xs font-bold text-white">Autonomous Surveillance Loop</h4>
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          </div>
          <p className="text-[11px] text-gray-400">
            Monitoring active watchlists • Statistical anomaly triggers • Auto multi-agent investigations
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2 self-end sm:self-auto">
        <button
          onClick={() => sweepMutation.mutate()}
          disabled={sweepMutation.isPending}
          className="px-3 py-1.5 rounded-xl bg-white/[0.03] hover:bg-white/[0.08] text-gray-300 hover:text-white border border-white/5 text-xs font-semibold flex items-center gap-1.5 transition-all disabled:opacity-40"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${sweepMutation.isPending ? 'animate-spin' : ''}`} />
          <span>{sweepMutation.isPending ? 'Scanning...' : 'Run Surveillance Sweep'}</span>
        </button>

        <button
          onClick={() => setShowDemoModal(true)}
          className="px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-orange-500 to-purple-600 hover:from-orange-400 hover:to-purple-500 text-white font-semibold text-xs shadow-glow-purple flex items-center gap-1.5 transition-all"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>Simulate Event [Demo]</span>
        </button>
      </div>

      {/* Demo Simulation Modal */}
      {showDemoModal && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-md flex items-center justify-center p-4">
          <div className="glass-panel p-6 sm:p-7 rounded-3xl border border-white/10 max-w-md w-full shadow-2xl space-y-5">
            <div className="flex items-center justify-between pb-3 border-b border-white/5">
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-orange-400" />
                <h4 className="text-sm font-bold text-white">Trigger Demo Surveillance Event</h4>
              </div>
              <button
                onClick={() => setShowDemoModal(false)}
                className="p-1 rounded-lg text-gray-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <p className="text-xs text-gray-400 leading-relaxed">
              Injects a simulated market displacement event into the autonomous monitoring engine.
              Demonstrates automatic event detection, multi-agent investigation, conflict checks, and proactive alert prioritization.
            </p>

            <form onSubmit={handleRunDemo} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1">
                  Target Stock Symbol
                </label>
                <input
                  type="text"
                  required
                  value={demoSymbol}
                  onChange={(e) => setDemoSymbol(e.target.value.toUpperCase())}
                  placeholder="NVDA"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-black/50 border border-white/10 text-sm font-bold text-white uppercase font-mono-numbers focus:outline-none focus:border-purple-500"
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="text-xs font-semibold text-gray-300">
                    Simulated Price Displacement
                  </label>
                  <span className="text-xs font-bold text-orange-400 font-mono-numbers">
                    {demoShift > 0 ? `+${demoShift.toFixed(1)}%` : `${demoShift.toFixed(1)}%`}
                  </span>
                </div>
                <input
                  type="range"
                  min="-15"
                  max="15"
                  step="0.5"
                  value={demoShift}
                  onChange={(e) => setDemoShift(parseFloat(e.target.value))}
                  className="w-full accent-orange-500 cursor-pointer"
                />
              </div>

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-white/5">
                <button
                  type="button"
                  onClick={() => setShowDemoModal(false)}
                  className="px-4 py-2 rounded-xl text-xs text-gray-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={demoMutation.isPending}
                  className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-orange-500 to-purple-600 text-white font-semibold text-xs shadow-glow-purple flex items-center gap-2"
                >
                  {demoMutation.isPending ? 'Simulating & Investigating...' : 'Trigger Autonomous Flow'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
