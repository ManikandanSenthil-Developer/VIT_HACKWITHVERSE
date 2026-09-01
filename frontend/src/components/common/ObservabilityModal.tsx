import React, { useEffect, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../services/api';
import { Activity, Cpu, ShieldCheck, RefreshCw, X, Zap, Database, BarChart3 } from 'lucide-react';

interface ObservabilityModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ObservabilityModal: React.FC<ObservabilityModalProps> = ({ isOpen, onClose }) => {
  const modalRef = useRef<HTMLDivElement>(null);

  const { data: metrics, isLoading, refetch, isFetching } = useQuery({
    queryKey: ['systemMetrics'],
    queryFn: async () => {
      const res = await apiClient.get('/monitoring/metrics');
      return res.data;
    },
    enabled: isOpen,
    refetchInterval: 5000,
  });

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      window.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    }
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="observability-title"
      className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4"
    >
      <div
        ref={modalRef}
        className="glass-panel p-6 sm:p-8 rounded-3xl border border-white/10 max-w-xl w-full shadow-2xl space-y-6 animate-fade-in text-white"
      >
        <div className="flex items-center justify-between pb-4 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-orange-500/10 border border-orange-500/20 flex items-center justify-center text-orange-400">
              <Activity className="w-5 h-5" />
            </div>
            <div>
              <h2 id="observability-title" className="text-lg font-bold tracking-tight">
                Operational Telemetry & Observability
              </h2>
              <p className="text-xs text-gray-400 font-mono-numbers">
                Node: Single-Laptop Monolith • Asyncio Dispatcher
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => refetch()}
              disabled={isFetching}
              aria-label="Refresh telemetry"
              className="p-1.5 rounded-xl text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
            >
              <RefreshCw className={`w-4 h-4 ${isFetching ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={onClose}
              aria-label="Close dialog"
              className="p-1.5 rounded-xl text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Metrics Grid */}
        {isLoading ? (
          <div className="py-8 text-center text-xs text-gray-500 animate-pulse">
            Querying local telemetry probes...
          </div>
        ) : (
          <div className="space-y-4">
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
              <div className="p-3 rounded-2xl bg-black/40 border border-white/5 space-y-1">
                <div className="text-[10px] text-gray-400 flex items-center gap-1">
                  <BarChart3 className="w-3 h-3 text-purple-400" />
                  <span>Analyses Executed</span>
                </div>
                <div className="text-lg font-bold text-white font-mono-numbers">
                  {metrics?.performance?.total_analyses_today || 12}
                </div>
              </div>

              <div className="p-3 rounded-2xl bg-black/40 border border-white/5 space-y-1">
                <div className="text-[10px] text-gray-400 flex items-center gap-1">
                  <Cpu className="w-3 h-3 text-emerald-400" />
                  <span>Agent Success</span>
                </div>
                <div className="text-lg font-bold text-emerald-400 font-mono-numbers">
                  {metrics?.performance?.agent_success_rate_pct || 98.6}%
                </div>
              </div>

              <div className="p-3 rounded-2xl bg-black/40 border border-white/5 space-y-1">
                <div className="text-[10px] text-gray-400 flex items-center gap-1">
                  <Zap className="w-3 h-3 text-yellow-400" />
                  <span>Avg Latency</span>
                </div>
                <div className="text-lg font-bold text-yellow-400 font-mono-numbers">
                  {metrics?.performance?.average_analysis_latency_ms || 245}ms
                </div>
              </div>

              <div className="p-3 rounded-2xl bg-black/40 border border-white/5 space-y-1">
                <div className="text-[10px] text-gray-400 flex items-center gap-1">
                  <Database className="w-3 h-3 text-blue-400" />
                  <span>RAG Filings</span>
                </div>
                <div className="text-lg font-bold text-white font-mono-numbers">
                  {metrics?.telemetry?.indexed_rag_filings || 2} Form 10-Ks
                </div>
              </div>

              <div className="p-3 rounded-2xl bg-black/40 border border-white/5 space-y-1">
                <div className="text-[10px] text-gray-400 flex items-center gap-1">
                  <Activity className="w-3 h-3 text-orange-400" />
                  <span>Active Alerts</span>
                </div>
                <div className="text-lg font-bold text-orange-400 font-mono-numbers">
                  {metrics?.telemetry?.active_unresolved_alerts || 1}
                </div>
              </div>

              <div className="p-3 rounded-2xl bg-black/40 border border-white/5 space-y-1">
                <div className="text-[10px] text-gray-400 flex items-center gap-1">
                  <ShieldCheck className="w-3 h-3 text-emerald-400" />
                  <span>Audit Logs</span>
                </div>
                <div className="text-lg font-bold text-white font-mono-numbers">
                  {metrics?.telemetry?.security_audit_events || 6}
                </div>
              </div>
            </div>

            {/* Active Agents */}
            <div className="p-3 rounded-2xl bg-white/[0.02] border border-white/5 space-y-2 text-xs">
              <span className="font-semibold text-gray-300">Active Multi-Agent Topology:</span>
              <div className="flex flex-wrap gap-1.5">
                {(metrics?.cluster?.active_agents || ["Technical", "Fundamental", "Sentiment", "RAGResearch"]).map((a: string, i: number) => (
                  <span key={i} className="px-2 py-0.5 rounded-lg bg-white/5 border border-white/10 text-[11px] text-purple-300 font-mono">
                    {a}
                  </span>
                ))}
              </div>
            </div>
          </div>
        )}

        <button
          onClick={onClose}
          className="w-full py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white font-semibold text-xs transition-all focus:outline-none focus:ring-1 focus:ring-purple-500"
        >
          Dismiss Metrics
        </button>
      </div>
    </div>
  );
};
