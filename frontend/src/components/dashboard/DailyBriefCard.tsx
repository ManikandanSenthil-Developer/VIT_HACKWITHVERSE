import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { monitoringService } from '../../services/monitoring';
import { Sparkles, Calendar, TrendingUp, AlertTriangle, ShieldCheck } from 'lucide-react';

export const DailyBriefCard: React.FC = () => {
  const { data: brief, isLoading } = useQuery({
    queryKey: ['dailyBrief'],
    queryFn: monitoringService.getDailyBrief,
    staleTime: 60000,
  });

  if (isLoading || !brief) {
    return (
      <div className="glass-panel p-6 rounded-3xl border border-white/5 animate-pulse space-y-3">
        <div className="w-40 h-4 bg-white/10 rounded" />
        <div className="w-full h-12 bg-white/5 rounded" />
      </div>
    );
  }

  return (
    <div className="glass-panel p-6 sm:p-7 rounded-3xl border border-white/10 shadow-2xl relative overflow-hidden space-y-5 bg-gradient-to-r from-purple-950/20 via-black/40 to-black/60">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-white/5">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-orange-500/10 border border-orange-500/20 flex items-center justify-center text-orange-400">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-base sm:text-lg font-extrabold text-white tracking-tight">
              MATS Daily Financial Intelligence Brief
            </h3>
            <div className="flex items-center gap-2 text-[11px] text-gray-400 font-mono-numbers">
              <Calendar className="w-3 h-3 text-purple-400" />
              <span>{brief.date}</span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white/[0.03] border border-white/10 text-xs font-mono-numbers">
          <span className="text-gray-400">Unrealized Return:</span>
          <span
            className={`font-bold ${
              brief.portfolio_return_today_pct >= 0 ? 'text-emerald-400' : 'text-rose-400'
            }`}
          >
            {brief.portfolio_return_today_pct >= 0 ? '+' : ''}
            {brief.portfolio_return_today_pct.toFixed(2)}%
          </span>
        </div>
      </div>

      {/* Summary Narrative */}
      <p className="text-xs sm:text-sm text-gray-300 leading-relaxed font-sans">
        {brief.portfolio_summary}
      </p>

      {/* Key Developments Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Important Developments */}
        <div className="space-y-2.5">
          <span className="text-[11px] font-bold uppercase tracking-wider text-purple-400 flex items-center gap-1.5">
            <TrendingUp className="w-3.5 h-3.5" />
            Key Overnight & Intraday Signals
          </span>
          <div className="space-y-2">
            {brief.key_developments.map((dev, i) => (
              <div
                key={i}
                className="p-3 rounded-2xl bg-black/40 border border-white/5 space-y-1 text-xs"
              >
                <div className="flex items-center justify-between">
                  <span className="font-bold text-white">{dev.symbol}</span>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-purple-500/10 text-purple-300 border border-purple-500/20">
                    {dev.priority}
                  </span>
                </div>
                <h5 className="text-[11px] font-semibold text-gray-300">{dev.title}</h5>
                <p className="text-[10px] text-gray-400 leading-relaxed">{dev.summary}</p>
              </div>
            ))}
          </div>
        </div>

        {/* What Deserves Attention & Changes */}
        <div className="space-y-4">
          <div className="space-y-2">
            <span className="text-[11px] font-bold uppercase tracking-wider text-orange-400 flex items-center gap-1.5">
              <AlertTriangle className="w-3.5 h-3.5" />
              What Deserves Attention
            </span>
            <ul className="space-y-1.5 text-xs text-gray-300">
              {brief.what_deserves_attention.map((item, i) => (
                <li key={i} className="p-2.5 rounded-xl bg-black/40 border border-white/5 leading-relaxed">
                  • {item}
                </li>
              ))}
            </ul>
          </div>

          <div className="p-3 rounded-xl bg-emerald-950/20 border border-emerald-500/20 text-[11px] text-emerald-300 flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 shrink-0" />
            <span>Autonomous Surveillance Loop is active across all watched tickers.</span>
          </div>
        </div>
      </div>
    </div>
  );
};
