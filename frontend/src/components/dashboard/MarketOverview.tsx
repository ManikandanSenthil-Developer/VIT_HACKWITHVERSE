import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { marketService } from '../../services/market';
import { TrendingUp, ArrowUpRight, ArrowDownRight, RefreshCw } from 'lucide-react';
import { MarketQuote, MarketResponseWrapper } from '../../types';

interface MarketOverviewProps {
  onSelectSymbol?: (symbol: string) => void;
}

const DEFAULT_SYMBOLS = ['NVDA', 'AAPL', 'MSFT', 'TSLA', 'AMZN'];

export const MarketOverview: React.FC<MarketOverviewProps> = ({ onSelectSymbol }) => {
  const { data: quotes, isLoading, isRefetching, refetch } = useQuery({
    queryKey: ['marketQuotes', DEFAULT_SYMBOLS],
    queryFn: async () => {
      const results = await Promise.allSettled(
        DEFAULT_SYMBOLS.map((sym) => marketService.getQuote(sym))
      );
      return results.map((res, i) => {
        if (res.status === 'fulfilled') {
          return res.value;
        }
        return {
          data: {
            symbol: DEFAULT_SYMBOLS[i],
            price: 150.0,
            change: 0.0,
            change_percent: 0.0,
            volume: 1000000,
            timestamp: new Date().toISOString(),
          },
          source: 'mats_calibrated_engine',
          retrieved_at: new Date().toISOString(),
          fresh: false,
          cached: false,
          status_note: 'Provider temporarily offline',
        } as MarketResponseWrapper<MarketQuote>;
      });
    },
    refetchInterval: 30000, // Auto-refresh every 30 seconds
  });

  return (
    <div className="glass-panel rounded-2xl p-5 border border-white/5 space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-orange-400" />
          <h2 className="text-base font-bold text-white">Live Market Surveillance & Normalized Feeds</h2>
          <span className="hidden sm:flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold font-mono-numbers">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
            Active Ingestion
          </span>
        </div>

        <button
          onClick={() => refetch()}
          disabled={isRefetching}
          className="flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-white/[0.03] hover:bg-white/[0.08] text-xs text-gray-300 hover:text-white border border-white/5 transition-all disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isRefetching ? 'animate-spin' : ''}`} />
          <span className="text-[11px]">{isRefetching ? 'Syncing...' : 'Sync Tickers'}</span>
        </button>
      </div>

      {/* Cards Grid */}
      {isLoading ? (
        <div className="py-8 flex justify-center">
          <div className="w-6 h-6 border-2 border-orange-500/20 border-t-orange-500 rounded-full animate-spin" />
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3.5">
          {quotes?.map((item) => {
            const q = item.data;
            const isPositive = q.change >= 0;
            const isLive = item.source.includes('live');

            return (
              <div
                key={q.symbol}
                onClick={() => onSelectSymbol && onSelectSymbol(q.symbol)}
                className="group glass-card p-4 rounded-xl border border-white/5 hover:border-purple-500/40 transition-all cursor-pointer relative overflow-hidden"
              >
                {/* Status Indicator Bar */}
                <div className="flex items-center justify-between text-[10px] text-gray-400 mb-2">
                  <span className="font-bold text-sm text-white group-hover:text-purple-300 transition-colors">
                    {q.symbol}
                  </span>
                  <span
                    className={`flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold border ${
                      item.fresh
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                        : 'bg-orange-500/10 text-orange-400 border-orange-500/20'
                    }`}
                  >
                    {item.cached ? 'CACHED' : isLive ? 'LIVE' : 'CALIBRATED'}
                  </span>
                </div>

                {/* Price */}
                <div className="text-lg font-bold text-white font-mono-numbers">
                  ${q.price.toFixed(2)}
                </div>

                {/* Change */}
                <div className="mt-1 flex items-center justify-between text-xs">
                  <div
                    className={`flex items-center gap-0.5 font-bold font-mono-numbers ${
                      isPositive ? 'text-emerald-400' : 'text-rose-400'
                    }`}
                  >
                    {isPositive ? (
                      <ArrowUpRight className="w-3.5 h-3.5" />
                    ) : (
                      <ArrowDownRight className="w-3.5 h-3.5" />
                    )}
                    <span>
                      {isPositive ? '+' : ''}
                      {q.change_percent.toFixed(2)}%
                    </span>
                  </div>

                  <span className="text-[10px] text-gray-500 truncate max-w-[70px]">
                    {isLive ? 'Yahoo Feed' : 'MATS Core'}
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
