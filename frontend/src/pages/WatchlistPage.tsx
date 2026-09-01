import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { portfolioService } from '../services/portfolio';
import { marketService } from '../services/market';
import { ragService } from '../services/rag';
import {
  Eye,
  Plus,
  Trash2,
  Tag,
  ArrowUpRight,
  ArrowDownRight,
  BookOpen,
  X,
  ExternalLink,
  ShieldAlert,
} from 'lucide-react';
import { RagSearchResultItem } from '../types';

interface TickerCardProps {
  symbol: string;
  onOpenResearch: (symbol: string) => void;
}

const TickerCard: React.FC<TickerCardProps> = ({ symbol, onOpenResearch }) => {
  const { data: quoteRes } = useQuery({
    queryKey: ['quote', symbol],
    queryFn: () => marketService.getQuote(symbol),
    staleTime: 30000,
  });

  const quote = quoteRes?.data;
  const isPositive = quote ? quote.change >= 0 : true;

  return (
    <div className="flex items-center justify-between p-3 rounded-xl bg-white/[0.02] border border-white/5 hover:border-purple-500/30 transition-all group">
      <div className="flex items-center gap-3">
        <span className="font-bold text-sm text-white font-mono-numbers">{symbol}</span>
        {quote ? (
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-gray-200 font-mono-numbers">
              ${quote.price.toFixed(2)}
            </span>
            <span
              className={`flex items-center text-[10px] font-bold font-mono-numbers px-1.5 py-0.5 rounded ${
                isPositive
                  ? 'bg-emerald-500/10 text-emerald-400'
                  : 'bg-rose-500/10 text-rose-400'
              }`}
            >
              {isPositive ? (
                <ArrowUpRight className="w-3 h-3 inline" />
              ) : (
                <ArrowDownRight className="w-3 h-3 inline" />
              )}
              {isPositive ? '+' : ''}
              {quote.change_percent.toFixed(2)}%
            </span>
          </div>
        ) : (
          <span className="text-[10px] text-gray-500">Connecting...</span>
        )}
      </div>

      <button
        onClick={() => onOpenResearch(symbol)}
        className="px-2.5 py-1 rounded-lg bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 text-[11px] font-semibold border border-purple-500/20 transition-all flex items-center gap-1 opacity-80 group-hover:opacity-100"
      >
        <BookOpen className="w-3 h-3 text-orange-400" />
        <span>10-K Research</span>
      </button>
    </div>
  );
};

export const WatchlistPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [showAddModal, setShowAddModal] = useState(false);
  const [name, setName] = useState('');
  const [symbols, setSymbols] = useState('');
  const [description, setDescription] = useState('');

  // RAG Research Modal State
  const [researchSymbol, setResearchSymbol] = useState<string | null>(null);
  const [researchQuery, setResearchQuery] = useState('What are the key risk factors and financial results?');

  const { data: watchlists, isLoading } = useQuery({
    queryKey: ['watchlists'],
    queryFn: portfolioService.getWatchlists,
  });

  const {
    data: researchData,
    isLoading: isResearching,
    refetch: triggerResearch,
  } = useQuery({
    queryKey: ['ragModalSearch', researchSymbol, researchQuery],
    queryFn: () =>
      ragService.search({
        query: researchQuery,
        symbol: researchSymbol || undefined,
        top_k: 3,
      }),
    enabled: !!researchSymbol,
  });

  const createMutation = useMutation({
    mutationFn: portfolioService.createWatchlist,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['watchlists'] });
      setShowAddModal(false);
      setName('');
      setSymbols('');
      setDescription('');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: portfolioService.deleteWatchlist,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['watchlists'] });
    },
  });

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    createMutation.mutate({
      name,
      symbols: symbols.toUpperCase(),
      description,
    });
  };

  const handleOpenResearch = (symbol: string) => {
    setResearchSymbol(symbol);
    setResearchQuery(`What are the key business highlights, margins, and risks for ${symbol}?`);
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Eye className="w-6 h-6 text-orange-400" />
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
              Watchlist Surveillance
            </h1>
          </div>
          <p className="text-xs sm:text-sm text-gray-400 mt-1">
            Real-time normalized quotes & instant RAG knowledge retrieval across target ticker baskets
          </p>
        </div>

        <button
          onClick={() => setShowAddModal(true)}
          className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-orange-500 hover:from-purple-500 hover:to-orange-400 text-white font-semibold text-xs shadow-glow-purple flex items-center gap-2 transition-all self-start"
        >
          <Plus className="w-4 h-4" />
          <span>New Watchlist</span>
        </button>
      </div>

      {isLoading ? (
        <div className="py-20 flex justify-center">
          <div className="w-8 h-8 border-2 border-orange-500/20 border-t-orange-500 rounded-full animate-spin" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {watchlists && watchlists.length > 0 ? (
            watchlists.map((wl) => {
              const symbolList = wl.symbols
                ? wl.symbols
                    .split(',')
                    .map((s) => s.trim())
                    .filter(Boolean)
                : [];
              return (
                <div
                  key={wl.id}
                  className="glass-panel rounded-2xl p-6 border border-white/5 flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="text-lg font-bold text-white">{wl.name}</h3>
                        <p className="text-xs text-gray-400 mt-1">
                          {wl.description || 'Continuous market surveillance basket'}
                        </p>
                      </div>
                      <button
                        onClick={() => deleteMutation.mutate(wl.id)}
                        className="p-1.5 rounded-lg text-gray-500 hover:text-rose-400 hover:bg-rose-500/10 transition-colors"
                        title="Delete Watchlist"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>

                    <div className="mt-6">
                      <div className="text-[11px] uppercase tracking-wider text-gray-400 font-semibold mb-3 flex items-center gap-1.5">
                        <Tag className="w-3.5 h-3.5 text-purple-400" />
                        <span>Monitored Assets ({symbolList.length})</span>
                      </div>
                      <div className="space-y-2.5">
                        {symbolList.map((sym) => (
                          <TickerCard
                            key={sym}
                            symbol={sym}
                            onOpenResearch={handleOpenResearch}
                          />
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="mt-8 pt-4 border-t border-white/5 flex items-center justify-between text-[11px] text-gray-500">
                    <span className="flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                      Normalized Feed Online
                    </span>
                    <span className="text-purple-400 font-semibold font-mono-numbers">
                      Phase 2 Active
                    </span>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="col-span-2 glass-panel p-12 text-center rounded-2xl border border-white/5">
              <Eye className="w-10 h-10 text-gray-500 mx-auto mb-3" />
              <h3 className="text-base font-bold text-white">No Watchlists Yet</h3>
              <p className="text-xs text-gray-400 mt-1">
                Create a watchlist basket of tickers to begin surveillance.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Add Watchlist Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-md flex items-center justify-center p-4">
          <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-white/10 max-w-md w-full shadow-2xl">
            <h3 className="text-lg font-bold text-white mb-2">Create Watchlist Basket</h3>
            <p className="text-xs text-gray-400 mb-6">
              Specify equities or indices to monitor with real-time quote feeds.
            </p>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1.5">
                  Watchlist Name
                </label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Semiconductors & AI Hardware"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-black/50 border border-white/10 text-sm text-white focus:outline-none focus:border-purple-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1.5">
                  Tickers (comma separated)
                </label>
                <input
                  type="text"
                  required
                  value={symbols}
                  onChange={(e) => setSymbols(e.target.value)}
                  placeholder="NVDA, AAPL, MSFT, TSLA"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-black/50 border border-white/10 text-sm text-white focus:outline-none focus:border-purple-500 font-mono-numbers uppercase"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1.5">
                  Strategy Notes / Description
                </label>
                <textarea
                  rows={2}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Core growth assets with high data center exposure"
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
                  className="px-5 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-orange-500 text-white font-bold text-xs shadow-glow-purple"
                >
                  {createMutation.isPending ? 'Creating...' : 'Create Watchlist'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* RAG Research Modal for Specific Symbol */}
      {researchSymbol && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-md flex items-center justify-center p-4">
          <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-purple-500/30 max-w-2xl w-full shadow-2xl space-y-6">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-2xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400 font-bold font-mono-numbers">
                  {researchSymbol}
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">
                    {researchSymbol} 10-K & Regulatory Research
                  </h3>
                  <p className="text-xs text-gray-400">
                    Query verified filings with grounded vector retrieval
                  </p>
                </div>
              </div>

              <button
                onClick={() => setResearchSymbol(null)}
                className="p-2 rounded-xl bg-white/5 text-gray-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Research Query Input */}
            <div className="flex gap-2">
              <input
                type="text"
                value={researchQuery}
                onChange={(e) => setResearchQuery(e.target.value)}
                placeholder="Ask filing question..."
                className="flex-1 px-4 py-2.5 rounded-xl bg-black/50 border border-white/10 text-xs text-white focus:outline-none focus:border-purple-500"
              />
              <button
                onClick={() => triggerResearch()}
                disabled={isResearching}
                className="px-4 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow-glow-purple"
              >
                {isResearching ? 'Searching...' : 'Search'}
              </button>
            </div>

            {/* Results */}
            <div className="max-h-[350px] overflow-y-auto space-y-3 pr-1">
              {isResearching ? (
                <div className="py-12 flex justify-center">
                  <div className="w-6 h-6 border-2 border-purple-500/20 border-t-purple-500 rounded-full animate-spin" />
                </div>
              ) : researchData?.results_found && researchData.results.length > 0 ? (
                researchData.results.map((item: RagSearchResultItem, idx: number) => (
                  <div
                    key={idx}
                    className="p-4 rounded-xl bg-black/40 border border-white/5 space-y-2 text-xs"
                  >
                    <div className="flex items-center justify-between text-gray-400">
                      <span className="font-semibold text-white">
                        {item.citation.document_title}
                      </span>
                      <span className="text-[10px] font-bold font-mono-numbers px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        {Math.round(item.score * 100)}% Match
                      </span>
                    </div>

                    <p className="text-gray-300 leading-relaxed bg-white/[0.02] p-3 rounded-lg border border-white/5">
                      "{item.text}"
                    </p>

                    <div className="flex items-center justify-between text-[11px] text-gray-500">
                      <span>{item.citation.section || 'General Filing'}</span>
                      {item.citation.source_url && (
                        <a
                          href={item.citation.source_url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-purple-400 hover:text-purple-300 flex items-center gap-1"
                        >
                          <span>SEC Source</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="p-8 text-center glass-card rounded-xl border border-orange-500/20 bg-orange-950/10 space-y-2">
                  <ShieldAlert className="w-6 h-6 text-orange-400 mx-auto" />
                  <p className="text-xs font-bold text-white">
                    No reliable supporting evidence was found.
                  </p>
                  <p className="text-[11px] text-gray-400">
                    No ingested passages for {researchSymbol} matched this query above threshold.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
