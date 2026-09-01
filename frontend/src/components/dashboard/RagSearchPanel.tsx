import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ragService } from '../../services/rag';
import {
  Search,
  BookOpen,
  FileText,
  ExternalLink,
  ShieldAlert,
  Sparkles,
  Plus,
  CheckCircle2,
} from 'lucide-react';
import { RagSearchResultItem } from '../../types';

export const RagSearchPanel: React.FC = () => {
  const queryClient = useQueryClient();

  const [query, setQuery] = useState('');
  const [selectedSymbol, setSelectedSymbol] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'search' | 'documents'>('search');

  // Ingestion Modal State
  const [showIngestModal, setShowIngestModal] = useState(false);
  const [ingestTitle, setIngestTitle] = useState('');
  const [ingestSymbol, setIngestSymbol] = useState('NVDA');
  const [ingestDocType, setIngestDocType] = useState('10-K');
  const [ingestContent, setIngestContent] = useState('');
  const [ingestUrl, setIngestUrl] = useState('');

  // RAG Search Query
  const {
    data: searchData,
    isLoading: isSearching,
    refetch: triggerSearch,
  } = useQuery({
    queryKey: ['ragSearch', query, selectedSymbol],
    queryFn: () =>
      ragService.search({
        query: query.trim(),
        symbol: selectedSymbol || undefined,
        top_k: 4,
      }),
    enabled: false,
  });

  // Documents Query
  const { data: documents, isLoading: isLoadingDocs } = useQuery({
    queryKey: ['ragDocuments', selectedSymbol],
    queryFn: () => ragService.getDocuments(selectedSymbol || undefined),
  });

  // Ingestion Mutation
  const ingestMutation = useMutation({
    mutationFn: ragService.ingest,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ragDocuments'] });
      setShowIngestModal(false);
      setIngestTitle('');
      setIngestContent('');
      setIngestUrl('');
    },
  });

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    triggerSearch();
  };

  const handleIngestSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!ingestTitle || (!ingestContent && !ingestUrl)) return;
    ingestMutation.mutate({
      title: ingestTitle,
      company_symbol: ingestSymbol.toUpperCase(),
      document_type: ingestDocType,
      content: ingestContent || undefined,
      source_url: ingestUrl || undefined,
    });
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border border-white/5 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-purple-400" />
            <h2 className="text-lg font-bold text-white">
              Financial RAG Knowledge Engine & Citations
            </h2>
            <span className="flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full bg-purple-500/10 text-purple-300 border border-purple-500/20 font-semibold">
              <Sparkles className="w-3 h-3 text-orange-400" />
              Verified SEC Filings
            </span>
          </div>
          <p className="text-xs text-gray-400 mt-1">
            Perform institutional semantic search across 10-K, 10-Q, and regulatory disclosures with strict source traceability
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center bg-black/40 p-1 rounded-xl border border-white/5">
            <button
              onClick={() => setActiveTab('search')}
              className={`px-3 py-1 text-xs font-semibold rounded-lg transition-all ${
                activeTab === 'search'
                  ? 'bg-purple-600 text-white shadow-glow-purple'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Research Terminal
            </button>
            <button
              onClick={() => setActiveTab('documents')}
              className={`px-3 py-1 text-xs font-semibold rounded-lg transition-all ${
                activeTab === 'documents'
                  ? 'bg-purple-600 text-white shadow-glow-purple'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Ingested Filings ({documents?.length || 0})
            </button>
          </div>

          <button
            onClick={() => setShowIngestModal(true)}
            className="px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-purple-600 to-orange-500 hover:from-purple-500 hover:to-orange-400 text-white font-semibold text-xs shadow-glow-purple flex items-center gap-1.5 transition-all"
          >
            <Plus className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Ingest Filing</span>
          </button>
        </div>
      </div>

      {activeTab === 'search' ? (
        <div className="space-y-6">
          {/* Query Bar */}
          <form onSubmit={handleSearchSubmit} className="space-y-3">
            <div className="flex flex-col sm:flex-row items-stretch gap-2.5">
              <div className="relative flex-1">
                <Search className="w-4 h-4 text-gray-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Ask financial question: e.g. What are NVIDIA's supply chain risks with TSMC?"
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-black/50 border border-white/10 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 transition-all font-sans"
                />
              </div>

              {/* Symbol selector */}
              <div className="flex items-center gap-2">
                <select
                  value={selectedSymbol}
                  onChange={(e) => setSelectedSymbol(e.target.value)}
                  className="px-3 py-2.5 rounded-xl bg-black/50 border border-white/10 text-xs text-white focus:outline-none focus:border-purple-500 font-mono-numbers"
                >
                  <option value="">All Tickers</option>
                  <option value="NVDA">NVDA (NVIDIA)</option>
                  <option value="AAPL">AAPL (Apple)</option>
                  <option value="MSFT">MSFT (Microsoft)</option>
                  <option value="TSLA">TSLA (Tesla)</option>
                </select>

                <button
                  type="submit"
                  disabled={isSearching || !query.trim()}
                  className="px-5 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow-glow-purple transition-all disabled:opacity-40 flex items-center gap-2"
                >
                  {isSearching ? (
                    <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                  ) : (
                    <span>Search RAG</span>
                  )}
                </button>
              </div>
            </div>

            {/* Suggested quick queries */}
            <div className="flex flex-wrap items-center gap-2 text-[11px] text-gray-400">
              <span className="font-semibold text-gray-500">Quick queries:</span>
              {[
                'What are NVIDIA supply chain risks?',
                'What drove Apple Services revenue record?',
                'Data Center gross margin expansion',
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  type="button"
                  onClick={() => {
                    setQuery(suggestion);
                  }}
                  className="px-2.5 py-0.5 rounded-lg bg-white/[0.03] hover:bg-white/[0.08] text-purple-300 border border-purple-500/20 transition-colors"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </form>

          {/* Results Area */}
          {searchData && (
            <div className="space-y-4">
              <div className="flex items-center justify-between text-xs text-gray-400 pb-2 border-b border-white/5">
                <span>
                  Query execution:{' '}
                  <strong className="text-white font-mono-numbers">{searchData.query_latency_ms}ms</strong>
                </span>
                <span className="font-mono-numbers">
                  {searchData.results.length} supporting passages retrieved
                </span>
              </div>

              {searchData.results_found && searchData.results.length > 0 ? (
                <div className="grid grid-cols-1 gap-4">
                  {searchData.results.map((item: RagSearchResultItem, idx: number) => {
                    const matchPercent = Math.round(item.score * 100);
                    return (
                      <div
                        key={idx}
                        className="glass-card p-5 rounded-2xl border border-white/5 hover:border-purple-500/40 transition-all space-y-3"
                      >
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <div className="flex items-center gap-2">
                            <span className="px-2 py-0.5 rounded bg-purple-500/15 text-purple-300 border border-purple-500/30 text-xs font-bold font-mono-numbers">
                              {item.citation.company_symbol}
                            </span>
                            <span className="font-bold text-xs text-white">
                              {item.citation.document_title}
                            </span>
                            {item.citation.section && (
                              <span className="text-[11px] text-gray-400 bg-white/5 px-2 py-0.5 rounded">
                                {item.citation.section}
                              </span>
                            )}
                          </div>

                          <div className="flex items-center gap-2">
                            <span className="text-[11px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold font-mono-numbers">
                              {matchPercent}% Relevance
                            </span>
                            {item.citation.source_url && (
                              <a
                                href={item.citation.source_url}
                                target="_blank"
                                rel="noreferrer"
                                className="text-gray-400 hover:text-purple-400 p-1 rounded transition-colors"
                                title="View Original SEC Source"
                              >
                                <ExternalLink className="w-3.5 h-3.5" />
                              </a>
                            )}
                          </div>
                        </div>

                        {/* Passage text */}
                        <p className="text-xs text-gray-300 leading-relaxed bg-black/30 p-3.5 rounded-xl border border-white/5 font-sans">
                          "{item.text}"
                        </p>

                        {/* Citation provenance footer */}
                        <div className="flex items-center justify-between text-[11px] text-gray-500 pt-1">
                          <span className="flex items-center gap-1 font-mono-numbers">
                            <FileText className="w-3 h-3 text-purple-400" />
                            Doc ID #{item.citation.document_id} • Page {item.citation.page_number || 1}
                          </span>
                          <span className="text-purple-400/80">Traceable SEC Citation</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                /* Strict RAG Quality Rule Fallback Banner */
                <div className="p-8 rounded-2xl glass-card border border-orange-500/20 text-center space-y-3 bg-orange-950/10">
                  <div className="w-10 h-10 rounded-full bg-orange-500/10 border border-orange-500/30 text-orange-400 flex items-center justify-center mx-auto">
                    <ShieldAlert className="w-5 h-5" />
                  </div>
                  <h4 className="text-sm font-bold text-white">
                    No reliable supporting evidence was found.
                  </h4>
                  <p className="text-xs text-gray-400 max-w-md mx-auto leading-relaxed">
                    Under strict MATS financial governance rules, ungrounded claims are never fabricated. 
                    No ingested filing passages met the similarity confidence threshold for this query.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      ) : (
        /* Ingested Documents List Tab */
        <div className="space-y-4">
          {isLoadingDocs ? (
            <div className="py-12 flex justify-center">
              <div className="w-6 h-6 border-2 border-purple-500/20 border-t-purple-500 rounded-full animate-spin" />
            </div>
          ) : documents && documents.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {documents.map((doc) => (
                <div
                  key={doc.id}
                  className="glass-card p-5 rounded-2xl border border-white/5 space-y-3"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 rounded bg-purple-500/15 text-purple-300 border border-purple-500/30 text-xs font-bold font-mono-numbers">
                          {doc.company_symbol}
                        </span>
                        <span className="text-xs font-bold text-orange-400 uppercase">
                          {doc.document_type}
                        </span>
                      </div>
                      <h4 className="text-sm font-bold text-white mt-1.5">{doc.title}</h4>
                    </div>

                    <span className="flex items-center gap-1 text-[10px] font-semibold text-emerald-400 px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20">
                      <CheckCircle2 className="w-3 h-3" />
                      {doc.status}
                    </span>
                  </div>

                  <div className="pt-2 border-t border-white/5 flex items-center justify-between text-xs text-gray-400 font-mono-numbers">
                    <span>{doc.chunk_count} Semantic Chunks</span>
                    {doc.source_url && (
                      <a
                        href={doc.source_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-purple-400 hover:text-purple-300 flex items-center gap-1"
                      >
                        <span>SEC Edgar</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-12 text-center text-xs text-gray-500">
              No documents ingested yet. Click "Ingest Filing" to add your first official filing.
            </div>
          )}
        </div>
      )}

      {/* Ingest Document Modal */}
      {showIngestModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-md flex items-center justify-center p-4">
          <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-white/10 max-w-lg w-full shadow-2xl space-y-6">
            <div>
              <h3 className="text-lg font-bold text-white">Ingest Official Financial Filing</h3>
              <p className="text-xs text-gray-400 mt-1">
                Submissions are validated, chunked, and embedded into 384-dimensional dense vectors.
              </p>
            </div>

            <form onSubmit={handleIngestSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1.5">
                  Document Title
                </label>
                <input
                  type="text"
                  required
                  value={ingestTitle}
                  onChange={(e) => setIngestTitle(e.target.value)}
                  placeholder="e.g. Microsoft Corporation FY2025 10-K Report"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-black/50 border border-white/10 text-xs text-white focus:outline-none focus:border-purple-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-gray-300 mb-1.5">
                    Ticker Symbol
                  </label>
                  <input
                    type="text"
                    required
                    value={ingestSymbol}
                    onChange={(e) => setIngestSymbol(e.target.value.toUpperCase())}
                    placeholder="NVDA, MSFT, AAPL"
                    className="w-full px-3.5 py-2.5 rounded-xl bg-black/50 border border-white/10 text-xs text-white focus:outline-none focus:border-purple-500 font-mono-numbers uppercase"
                  />
                </div>

                <div>
                  <label className="block text-xs font-semibold text-gray-300 mb-1.5">
                    Filing Type
                  </label>
                  <select
                    value={ingestDocType}
                    onChange={(e) => setIngestDocType(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl bg-black/50 border border-white/10 text-xs text-white focus:outline-none focus:border-purple-500"
                  >
                    <option value="10-K">10-K (Annual)</option>
                    <option value="10-Q">10-Q (Quarterly)</option>
                    <option value="8-K">8-K (Current Event)</option>
                    <option value="Presentation">Investor Presentation</option>
                    <option value="Disclosure">Press Disclosure</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1.5">
                  Official Source URL (Validated SEC / Investor Relations)
                </label>
                <input
                  type="url"
                  value={ingestUrl}
                  onChange={(e) => setIngestUrl(e.target.value)}
                  placeholder="https://www.sec.gov/edgar/data/..."
                  className="w-full px-3.5 py-2.5 rounded-xl bg-black/50 border border-white/10 text-xs text-white focus:outline-none focus:border-purple-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-300 mb-1.5">
                  Document Text (Paste Excerpts or Full Content)
                </label>
                <textarea
                  rows={6}
                  value={ingestContent}
                  onChange={(e) => setIngestContent(e.target.value)}
                  placeholder="Paste textual excerpts containing Item 1 Business, Item 1A Risk Factors, or MD&A disclosures..."
                  className="w-full px-3.5 py-2.5 rounded-xl bg-black/50 border border-white/10 text-xs text-white focus:outline-none focus:border-purple-500"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-white/5">
                <button
                  type="button"
                  onClick={() => setShowIngestModal(false)}
                  className="px-4 py-2 rounded-xl text-xs text-gray-400 hover:text-white"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={ingestMutation.isPending}
                  className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-orange-500 text-white font-bold text-xs shadow-glow-purple"
                >
                  {ingestMutation.isPending ? 'Processing & Embedding...' : 'Ingest & Embed'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
