import React, { useState, useEffect } from 'react';
import {
  Layers,
  Scale,
  BookOpen,
  Filter,
  Clock,
  CheckCircle,
  AlertCircle,
  AlertTriangle,
  FileText,
  Activity,
  TrendingUp,
  RefreshCw,
  Plus,
} from 'lucide-react';
import { researchService } from '../services/researchService';
import {
  CompanyComparisonResponse,
  ThesisResponse,
  DecisionJournalItem,
  ScreenerResultItem,
  TimelineItem,
} from '../types';

export const ResearchPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'compare' | 'thesis' | 'journal' | 'screener' | 'timeline'>('compare');

  // --- 1. Comparison State ---
  const [compSymbolA, setCompSymbolA] = useState('NVDA');
  const [compSymbolB, setCompSymbolB] = useState('MSFT');
  const [comparisonData, setComparisonData] = useState<CompanyComparisonResponse | null>(null);
  const [isComparing, setIsComparing] = useState(false);

  // --- 2. Thesis State ---
  const [thesisSymbol, setThesisSymbol] = useState('NVDA');
  const [thesisData, setThesisData] = useState<ThesisResponse | null>(null);
  const [isBuildingThesis, setIsBuildingThesis] = useState(false);

  // --- 3. Decision Journal State ---
  const [journalEntries, setJournalEntries] = useState<DecisionJournalItem[]>([]);
  const [showJournalForm, setShowJournalForm] = useState(false);
  const [newSymbol, setNewSymbol] = useState('NVDA');
  const [newTitle, setNewTitle] = useState('');
  const [newReason, setNewReason] = useState('');
  const [newConfidence, setNewConfidence] = useState(0.85);
  const [newRisk, setNewRisk] = useState('');
  const [isReviewingId, setIsReviewingId] = useState<number | null>(null);

  // --- 4. Screener State ---
  const [screenerSector, setScreenerSector] = useState('');
  const [screenerMaxPe, setScreenerMaxPe] = useState('');
  const [screenerResults, setScreenerResults] = useState<ScreenerResultItem[]>([]);
  const [isScreening, setIsScreening] = useState(false);

  // --- 5. Timeline State ---
  const [timelineSymbol, setTimelineSymbol] = useState('NVDA');
  const [timelineItems, setTimelineItems] = useState<TimelineItem[]>([]);
  const [isTimelineLoading, setIsTimelineLoading] = useState(false);

  useEffect(() => {
    if (activeTab === 'compare' && !comparisonData) {
      handleRunComparison();
    } else if (activeTab === 'thesis' && !thesisData) {
      handleBuildThesis();
    } else if (activeTab === 'journal') {
      loadJournal();
    } else if (activeTab === 'screener' && screenerResults.length === 0) {
      handleRunScreen();
    } else if (activeTab === 'timeline' && timelineItems.length === 0) {
      handleLoadTimeline();
    }
  }, [activeTab]);

  // Actions
  const handleRunComparison = async () => {
    if (!compSymbolA || !compSymbolB) return;
    setIsComparing(true);
    try {
      const res = await researchService.compare(compSymbolA, compSymbolB);
      setComparisonData(res);
    } catch (err) {
      console.error('Failed to run comparison', err);
    } finally {
      setIsComparing(false);
    }
  };

  const handleBuildThesis = async () => {
    if (!thesisSymbol) return;
    setIsBuildingThesis(true);
    try {
      const res = await researchService.buildThesis(thesisSymbol, true);
      setThesisData(res);
    } catch (err) {
      console.error('Failed to build thesis', err);
    } finally {
      setIsBuildingThesis(false);
    }
  };

  const loadJournal = async () => {
    try {
      const entries = await researchService.listDecisionJournal();
      setJournalEntries(entries);
    } catch (err) {
      console.error('Failed to load journal', err);
    }
  };

  const handleCreateJournal = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newSymbol || !newTitle || !newReason) return;
    try {
      await researchService.createJournalEntry({
        symbol: newSymbol,
        thesis_title: newTitle,
        reason: newReason,
        risk_assessment: newRisk,
        confidence: newConfidence,
      });
      setShowJournalForm(false);
      setNewTitle('');
      setNewReason('');
      setNewRisk('');
      loadJournal();
    } catch (err) {
      console.error('Failed to create journal entry', err);
    }
  };

  const handleReviewJournal = async (id: number) => {
    setIsReviewingId(id);
    try {
      await researchService.reviewJournalEntry(id);
      loadJournal();
    } catch (err) {
      console.error('Failed to review journal entry', err);
    } finally {
      setIsReviewingId(null);
    }
  };

  const handleRunScreen = async () => {
    setIsScreening(true);
    try {
      const maxPeNum = screenerMaxPe ? parseFloat(screenerMaxPe) : undefined;
      const res = await researchService.screen({
        sector: screenerSector || undefined,
        max_pe: maxPeNum,
        limit: 10,
      });
      setScreenerResults(res);
    } catch (err) {
      console.error('Failed to screen securities', err);
    } finally {
      setIsScreening(false);
    }
  };

  const handleLoadTimeline = async () => {
    if (!timelineSymbol) return;
    setIsTimelineLoading(true);
    try {
      const res = await researchService.getTimeline(timelineSymbol);
      setTimelineItems(res);
    } catch (err) {
      console.error('Failed to load timeline', err);
    } finally {
      setIsTimelineLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-2">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/60 p-6 rounded-2xl border border-slate-800 backdrop-blur-sm">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Layers className="w-7 h-7 text-indigo-400" />
            Research Lab & Decision Support
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Comparative intelligence, evidence-weighted theses, Devil's Advocate stress-testing & decision journaling.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {[
            { id: 'compare', label: 'Company Comparison', icon: Scale },
            { id: 'thesis', label: 'Thesis Builder', icon: BookOpen },
            { id: 'journal', label: 'Decision Journal', icon: CheckCircle },
            { id: 'screener', label: 'Stock Screener', icon: Filter },
            { id: 'timeline', label: 'Research Timeline', icon: Clock },
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center space-x-2 px-3.5 py-2 rounded-xl text-xs font-semibold transition-all ${
                  activeTab === tab.id
                    ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30'
                    : 'bg-slate-800/60 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* --- TAB 1: COMPANY COMPARISON --- */}
      {activeTab === 'compare' && (
        <div className="space-y-6">
          {/* Compare Controls */}
          <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 flex flex-wrap items-center gap-4">
            <div className="flex items-center space-x-2">
              <span className="text-xs font-medium text-slate-400">Security A:</span>
              <input
                type="text"
                value={compSymbolA}
                onChange={(e) => setCompSymbolA(e.target.value.toUpperCase())}
                className="w-24 bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-100 text-center font-bold"
              />
            </div>
            <span className="text-xs text-slate-500 font-bold">VS</span>
            <div className="flex items-center space-x-2">
              <span className="text-xs font-medium text-slate-400">Security B:</span>
              <input
                type="text"
                value={compSymbolB}
                onChange={(e) => setCompSymbolB(e.target.value.toUpperCase())}
                className="w-24 bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-100 text-center font-bold"
              />
            </div>
            <button
              onClick={handleRunComparison}
              disabled={isComparing}
              className="px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center space-x-1.5 transition-colors"
            >
              {isComparing ? <Activity className="w-3.5 h-3.5 animate-spin" /> : <Scale className="w-3.5 h-3.5" />}
              <span>Compare Securities</span>
            </button>
          </div>

          {comparisonData && (
            <div className="space-y-6">
              {/* Relative Insights Banner */}
              <div className="bg-indigo-950/30 border border-indigo-800/40 p-4 rounded-xl space-y-2">
                <div className="text-xs font-semibold text-indigo-300 flex items-center space-x-1.5">
                  <TrendingUp className="w-4 h-4 text-indigo-400" />
                  <span>Relative Multi-Factor Synthesis</span>
                </div>
                <ul className="space-y-1 text-xs text-slate-300">
                  {comparisonData.relative_insights.map((ins, idx) => (
                    <li key={idx} className="flex items-start space-x-2">
                      <span className="text-indigo-400 font-bold">•</span>
                      <span>{ins}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Side-by-Side Comparison Table */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {[
                  { label: comparisonData.symbol_a, data: comparisonData.company_a },
                  { label: comparisonData.symbol_b, data: comparisonData.company_b },
                ].map((item, idx) => (
                  <div
                    key={idx}
                    className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-4 shadow-xl"
                  >
                    <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                      <div>
                        <h3 className="text-lg font-bold text-white">{item.label}</h3>
                        <p className="text-xs text-slate-400">{item.data.profile.name}</p>
                      </div>
                      <span className="px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 text-[11px] font-medium">
                        {item.data.profile.sector}
                      </span>
                    </div>

                    {/* Market & Valuation Metrics */}
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="bg-slate-950/60 p-2.5 rounded-lg">
                        <span className="text-slate-500 block text-[10px]">Price</span>
                        <span className="font-bold text-slate-200">
                          {typeof item.data.market.price === 'number'
                            ? `$${item.data.market.price.toFixed(2)}`
                            : item.data.market.price}
                        </span>
                      </div>
                      <div className="bg-slate-950/60 p-2.5 rounded-lg">
                        <span className="text-slate-500 block text-[10px]">Intraday Change</span>
                        <span
                          className={`font-bold ${
                            typeof item.data.market.change_percent === 'number' &&
                            item.data.market.change_percent >= 0
                              ? 'text-emerald-400'
                              : 'text-rose-400'
                          }`}
                        >
                          {typeof item.data.market.change_percent === 'number'
                            ? `${item.data.market.change_percent > 0 ? '+' : ''}${item.data.market.change_percent.toFixed(2)}%`
                            : item.data.market.change_percent}
                        </span>
                      </div>
                      <div className="bg-slate-950/60 p-2.5 rounded-lg">
                        <span className="text-slate-500 block text-[10px]">P/E Multiple</span>
                        <span className="font-bold text-slate-200">
                          {typeof item.data.fundamentals.pe_ratio === 'number'
                            ? `${item.data.fundamentals.pe_ratio.toFixed(1)}x`
                            : item.data.fundamentals.pe_ratio}
                        </span>
                      </div>
                      <div className="bg-slate-950/60 p-2.5 rounded-lg">
                        <span className="text-slate-500 block text-[10px]">Debt-to-Equity</span>
                        <span className="font-bold text-slate-200">
                          {typeof item.data.fundamentals.debt_to_equity === 'number'
                            ? item.data.fundamentals.debt_to_equity.toFixed(2)
                            : item.data.fundamentals.debt_to_equity}
                        </span>
                      </div>
                    </div>

                    {/* Agent Signals */}
                    <div className="space-y-2 pt-2 border-t border-slate-800/60 text-xs">
                      <div className="flex justify-between items-center">
                        <span className="text-slate-400">Technical Signal:</span>
                        <span className="font-semibold px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 text-[10px]">
                          {item.data.technical.signal}
                        </span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-slate-400">Sentiment Signal:</span>
                        <span className="font-semibold px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px]">
                          {item.data.sentiment.signal}
                        </span>
                      </div>
                    </div>

                    {/* Top SEC Citation */}
                    <div className="bg-slate-950/40 p-3 rounded-lg border border-slate-800/60 text-[11px] text-slate-400 space-y-1">
                      <span className="font-semibold text-slate-300 flex items-center gap-1">
                        <FileText className="w-3 h-3 text-indigo-400" />
                        SEC 10-K Evidence:
                      </span>
                      <p className="italic leading-relaxed">{item.data.top_citation}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* --- TAB 2: THESIS BUILDER --- */}
      {activeTab === 'thesis' && (
        <div className="space-y-6">
          <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 flex items-center gap-4">
            <span className="text-xs font-medium text-slate-400">Symbol:</span>
            <input
              type="text"
              value={thesisSymbol}
              onChange={(e) => setThesisSymbol(e.target.value.toUpperCase())}
              className="w-24 bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-100 text-center font-bold"
            />
            <button
              onClick={handleBuildThesis}
              disabled={isBuildingThesis}
              className="px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center space-x-1.5 transition-colors"
            >
              {isBuildingThesis ? <Activity className="w-3.5 h-3.5 animate-spin" /> : <BookOpen className="w-3.5 h-3.5" />}
              <span>Generate Multi-Perspective Thesis</span>
            </button>
          </div>

          {thesisData && (
            <div className="space-y-6">
              {/* Executive Thesis Header */}
              <div className="bg-slate-900/70 border border-slate-800 p-6 rounded-2xl space-y-3 shadow-xl">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-bold text-white">{thesisData.title}</h2>
                  <span className="text-xs text-slate-400">Saved to Research Memory</span>
                </div>
                <p className="text-sm text-slate-300 leading-relaxed">{thesisData.summary}</p>
              </div>

              {/* Bull vs Bear Case Columns */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Bull Case */}
                <div className="bg-emerald-950/20 border border-emerald-800/40 rounded-2xl p-5 space-y-3">
                  <div className="flex items-center space-x-2 text-emerald-400 font-bold text-sm">
                    <CheckCircle className="w-4 h-4" />
                    <span>Evidence-Backed Bull Case</span>
                  </div>
                  <ul className="space-y-2 text-xs text-emerald-200/90">
                    {thesisData.bull_case.map((b, idx) => (
                      <li key={idx} className="flex items-start space-x-2">
                        <span className="text-emerald-400 font-bold">•</span>
                        <span>{b}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Bear Case */}
                <div className="bg-rose-950/20 border border-rose-800/40 rounded-2xl p-5 space-y-3">
                  <div className="flex items-center space-x-2 text-rose-400 font-bold text-sm">
                    <AlertCircle className="w-4 h-4" />
                    <span>Adverse Factors & Valuation Bear Case</span>
                  </div>
                  <ul className="space-y-2 text-xs text-rose-200/90">
                    {thesisData.bear_case.map((b, idx) => (
                      <li key={idx} className="flex items-start space-x-2">
                        <span className="text-rose-400 font-bold">•</span>
                        <span>{b}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Devil's Advocate Counterarguments */}
              <div className="bg-amber-950/25 border border-amber-800/50 rounded-2xl p-5 space-y-3 shadow-xl">
                <div className="flex items-center space-x-2 text-amber-400 font-bold text-sm">
                  <AlertTriangle className="w-4 h-4" />
                  <span>Devil's Advocate Challenges (Combating Confirmation Bias)</span>
                </div>
                <p className="text-xs text-slate-400">
                  MATS actively challenges this thesis by isolating structural vulnerabilities, debt leverage, and multiple compression risks without fabricating negative data.
                </p>
                <ul className="space-y-2 text-xs text-amber-200/90">
                  {thesisData.counterarguments.map((c, idx) => (
                    <li key={idx} className="flex items-start space-x-2">
                      <span className="text-amber-400 font-bold">⚠️</span>
                      <span>{c}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Invalidation Conditions & What to Monitor */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    Thesis Invalidation Triggers
                  </h4>
                  <ul className="space-y-2 text-xs text-slate-300">
                    {thesisData.invalidation_conditions.map((cond, idx) => (
                      <li key={idx} className="flex items-start space-x-2">
                        <span className="text-rose-400 font-bold">✕</span>
                        <span>{cond}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-3">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    Surveillance Metrics to Monitor
                  </h4>
                  <ul className="space-y-2 text-xs text-slate-300">
                    {thesisData.what_to_monitor.map((mon, idx) => (
                      <li key={idx} className="flex items-start space-x-2">
                        <span className="text-indigo-400 font-bold">👁️</span>
                        <span>{mon}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Evidence Provenance Citations */}
              <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-5 space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
                  <FileText className="w-3.5 h-3.5 text-indigo-400" />
                  <span>Grounding Citations & Source Provenance</span>
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {thesisData.evidence_citations.map((cite, idx) => (
                    <div key={idx} className="bg-slate-950 p-3 rounded-xl border border-slate-800/60 text-xs space-y-1">
                      <div className="flex justify-between items-center text-slate-400">
                        <span className="font-semibold text-slate-200">{cite.document_title}</span>
                        <span className="text-[10px] text-indigo-400 font-mono">
                          Reliability: {(cite.reliability_weight * 100).toFixed(0)}%
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400 italic">"{cite.excerpt}"</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* --- TAB 3: DECISION JOURNAL --- */}
      {activeTab === 'journal' && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="text-lg font-bold text-white">Investment Decision Journal</h3>
              <p className="text-xs text-slate-400">Record investment theses and review them retrospectively against new evidence.</p>
            </div>
            <button
              onClick={() => setShowJournalForm(!showJournalForm)}
              className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center space-x-1.5 transition-colors"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Record Research Thesis</span>
            </button>
          </div>

          {/* Form Modal / Inline */}
          {showJournalForm && (
            <form
              onSubmit={handleCreateJournal}
              className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl space-y-4 shadow-xl"
            >
              <h4 className="text-sm font-bold text-indigo-300">New Investment Thesis Entry</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                <div>
                  <label className="block text-slate-400 mb-1">Symbol</label>
                  <input
                    type="text"
                    value={newSymbol}
                    onChange={(e) => setNewSymbol(e.target.value.toUpperCase())}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-white font-bold"
                    required
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-slate-400 mb-1">Thesis Title</label>
                  <input
                    type="text"
                    value={newTitle}
                    onChange={(e) => setNewTitle(e.target.value)}
                    placeholder="e.g. Data Center Capex Dominance"
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-white"
                    required
                  />
                </div>
              </div>
              <div className="text-xs">
                <label className="block text-slate-400 mb-1">Reason / Core Assumption</label>
                <textarea
                  value={newReason}
                  onChange={(e) => setNewReason(e.target.value)}
                  placeholder="Explain why you expect this company to execute..."
                  rows={3}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-white"
                  required
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
                <div>
                  <label className="block text-slate-400 mb-1">Risk Assessment</label>
                  <input
                    type="text"
                    value={newRisk}
                    onChange={(e) => setNewRisk(e.target.value)}
                    placeholder="e.g. Valuation compression if capex slows"
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-white"
                  />
                </div>
                <div>
                  <label className="block text-slate-400 mb-1">Confidence: {(newConfidence * 100).toFixed(0)}%</label>
                  <input
                    type="range"
                    min="0.1"
                    max="1.0"
                    step="0.05"
                    value={newConfidence}
                    onChange={(e) => setNewConfidence(parseFloat(e.target.value))}
                    className="w-full mt-2 accent-indigo-500"
                  />
                </div>
              </div>
              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowJournalForm(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300 text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
                >
                  Save Entry
                </button>
              </div>
            </form>
          )}

          {/* Journal Entries List */}
          <div className="space-y-4">
            {journalEntries.length === 0 ? (
              <div className="text-center py-12 text-slate-500 text-xs bg-slate-900/30 rounded-2xl border border-slate-800">
                No recorded investment hypotheses yet. Click 'Record Research Thesis' to create one.
              </div>
            ) : (
              journalEntries.map((entry) => (
                <div
                  key={entry.id}
                  className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-3 shadow-lg"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800 pb-3">
                    <div className="flex items-center space-x-3">
                      <span className="px-2.5 py-1 rounded-lg bg-indigo-950 text-indigo-300 font-bold text-xs">
                        {entry.symbol}
                      </span>
                      <h4 className="text-sm font-bold text-white">{entry.thesis_title}</h4>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span
                        className={`px-2.5 py-1 rounded-full text-[11px] font-bold ${
                          entry.status === 'SUPPORTED'
                            ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                            : entry.status === 'CONTRADICTED'
                            ? 'bg-rose-950 text-rose-300 border border-rose-800'
                            : 'bg-indigo-950 text-indigo-300 border border-indigo-800'
                        }`}
                      >
                        {entry.status}
                      </span>
                      <button
                        onClick={() => handleReviewJournal(entry.id)}
                        disabled={isReviewingId === entry.id}
                        className="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium flex items-center space-x-1"
                      >
                        <RefreshCw className={`w-3 h-3 ${isReviewingId === entry.id ? 'animate-spin' : ''}`} />
                        <span>Review Thesis</span>
                      </button>
                    </div>
                  </div>

                  <p className="text-xs text-slate-300 leading-relaxed">{entry.reason}</p>

                  {entry.review_notes && (
                    <div className="bg-slate-950/70 p-3 rounded-xl border border-slate-800/80 text-xs text-slate-300 space-y-1">
                      <span className="font-semibold text-indigo-300 block text-[11px]">
                        Retrospective Review Notes:
                      </span>
                      <p>{entry.review_notes}</p>
                    </div>
                  )}

                  <div className="flex justify-between items-center text-[10px] text-slate-500 pt-1">
                    <span>Logged on: {new Date(entry.date).toLocaleDateString()}</span>
                    <span>Confidence: {(entry.confidence * 100).toFixed(0)}%</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* --- TAB 4: STOCK SCREENER --- */}
      {activeTab === 'screener' && (
        <div className="space-y-6">
          <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 flex flex-wrap items-center gap-4">
            <div className="flex items-center space-x-2">
              <span className="text-xs text-slate-400">Sector:</span>
              <input
                type="text"
                placeholder="e.g. Technology"
                value={screenerSector}
                onChange={(e) => setScreenerSector(e.target.value)}
                className="bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-white"
              />
            </div>
            <div className="flex items-center space-x-2">
              <span className="text-xs text-slate-400">Max P/E:</span>
              <input
                type="number"
                placeholder="e.g. 45"
                value={screenerMaxPe}
                onChange={(e) => setScreenerMaxPe(e.target.value)}
                className="w-20 bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-white"
              />
            </div>
            <button
              onClick={handleRunScreen}
              disabled={isScreening}
              className="px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center space-x-1.5 transition-colors"
            >
              {isScreening ? <Activity className="w-3.5 h-3.5 animate-spin" /> : <Filter className="w-3.5 h-3.5" />}
              <span>Filter Candidates</span>
            </button>
          </div>

          <div className="overflow-x-auto rounded-2xl border border-slate-800 shadow-xl bg-slate-900/60">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950 text-slate-400 font-semibold border-b border-slate-800">
                <tr>
                  <th className="p-3.5">Security</th>
                  <th className="p-3.5">Sector</th>
                  <th className="p-3.5">Price</th>
                  <th className="p-3.5">P/E</th>
                  <th className="p-3.5">Debt/Equity</th>
                  <th className="p-3.5">Why Included? (Explainability)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {screenerResults.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="p-6 text-center text-slate-500">
                      No securities match the active screening criteria.
                    </td>
                  </tr>
                ) : (
                  screenerResults.map((r, idx) => (
                    <tr key={idx} className="hover:bg-slate-850 transition-colors">
                      <td className="p-3.5 font-bold text-white">
                        {r.symbol} <span className="font-normal text-slate-400 text-[11px] block">{r.name}</span>
                      </td>
                      <td className="p-3.5 text-slate-300">{r.sector}</td>
                      <td className="p-3.5 font-mono">
                        {typeof r.price === 'number' ? `$${r.price.toFixed(2)}` : r.price}
                      </td>
                      <td className="p-3.5 font-mono">
                        {typeof r.pe_ratio === 'number' ? `${r.pe_ratio.toFixed(1)}x` : r.pe_ratio}
                      </td>
                      <td className="p-3.5 font-mono">
                        {typeof r.debt_to_equity === 'number' ? r.debt_to_equity.toFixed(2) : r.debt_to_equity}
                      </td>
                      <td className="p-3.5 text-indigo-300 font-medium">{r.why_included}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* --- TAB 5: RESEARCH TIMELINE --- */}
      {activeTab === 'timeline' && (
        <div className="space-y-6">
          <div className="bg-slate-900/50 p-4 rounded-xl border border-slate-800 flex items-center gap-4">
            <span className="text-xs font-medium text-slate-400">Security Timeline:</span>
            <input
              type="text"
              value={timelineSymbol}
              onChange={(e) => setTimelineSymbol(e.target.value.toUpperCase())}
              className="w-24 bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white text-center font-bold"
            />
            <button
              onClick={handleLoadTimeline}
              disabled={isTimelineLoading}
              className="px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center space-x-1.5 transition-colors"
            >
              {isTimelineLoading ? <Activity className="w-3.5 h-3.5 animate-spin" /> : <Clock className="w-3.5 h-3.5" />}
              <span>Load Timeline</span>
            </button>
          </div>

          <div className="relative border-l border-slate-800 ml-4 space-y-6">
            {timelineItems.length === 0 ? (
              <div className="pl-6 py-6 text-slate-500 text-xs">
                No historical research milestones on record for {timelineSymbol}.
              </div>
            ) : (
              timelineItems.map((item, idx) => (
                <div key={idx} className="relative pl-6">
                  <div
                    className={`absolute -left-2 top-1.5 w-4 h-4 rounded-full border-2 border-slate-950 ${
                      item.type === 'ANALYSIS'
                        ? 'bg-indigo-500'
                        : item.type === 'DOCUMENT'
                        ? 'bg-emerald-500'
                        : item.type === 'MARKET_EVENT'
                        ? 'bg-amber-500'
                        : 'bg-rose-500'
                    }`}
                  />
                  <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4 space-y-1 shadow-md">
                    <div className="flex justify-between items-center text-xs">
                      <span className="font-bold text-white">{item.title}</span>
                      <span className="text-[10px] text-slate-500">
                        {item.timestamp ? new Date(item.timestamp).toLocaleString() : 'N/A'}
                      </span>
                    </div>
                    <p className="text-xs text-slate-400">{item.summary}</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};
export default ResearchPage;
