import React from 'react';
import { ShieldAlert, Zap, AlertTriangle, RefreshCw, ChevronRight } from 'lucide-react';
import { AiAlert } from '../../types';

interface AlertsPanelProps {
  alerts: AiAlert[];
}

const alertIcons = {
  opportunity: Zap,
  risk: AlertTriangle,
  anomaly: ShieldAlert,
  rebalance: RefreshCw,
};

const badgeStyles = {
  opportunity: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  risk: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
  anomaly: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
  rebalance: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
};

export const AlertsPanel: React.FC<AlertsPanelProps> = ({ alerts }) => {
  return (
    <div className="glass-panel rounded-2xl p-6 border border-white/5 flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-purple-500 animate-pulse" />
          <h2 className="text-lg font-bold text-white">AI Alerts & Insights</h2>
        </div>
        <span className="text-xs px-2 py-0.5 rounded-full bg-white/5 text-gray-400 border border-white/10 font-mono-numbers">
          {alerts.length} Live Signals
        </span>
      </div>

      {/* Feed list */}
      <div className="space-y-3.5 overflow-y-auto max-h-[480px] pr-1">
        {alerts.map((alert) => {
          const Icon = alertIcons[alert.type];
          return (
            <div
              key={alert.id}
              className="group p-4 rounded-xl glass-card border border-white/5 hover:border-purple-500/30 transition-all cursor-pointer relative"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-center gap-2">
                  <span
                    className={`p-1.5 rounded-lg border text-xs font-semibold ${
                      badgeStyles[alert.type]
                    }`}
                  >
                    <Icon className="w-3.5 h-3.5" />
                  </span>
                  <span className="text-xs font-semibold uppercase tracking-wider text-gray-300">
                    {alert.type}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-[11px] text-gray-400 font-mono-numbers">
                  <span>{alert.timestamp}</span>
                  {alert.symbol && (
                    <span className="px-1.5 py-0.5 rounded bg-purple-500/15 text-purple-300 border border-purple-500/30 font-bold">
                      {alert.symbol}
                    </span>
                  )}
                </div>
              </div>

              <h4 className="text-sm font-semibold text-white mt-2.5 group-hover:text-purple-300 transition-colors">
                {alert.title}
              </h4>
              <p className="text-xs text-gray-400 mt-1 leading-relaxed">
                {alert.description}
              </p>

              <div className="mt-3 flex items-center justify-between pt-2.5 border-t border-white/5">
                <div className="flex items-center gap-2">
                  <span className="text-[11px] text-gray-400">Confidence:</span>
                  <div className="w-16 h-1.5 bg-gray-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-purple-500 to-orange-500 rounded-full"
                      style={{ width: `${alert.confidence}%` }}
                    />
                  </div>
                  <span className="text-[11px] font-bold text-white font-mono-numbers">
                    {alert.confidence}%
                  </span>
                </div>
                <span className="text-gray-400 group-hover:text-purple-400 transition-colors">
                  <ChevronRight className="w-4 h-4" />
                </span>
              </div>
            </div>
          );
        })}
      </div>

      <button className="mt-auto pt-4 w-full text-center text-xs font-medium text-purple-400 hover:text-purple-300 transition-colors">
        View All Intelligence Feeds &rarr;
      </button>
    </div>
  );
};
