import React, { useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { intelligenceService } from '../../services/intelligence';
import {
  Cpu,
  Sparkles,
  Send,
  CheckCircle2,
  AlertTriangle,
  ShieldAlert,
  ChevronDown,
  ChevronUp,
  Clock,
  Layers,
  ExternalLink,
  Zap,
  BarChart3,
  BookOpen,
  Scale,
  UserCheck,
  FileText,
} from 'lucide-react';
import {
  AnalysisResponse,
  AgentFinding,
  SignalConflict,
} from '../../types';
import { ExportReportModal } from '../common/ExportReportModal';

export const IntelligenceTerminal: React.FC = () => {
  const [query, setQuery] = useState('Perform a complete research-oriented analysis of NVDA for long-term investment.');
  const [symbol, setSymbol] = useState('NVDA');
  const [analysisType, setAnalysisType] = useState('auto');
  const [showReasoningTrace, setShowReasoningTrace] = useState(false);
  const [showSources, setShowSources] = useState(false);
  const [showExportModal, setShowExportModal] = useState(false);

  // Available agent catalog
  const { data: agentCatalog } = useQuery({
    queryKey: ['intelligenceAgents'],
    queryFn: intelligenceService.getAgents,
  });

  // Multi-agent execution mutation
  const analyzeMutation = useMutation({
    mutationFn: intelligenceService.analyze,
  });

  const handleExecute = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || !symbol.trim()) return;
    analyzeMutation.mutate({
      query: query.trim(),
      symbol: symbol.trim().toUpperCase(),
      analysis_type: analysisType,
    });
  };

  const setPromptPreset = (newSymbol: string, newQuery: string, type: string = 'comprehensive') => {
    setSymbol(newSymbol);
    setQuery(newQuery);
    setAnalysisType(type);
  };

  const result: AnalysisResponse | undefined = analyzeMutation.data;

  const getSignalBadgeColor = (signal: string) => {
    switch (signal) {
      case 'BULLISH':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'BEARISH':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      case 'CAUTIOUS':
        return 'bg-orange-500/10 text-orange-400 border-orange-500/30';
      default:
        return 'bg-purple-500/10 text-purple-300 border-purple-500/30';
    }
  };

  return (
    <div className="glass-panel rounded-3xl p-6 sm:p-8 border border-white/10 shadow-2xl space-y-8 relative overflow-hidden">
      {/* Background ambient glow */}
      <div className="absolute top-0 right-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 left-1/3 w-80 h-80 bg-orange-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
        <div>
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-2xl bg-gradient-to-tr from-purple-600 to-orange-500 p-0.5 shadow-glow-purple flex items-center justify-center">
              <div className="w-full h-full bg-[#0d091a] rounded-[14px] flex items-center justify-center">
                <Cpu className="w-5 h-5 text-purple-300" />
              </div>
            </div>
            <div>
              <h2 className="text-xl sm:text-2xl font-extrabold text-white tracking-tight">
                MATS Multi-Agent Intelligence Engine
              </h2>
              <p className="text-xs text-gray-400">
                Coordinated autonomous agents • Conflict detection • Grounded SEC citations • Personalization
              </p>
            </div>
          </div>
        </div>

        {/* Live status badge */}
        <div className="flex items-center gap-2">
          <div className="px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold flex items-center gap-2 font-mono-numbers">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            <span>{agentCatalog?.length || 4} Specialized Agents Online</span>
          </div>
        </div>
      </div>

      {/* Query Bar */}
      <form onSubmit={handleExecute} className="space-y-4 relative z-10">
        <div className="flex flex-col lg:flex-row items-stretch gap-3">
          <div className="w-full lg:w-36">
            <label className="block text-[11px] font-semibold text-gray-400 mb-1">
              Target Ticker
            </label>
            <input
              type="text"
              required
              value={symbol}
              onChange={(e) => setSymbol(e.target.value.toUpperCase())}
              placeholder="NVDA"
              className="w-full px-3.5 py-3 rounded-2xl bg-black/50 border border-white/10 text-sm font-bold text-white uppercase font-mono-numbers focus:outline-none focus:border-purple-500 transition-all"
            />
          </div>

          <div className="flex-1">
            <label className="block text-[11px] font-semibold text-gray-400 mb-1">
              Financial Research Query
            </label>
            <div className="relative">
              <input
                type="text"
                required
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask financial question: e.g. Analyze NVDA for long-term investment..."
                className="w-full pl-4 pr-12 py-3 rounded-2xl bg-black/50 border border-white/10 text-xs sm:text-sm text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 transition-all"
              />
              <button
                type="submit"
                disabled={analyzeMutation.isPending || !query.trim() || !symbol.trim()}
                className="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-xl bg-gradient-to-r from-purple-600 to-orange-500 text-white hover:opacity-90 transition-all disabled:opacity-40 shadow-glow-purple"
                title="Execute Multi-Agent Analysis"
              >
                {analyzeMutation.isPending ? (
                  <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </button>
            </div>
          </div>

          <div className="w-full lg:w-48">
            <label className="block text-[11px] font-semibold text-gray-400 mb-1">
              Routing Strategy
            </label>
            <select
              value={analysisType}
              onChange={(e) => setAnalysisType(e.target.value)}
              className="w-full px-3.5 py-3 rounded-2xl bg-black/50 border border-white/10 text-xs text-white focus:outline-none focus:border-purple-500 transition-all"
            >
              <option value="comprehensive">Comprehensive (All Agents)</option>
              <option value="technical">Technical Only</option>
              <option value="fundamental">Fundamental Only</option>
              <option value="auto">Auto Intent Routing</option>
            </select>
          </div>
        </div>

        {/* Query Presets Chips */}
        <div className="flex flex-wrap items-center gap-2 pt-1 text-[11px]">
          <span className="text-gray-500 font-semibold flex items-center gap-1">
            <Sparkles className="w-3 h-3 text-orange-400" />
            Quick Presets:
          </span>
          <button
            type="button"
            onClick={() =>
              setPromptPreset(
                'NVDA',
                'Perform a complete research-oriented analysis of NVDA for long-term investment.',
                'comprehensive'
              )
            }
            className="px-2.5 py-1 rounded-xl bg-white/[0.03] hover:bg-white/[0.08] text-purple-300 border border-purple-500/20 transition-all"
          >
            NVDA Comprehensive
          </button>
          <button
            type="button"
            onClick={() =>
              setPromptPreset(
                'AAPL',
                'What is the technical momentum and RSI trend for AAPL?',
                'technical'
              )
            }
            className="px-2.5 py-1 rounded-xl bg-white/[0.03] hover:bg-white/[0.08] text-purple-300 border border-purple-500/20 transition-all"
          >
            AAPL Technical & RSI
          </button>
          <button
            type="button"
            onClick={() =>
              setPromptPreset(
                'MSFT',
                'Audit balance sheet debt to equity, operating margins, and free cash flow for MSFT.',
                'fundamental'
              )
            }
            className="px-2.5 py-1 rounded-xl bg-white/[0.03] hover:bg-white/[0.08] text-purple-300 border border-purple-500/20 transition-all"
          >
            MSFT Fundamentals
          </button>
          <button
            type="button"
            onClick={() =>
              setPromptPreset(
                'TSLA',
                'Analyze supply chain and regulatory risks documented in TSLA official filings.',
                'comprehensive'
              )
            }
            className="px-2.5 py-1 rounded-xl bg-white/[0.03] hover:bg-white/[0.08] text-purple-300 border border-purple-500/20 transition-all"
          >
            TSLA Risk Disclosures
          </button>
        </div>
      </form>

      {/* Visual Multi-Agent Pipeline Representation */}
      <div className="p-4 rounded-2xl bg-black/40 border border-white/5 space-y-3">
        <div className="flex items-center justify-between text-xs text-gray-400">
          <span className="flex items-center gap-1.5 font-semibold text-gray-300">
            <Layers className="w-3.5 h-3.5 text-purple-400" />
            Parallel Agent Pipeline Architecture
          </span>
          {result && (
            <span className="text-[11px] font-mono-numbers text-emerald-400 flex items-center gap-1">
              <Clock className="w-3 h-3" />
              Completed in {result.execution_time_ms}ms
            </span>
          )}
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-7 gap-2 items-center text-center">
          {/* 1. Technical */}
          <div className={`p-2.5 rounded-xl border transition-all ${
            result?.successful_agents.includes('technical')
              ? 'bg-purple-950/20 border-purple-500/40 text-purple-200'
              : analyzeMutation.isPending
              ? 'bg-white/[0.02] border-white/10 animate-pulse text-gray-400'
              : 'bg-white/[0.01] border-white/5 text-gray-500'
          }`}>
            <BarChart3 className="w-4 h-4 mx-auto mb-1 text-purple-400" />
            <div className="text-[11px] font-bold">Technical</div>
            <div className="text-[9px] text-gray-400">Momentum</div>
          </div>

          {/* 2. Fundamental */}
          <div className={`p-2.5 rounded-xl border transition-all ${
            result?.successful_agents.includes('fundamental')
              ? 'bg-purple-950/20 border-purple-500/40 text-purple-200'
              : analyzeMutation.isPending
              ? 'bg-white/[0.02] border-white/10 animate-pulse text-gray-400'
              : 'bg-white/[0.01] border-white/5 text-gray-500'
          }`}>
            <Scale className="w-4 h-4 mx-auto mb-1 text-orange-400" />
            <div className="text-[11px] font-bold">Fundamental</div>
            <div className="text-[9px] text-gray-400">Valuation</div>
          </div>

          {/* 3. Sentiment */}
          <div className={`p-2.5 rounded-xl border transition-all ${
            result?.successful_agents.includes('sentiment')
              ? 'bg-purple-950/20 border-purple-500/40 text-purple-200'
              : analyzeMutation.isPending
              ? 'bg-white/[0.02] border-white/10 animate-pulse text-gray-400'
              : 'bg-white/[0.01] border-white/5 text-gray-500'
          }`}>
            <Zap className="w-4 h-4 mx-auto mb-1 text-yellow-400" />
            <div className="text-[11px] font-bold">Sentiment</div>
            <div className="text-[9px] text-gray-400">Anomalies</div>
          </div>

          {/* 4. RAG Research */}
          <div className={`p-2.5 rounded-xl border transition-all ${
            result?.successful_agents.includes('rag_research')
              ? 'bg-purple-950/20 border-purple-500/40 text-purple-200'
              : analyzeMutation.isPending
              ? 'bg-white/[0.02] border-white/10 animate-pulse text-gray-400'
              : 'bg-white/[0.01] border-white/5 text-gray-500'
          }`}>
            <BookOpen className="w-4 h-4 mx-auto mb-1 text-emerald-400" />
            <div className="text-[11px] font-bold">RAG Research</div>
            <div className="text-[9px] text-gray-400">SEC Citations</div>
          </div>

          {/* 5. Conflict Detector */}
          <div className={`p-2.5 rounded-xl border transition-all ${
            result
              ? result.conflicts.length > 0
                ? 'bg-orange-950/20 border-orange-500/40 text-orange-200'
                : 'bg-emerald-950/20 border-emerald-500/40 text-emerald-200'
              : 'bg-white/[0.01] border-white/5 text-gray-500'
          }`}>
            <ShieldAlert className="w-4 h-4 mx-auto mb-1 text-orange-400" />
            <div className="text-[11px] font-bold">Conflict Check</div>
            <div className="text-[9px] text-gray-400">
              {result ? `${result.conflicts.length} Signals` : 'Scan'}
            </div>
          </div>

          {/* 6. Synthesis */}
          <div className={`p-2.5 rounded-xl border transition-all ${
            result
              ? 'bg-purple-950/20 border-purple-500/40 text-purple-200'
              : 'bg-white/[0.01] border-white/5 text-gray-500'
          }`}>
            <Cpu className="w-4 h-4 mx-auto mb-1 text-purple-400" />
            <div className="text-[11px] font-bold">Synthesis</div>
            <div className="text-[9px] text-gray-400">Harmonize</div>
          </div>

          {/* 7. Personalization */}
          <div className={`p-2.5 rounded-xl border transition-all ${
            result
              ? 'bg-gradient-to-tr from-purple-600/30 to-orange-500/30 border-purple-500/40 text-white shadow-glow-purple'
              : 'bg-white/[0.01] border-white/5 text-gray-500'
          }`}>
            <UserCheck className="w-4 h-4 mx-auto mb-1 text-emerald-400" />
            <div className="text-[11px] font-bold">Personalized</div>
            <div className="text-[9px] text-gray-400">Profile Frame</div>
          </div>
        </div>
      </div>

      {/* Loading state indicator */}
      {analyzeMutation.isPending && (
        <div className="p-12 text-center glass-card rounded-2xl border border-purple-500/20 space-y-4">
          <div className="w-10 h-10 border-2 border-purple-500/20 border-t-purple-500 rounded-full animate-spin mx-auto" />
          <div>
            <h4 className="text-sm font-bold text-white">Decomposing & Executing Specialized Agents...</h4>
            <p className="text-xs text-gray-400 mt-1">
              Querying live OHLCV bars, corporate balance sheets, volume distributions, and official SEC filings in parallel.
            </p>
          </div>
        </div>
      )}

      {/* Disclosures for partial failure or missing agents */}
      {result && result.disclosures.length > 0 && (
        <div className="p-4 rounded-2xl bg-orange-950/20 border border-orange-500/30 space-y-2">
          <div className="flex items-center gap-2 text-xs font-bold text-orange-400">
            <AlertTriangle className="w-4 h-4" />
            <span>Agent Availability Disclosure</span>
          </div>
          <ul className="text-xs text-gray-300 list-disc list-inside space-y-1">
            {result.disclosures.map((d, i) => (
              <li key={i}>{d}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Main Results Container */}
      {result && (
        <div className="space-y-6">
          {/* Top Recommendation & Overall Assessment Card */}
          <div className="glass-card p-6 sm:p-8 rounded-3xl border border-purple-500/30 space-y-6 bg-gradient-to-br from-purple-950/20 via-black/40 to-black/60 shadow-2xl">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-white/5">
              <div>
                <span className="text-[10px] uppercase font-bold tracking-widest text-purple-400">
                  MATS Autonomous Synthesis
                </span>
                <h3 className="text-xl sm:text-2xl font-extrabold text-white mt-1">
                  {result.recommendation.assessment}
                </h3>
              </div>

              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => setShowExportModal(true)}
                  aria-label="Export intelligence report"
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-purple-600/20 hover:bg-purple-600/30 text-purple-300 border border-purple-500/30 text-xs font-semibold transition-all shadow-sm focus:outline-none focus:ring-1 focus:ring-purple-400"
                >
                  <FileText className="w-3.5 h-3.5" />
                  <span>Export Report</span>
                </button>
                <div className="text-right">
                  <div className="text-[11px] text-gray-400 font-semibold">Synthesis Confidence</div>
                  <div className="text-lg font-extrabold text-emerald-400 font-mono-numbers">
                    {(result.confidence * 100).toFixed(0)}%
                  </div>
                </div>
                <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                  <CheckCircle2 className="w-6 h-6" />
                </div>
              </div>
            </div>

            {/* Personalization Framing Note */}
            {result.recommendation.personalization_note && (
              <div className="p-3.5 rounded-2xl bg-purple-500/10 border border-purple-500/20 text-xs text-purple-200 flex items-start gap-2.5">
                <UserCheck className="w-4 h-4 text-orange-400 shrink-0 mt-0.5" />
                <span>{result.recommendation.personalization_note}</span>
              </div>
            )}

            {/* Key Reasons & Risks Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Supporting Factors */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold text-gray-300 uppercase tracking-wider flex items-center gap-2">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                  Key Supporting Drivers
                </h4>
                <div className="space-y-2">
                  {result.recommendation.key_reasons.map((r, i) => (
                    <div
                      key={i}
                      className="p-3 rounded-xl bg-white/[0.02] border border-white/5 text-xs text-gray-300 leading-relaxed"
                    >
                      {r}
                    </div>
                  ))}
                </div>
              </div>

              {/* Key Risks & Opposing Factors */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold text-gray-300 uppercase tracking-wider flex items-center gap-2">
                  <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
                  Opposing Risks & Limitations
                </h4>
                <div className="space-y-2">
                  {result.recommendation.risks.map((r, i) => (
                    <div
                      key={i}
                      className="p-3 rounded-xl bg-white/[0.02] border border-white/5 text-xs text-gray-300 leading-relaxed"
                    >
                      {r}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* What to monitor */}
            <div className="pt-4 border-t border-white/5 space-y-2">
              <span className="text-[11px] font-bold uppercase tracking-wider text-orange-400">
                Actionable Watchlist Monitoring:
              </span>
              <ul className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs text-gray-300">
                {result.recommendation.what_to_monitor.map((item, i) => (
                  <li key={i} className="p-2.5 rounded-xl bg-black/40 border border-white/5">
                    • {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Conflict Detector Alert Banner (If Any) */}
          {result.conflicts.length > 0 && (
            <div className="glass-card p-6 rounded-3xl border border-orange-500/30 bg-orange-950/20 space-y-4">
              <div className="flex items-center gap-2.5">
                <ShieldAlert className="w-5 h-5 text-orange-400" />
                <div>
                  <h4 className="text-sm font-bold text-white">
                    Signal Divergence Detected ({result.conflicts.length} Disconnects)
                  </h4>
                  <p className="text-xs text-gray-400">
                    MATS isolated conflicting inputs rather than muting disagreements into an average.
                  </p>
                </div>
              </div>

              <div className="space-y-3">
                {result.conflicts.map((c: SignalConflict, i: number) => (
                  <div
                    key={i}
                    className="p-4 rounded-2xl bg-black/50 border border-orange-500/20 space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-orange-300 font-mono-numbers">
                        {c.conflict_type}
                      </span>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-orange-500/10 text-orange-400 border border-orange-500/20 uppercase">
                        {c.severity} severity
                      </span>
                    </div>

                    <p className="text-xs text-gray-300 leading-relaxed">{c.description}</p>

                    <div className="flex flex-wrap gap-2 pt-1">
                      {Object.entries(c.conflicting_signals).map(([ag, sig]) => (
                        <span
                          key={ag}
                          className="px-2 py-0.5 rounded bg-white/5 text-[10px] text-gray-400 font-semibold"
                        >
                          {ag}: <strong className="text-white">{sig}</strong>
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Multi-Agent Findings Grid */}
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Cpu className="w-4 h-4 text-purple-400" />
              Specialized Agent Deep Dives ({result.agents.length} Consulted)
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {result.agents.map((agent: AgentFinding, i: number) => (
                <div
                  key={i}
                  className="glass-card p-5 rounded-2xl border border-white/5 hover:border-purple-500/40 transition-all space-y-3 flex flex-col justify-between"
                >
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-white uppercase tracking-wider">
                          {agent.agent.replace('_', ' ')} Agent
                        </span>
                      </div>

                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${getSignalBadgeColor(
                          agent.signal
                        )}`}
                      >
                        {agent.signal} • {(agent.confidence * 100).toFixed(0)}% Conf
                      </span>
                    </div>

                    <p className="text-xs text-gray-300 leading-relaxed">{agent.finding}</p>

                    {/* Factual Evidence List */}
                    {agent.evidence.length > 0 && (
                      <div className="p-3 rounded-xl bg-black/40 border border-white/5 space-y-1.5">
                        <span className="text-[10px] font-bold uppercase tracking-wider text-gray-500">
                          Empirical Evidence:
                        </span>
                        <ul className="space-y-1 text-[11px] text-gray-400">
                          {agent.evidence.slice(0, 3).map((ev, idx) => (
                            <li key={idx} className="truncate">
                              • {ev}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>

                  {/* Agent Limitations / Provenance */}
                  <div className="pt-2 border-t border-white/5 flex items-center justify-between text-[10px] text-gray-500 font-mono-numbers">
                    <span>{agent.limitations[0] || 'Standard boundaries'}</span>
                    <span>{agent.source_ids[0]?.split(':')[0] || 'Verified'}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Reasoning Trace Drawer */}
          <div className="glass-panel p-5 rounded-2xl border border-white/5 space-y-3">
            <button
              onClick={() => setShowReasoningTrace(!showReasoningTrace)}
              className="w-full flex items-center justify-between text-xs font-bold text-white hover:text-purple-300 transition-colors"
            >
              <div className="flex items-center gap-2">
                <Layers className="w-4 h-4 text-purple-400" />
                <span>Auditable Reasoning Trace</span>
                <span className="text-[10px] font-normal text-gray-400">
                  (Transparent non-hallucinatory evaluation trail)
                </span>
              </div>
              {showReasoningTrace ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>

            {showReasoningTrace && (
              <div className="pt-4 border-t border-white/5 space-y-4 text-xs">
                <div>
                  <span className="text-[11px] font-bold uppercase tracking-wider text-purple-400">
                    1. Data Considered:
                  </span>
                  <ul className="list-disc list-inside text-gray-300 space-y-1 mt-1">
                    {result.reasoning_trace.data_considered.map((d, i) => (
                      <li key={i}>{d}</li>
                    ))}
                  </ul>
                </div>

                <div>
                  <span className="text-[11px] font-bold uppercase tracking-wider text-purple-400">
                    2. Specialized Agents Consulted:
                  </span>
                  <div className="flex flex-wrap gap-2 mt-1.5">
                    {result.reasoning_trace.agents_consulted.map((a, i) => (
                      <span key={i} className="px-2.5 py-1 rounded-lg bg-white/5 text-purple-300 font-semibold font-mono-numbers">
                        ✓ {a}
                      </span>
                    ))}
                  </div>
                </div>

                <div>
                  <span className="text-[11px] font-bold uppercase tracking-wider text-purple-400">
                    3. Stated Methodological Limitations:
                  </span>
                  <ul className="list-disc list-inside text-gray-400 space-y-1 mt-1">
                    {result.reasoning_trace.limitations.map((lim, i) => (
                      <li key={i}>{lim}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>

          {/* Grounded Sources & Citations Drawer */}
          <div className="glass-panel p-5 rounded-2xl border border-white/5 space-y-3">
            <button
              onClick={() => setShowSources(!showSources)}
              className="w-full flex items-center justify-between text-xs font-bold text-white hover:text-purple-300 transition-colors"
            >
              <div className="flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-orange-400" />
                <span>Grounded Citations & External Sources ({result.sources.length})</span>
              </div>
              {showSources ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>

            {showSources && (
              <div className="pt-4 border-t border-white/5 space-y-2 text-xs">
                {result.sources.map((src, i) => (
                  <div
                    key={i}
                    className="p-3 rounded-xl bg-black/40 border border-white/5 flex items-center justify-between text-gray-300"
                  >
                    <span className="font-mono-numbers truncate max-w-md">{src}</span>
                    {src.startsWith('http') && (
                      <a
                        href={src}
                        target="_blank"
                        rel="noreferrer"
                        className="text-purple-400 hover:text-purple-300 flex items-center gap-1 shrink-0"
                      >
                        <span>Open Document</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Phase 6: Institutional Intelligence Report Export Modal */}
      <ExportReportModal
        isOpen={showExportModal}
        onClose={() => setShowExportModal(false)}
        analysis={result || null}
      />
    </div>
  );
};
