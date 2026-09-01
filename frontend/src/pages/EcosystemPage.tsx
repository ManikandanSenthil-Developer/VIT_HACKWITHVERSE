import React, { useState, useEffect } from 'react';
import {
  Globe,
  Sliders,
  Download,
  Upload,
  Volume2,
  VolumeX,
  ShieldCheck,
  Building,
  GraduationCap,
  Activity,
  AlertTriangle,
  FileSpreadsheet,
  Database,
  RefreshCw,
  Eye,
} from 'lucide-react';
import { useAccessibility } from '../context/AccessibilityContext';
import { ecosystemService } from '../services/ecosystemService';
import { voiceService } from '../services/voiceService';
import {
  ImpactMetrics,
  ProviderHealthItem,
  EducationConcept,
  SourceConflictReport,
  CsvImportResult,
} from '../types';

export const EcosystemPage: React.FC = () => {
  const {
    preferences,
    setLanguage,
    setTextSize,
    setReducedMotion,
    setHighContrast,
    setVoiceEnabled,
  } = useAccessibility();

  const [activeTab, setActiveTab] = useState<'accessibility' | 'portability' | 'provenance' | 'broker' | 'impact'>('accessibility');

  // --- Accessibility Audio Test ---
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);

  // --- CSV Import State ---
  const [csvText, setCsvText] = useState(
    'symbol,quantity,average_price\nNVDA,15,122.50\nMSFT,10,412.00\nAAPL,20,195.00\nINVALID_TICKER,-5,0'
  );
  const [importResult, setImportResult] = useState<CsvImportResult | null>(null);
  const [isImporting, setIsImporting] = useState(false);

  // --- Source Conflict Simulator State ---
  const [conflictReport, setConflictReport] = useState<SourceConflictReport | null>(null);
  const [sourceAValue, setSourceAValue] = useState(128.5);
  const [sourceBValue, setSourceBValue] = useState(132.5);
  const [isCheckingConflict, setIsCheckingConflict] = useState(false);

  // --- Mock Broker State ---
  const [brokerSyncResult, setBrokerSyncResult] = useState<any>(null);
  const [isSyncingBroker, setIsSyncingBroker] = useState(false);

  // --- Education & Impact State ---
  const [selectedConcept, setSelectedConcept] = useState('pe_ratio');
  const [conceptData, setConceptData] = useState<EducationConcept | null>(null);
  const [impactData, setImpactData] = useState<ImpactMetrics | null>(null);
  const [providerStatuses, setProviderStatuses] = useState<ProviderHealthItem[]>([]);

  useEffect(() => {
    loadConcept(selectedConcept);
    loadImpactMetrics();
  }, [selectedConcept, preferences.language]);

  const handleTestVoice = () => {
    if (isPlayingAudio) {
      voiceService.stopSpeaking();
      setIsPlayingAudio(false);
      return;
    }
    setIsPlayingAudio(true);
    const testPhrase =
      preferences.language === 'ta'
        ? 'மேட்ஸ் அணுகல்தன்மை மற்றும் குரல் சேவை வெற்றிகரமாக இயக்கப்பட்டது.'
        : preferences.language === 'hi'
        ? 'मैट्स अभिगम्यता और वॉयस सेवाएं सफलतापूर्वक सक्रिय हैं।'
        : 'MATS accessibility and voice services are online and operational.';

    voiceService.speak(testPhrase, preferences.language, () => {
      setIsPlayingAudio(false);
    });
  };

  const handleImportCsv = async () => {
    if (!csvText.trim()) return;
    setIsImporting(true);
    try {
      // Default to portfolio ID 1
      const res = await ecosystemService.importPortfolioCsv(1, csvText);
      setImportResult(res);
    } catch (err: any) {
      console.error('Import failed', err);
      alert(`Import error: ${err?.response?.data?.detail || err.message}`);
    } finally {
      setIsImporting(false);
    }
  };

  const handleCheckConflict = async () => {
    setIsCheckingConflict(true);
    try {
      const res = await ecosystemService.checkSourceConflict({
        symbol: 'NVDA',
        metric: 'Price',
        source_a_name: 'Primary Live Feed',
        source_a_value: sourceAValue,
        source_a_hierarchy: 'PRIMARY',
        source_b_name: 'Secondary Aggregator',
        source_b_value: sourceBValue,
        source_b_hierarchy: 'SECONDARY',
      });
      setConflictReport(res);
    } catch (err) {
      console.error('Conflict check failed', err);
    } finally {
      setIsCheckingConflict(false);
    }
  };

  const handleSyncBroker = async () => {
    setIsSyncingBroker(true);
    try {
      const res = await ecosystemService.syncMockBroker();
      setBrokerSyncResult(res);
    } catch (err) {
      console.error('Broker sync failed', err);
    } finally {
      setIsSyncingBroker(false);
    }
  };

  const loadConcept = async (concept: string) => {
    try {
      const res = await ecosystemService.getEducationConcept(concept, preferences.language);
      setConceptData(res);
    } catch (err) {
      console.error('Failed to load concept', err);
    }
  };

  const loadImpactMetrics = async () => {
    try {
      const [impact, providers] = await Promise.all([
        ecosystemService.getImpactMetrics(),
        ecosystemService.getProvidersHealth(),
      ]);
      setImpactData(impact);
      setProviderStatuses(providers);
    } catch (err) {
      console.error('Failed to load telemetry', err);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-2">
      {/* Top Banner */}
      <div className="bg-slate-900/60 p-6 rounded-2xl border border-slate-800 backdrop-blur-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
            <Globe className="w-7 h-7 text-indigo-400" />
            Ecosystem, Accessibility & Data Provenance
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Multilingual intelligence (English, தமிழ், हिन्दी), Senior accessibility, data lineage & non-custodial ecosystem integrations.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {[
            { id: 'accessibility', label: 'Accessibility & Voice', icon: Sliders },
            { id: 'portability', label: 'Import / Export Data', icon: Download },
            { id: 'provenance', label: 'Data Provenance & Lineage', icon: ShieldCheck },
            { id: 'broker', label: 'Mock Brokerage (Read-Only)', icon: Building },
            { id: 'impact', label: 'Education & Impact', icon: GraduationCap },
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

      {/* --- TAB 1: ACCESSIBILITY & VOICE SETTINGS --- */}
      {activeTab === 'accessibility' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Language Selection */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-xl">
            <h3 className="text-sm font-bold text-white flex items-center space-x-2">
              <Globe className="w-4 h-4 text-indigo-400" />
              <span>Multilingual Interaction Language</span>
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Select your preferred language. Financial terminology is paired bilingually with English terms to avoid translation ambiguity.
            </p>
            <div className="grid grid-cols-3 gap-3 pt-2">
              {[
                { code: 'en', label: 'English', sub: 'Default' },
                { code: 'ta', label: 'தமிழ்', sub: 'Tamil' },
                { code: 'hi', label: 'हिन्दी', sub: 'Hindi' },
              ].map((l) => (
                <button
                  key={l.code}
                  onClick={() => setLanguage(l.code as any)}
                  className={`p-3.5 rounded-xl border text-center transition-all ${
                    preferences.language === l.code
                      ? 'bg-indigo-950/80 border-indigo-500 text-white font-bold shadow-lg shadow-indigo-500/20'
                      : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  <span className="block text-sm font-bold">{l.label}</span>
                  <span className="block text-[10px] text-slate-500 mt-0.5">{l.sub}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Senior-Friendly Text Size */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-xl">
            <h3 className="text-sm font-bold text-white flex items-center space-x-2">
              <Eye className="w-4 h-4 text-indigo-400" />
              <span>Senior-Friendly Text Sizing</span>
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Dynamically scales typography across the entire platform without breaking responsive layouts.
            </p>
            <div className="grid grid-cols-3 gap-3 pt-2">
              {[
                { size: 'normal', label: 'Normal', preview: '14px Base' },
                { size: 'large', label: 'Large', preview: '+2px Enlarge' },
                { size: 'extra_large', label: 'Extra Large', preview: '+4px Senior' },
              ].map((s) => (
                <button
                  key={s.size}
                  onClick={() => setTextSize(s.size as any)}
                  className={`p-3.5 rounded-xl border text-center transition-all ${
                    preferences.text_size === s.size
                      ? 'bg-indigo-950/80 border-indigo-500 text-white font-bold shadow-lg shadow-indigo-500/20'
                      : 'bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  <span className="block text-sm font-bold">{s.label}</span>
                  <span className="block text-[10px] text-slate-500 mt-0.5">{s.preview}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Visual Comfort & Reduced Motion */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-xl">
            <h3 className="text-sm font-bold text-white flex items-center space-x-2">
              <Sliders className="w-4 h-4 text-indigo-400" />
              <span>Contrast & Motion Controls</span>
            </h3>
            <div className="space-y-3 pt-2">
              <label className="flex items-center justify-between p-3 rounded-xl bg-slate-950/60 border border-slate-800 cursor-pointer">
                <div>
                  <span className="text-xs font-semibold text-slate-200 block">High Contrast Mode</span>
                  <span className="text-[11px] text-slate-500">WCAG AAA compliant border and text contrast</span>
                </div>
                <input
                  type="checkbox"
                  checked={preferences.high_contrast}
                  onChange={(e) => setHighContrast(e.target.checked)}
                  className="w-4 h-4 accent-indigo-600 rounded"
                />
              </label>

              <label className="flex items-center justify-between p-3 rounded-xl bg-slate-950/60 border border-slate-800 cursor-pointer">
                <div>
                  <span className="text-xs font-semibold text-slate-200 block">Reduced Motion Mode</span>
                  <span className="text-[11px] text-slate-500">Disables 3D canvas transitions and micro-animations</span>
                </div>
                <input
                  type="checkbox"
                  checked={preferences.reduced_motion}
                  onChange={(e) => setReducedMotion(e.target.checked)}
                  className="w-4 h-4 accent-indigo-600 rounded"
                />
              </label>
            </div>
          </div>

          {/* Voice-First Interface */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-xl">
            <h3 className="text-sm font-bold text-white flex items-center space-x-2">
              <Volume2 className="w-4 h-4 text-indigo-400" />
              <span>Voice-First Audio Integration</span>
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Enable spoken question input and spoken intelligence summaries using browser Web Speech APIs.
            </p>
            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-950/60 border border-slate-800">
              <span className="text-xs font-semibold text-slate-200">Voice Audio Output Enabled</span>
              <input
                type="checkbox"
                checked={preferences.voice_enabled}
                onChange={(e) => setVoiceEnabled(e.target.checked)}
                className="w-4 h-4 accent-indigo-600 rounded"
              />
            </div>
            <button
              onClick={handleTestVoice}
              className="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center justify-center space-x-2 transition-colors"
            >
              {isPlayingAudio ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
              <span>{isPlayingAudio ? 'Stop Audio Sample' : 'Play Test Voice Sample'}</span>
            </button>
          </div>
        </div>
      )}

      {/* --- TAB 2: IMPORT / EXPORT DATA PORTABILITY --- */}
      {activeTab === 'portability' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* CSV Portfolio Importer */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-xl">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                <FileSpreadsheet className="w-4 h-4 text-indigo-400" />
                <span>Import Portfolio CSV</span>
              </h3>
              <span className="text-[11px] text-slate-400">Strict Row Validation</span>
            </div>
            <p className="text-xs text-slate-400">
              Paste CSV contents below. Headers required: <code className="text-indigo-300">symbol,quantity,average_price</code>.
            </p>
            <textarea
              rows={5}
              value={csvText}
              onChange={(e) => setCsvText(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-xl p-3 font-mono text-xs text-slate-200"
            />
            <button
              onClick={handleImportCsv}
              disabled={isImporting}
              className="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center justify-center space-x-2 transition-colors"
            >
              {isImporting ? <Activity className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
              <span>Validate & Import Holdings</span>
            </button>

            {importResult && (
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2 text-xs">
                <div className="flex justify-between font-semibold">
                  <span className="text-emerald-400">✓ {importResult.valid_count} Valid Holdings Imported</span>
                  <span className="text-rose-400">✕ {importResult.rejected_count} Rows Rejected</span>
                </div>
                {importResult.rejected_rows.length > 0 && (
                  <div className="text-[11px] text-rose-300/90 space-y-1 pt-1 border-t border-slate-800">
                    <span className="font-bold">Rejection Details:</span>
                    {importResult.rejected_rows.map((rej, idx) => (
                      <div key={idx}>• Line {rej.line || idx + 2}: {rej.reason}</div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* User Data Export (GDPR Portability) */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-xl">
            <h3 className="text-sm font-bold text-white flex items-center space-x-2">
              <Download className="w-4 h-4 text-indigo-400" />
              <span>Export My Data (GDPR Portability)</span>
            </h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Export your full user data archive: active portfolios, watchlists, multi-agent analysis records, decision journal entries, and audit logs.
            </p>
            <div className="grid grid-cols-2 gap-3 pt-2">
              <button
                onClick={async () => {
                  const data = await ecosystemService.exportUserDataJson();
                  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `mats_user_export_${Date.now()}.json`;
                  a.click();
                }}
                className="p-4 rounded-xl bg-slate-950 border border-slate-800 hover:border-indigo-500/40 text-center transition-all text-xs text-slate-200"
              >
                <Database className="w-5 h-5 text-indigo-400 mx-auto mb-1.5" />
                <span className="font-bold block">Download JSON</span>
                <span className="text-[10px] text-slate-500">Structured raw data</span>
              </button>

              <button
                onClick={() => ecosystemService.downloadUserDataCsv()}
                className="p-4 rounded-xl bg-slate-950 border border-slate-800 hover:border-indigo-500/40 text-center transition-all text-xs text-slate-200"
              >
                <FileSpreadsheet className="w-5 h-5 text-emerald-400 mx-auto mb-1.5" />
                <span className="font-bold block">Download CSV</span>
                <span className="text-[10px] text-slate-500">Spreadsheet table view</span>
              </button>
            </div>

            <div className="p-3 bg-amber-950/20 border border-amber-800/40 rounded-xl text-[11px] text-amber-300">
              User data exports are strictly isolated to your authenticated account ID. Cross-tenant inspection is prevented.
            </div>
          </div>
        </div>
      )}

      {/* --- TAB 3: DATA PROVENANCE & SOURCE CONFLICTS --- */}
      {activeTab === 'provenance' && (
        <div className="space-y-6">
          {/* Source Hierarchy Explainer */}
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs">
            <div className="bg-purple-950/30 border border-purple-800/50 p-4 rounded-xl">
              <span className="text-[10px] uppercase font-bold text-purple-400">Tier 1: OFFICIAL</span>
              <h4 className="font-bold text-white mt-1">SEC Form 10-K</h4>
              <p className="text-slate-400 text-[11px] mt-1">Audited annual financial reports & statutory Item 1A risks.</p>
            </div>
            <div className="bg-emerald-950/30 border border-emerald-800/50 p-4 rounded-xl">
              <span className="text-[10px] uppercase font-bold text-emerald-400">Tier 2: PRIMARY</span>
              <h4 className="font-bold text-white mt-1">Direct Exchange Feeds</h4>
              <p className="text-slate-400 text-[11px] mt-1">Real-time normalized market quotes and continuous OHLCV.</p>
            </div>
            <div className="bg-amber-950/30 border border-amber-800/50 p-4 rounded-xl">
              <span className="text-[10px] uppercase font-bold text-amber-400">Tier 3: REGULATORY</span>
              <h4 className="font-bold text-white mt-1">Compliance Alerts</h4>
              <p className="text-slate-400 text-[11px] mt-1">Enforcement actions and statutory disclosures.</p>
            </div>
            <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl">
              <span className="text-[10px] uppercase font-bold text-slate-400">Tier 4: SECONDARY</span>
              <h4 className="font-bold text-white mt-1">Aggregated Metrics</h4>
              <p className="text-slate-400 text-[11px] mt-1">Third-party ratio providers and historical consensus.</p>
            </div>
          </div>

          {/* Source Conflict Detector Simulator */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-xl">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                <span>Live Source Conflict Detector</span>
              </h3>
              <span className="text-[11px] text-slate-400">Zero Silent Approximations</span>
            </div>
            <p className="text-xs text-slate-400">
              When two providers report divergent prices or valuation multiples (&gt;2%), MATS exposes the conflict rather than picking one arbitrarily.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
              <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
                <label className="block text-slate-400 mb-1">Source A (Primary Feed Price):</label>
                <input
                  type="number"
                  step="0.1"
                  value={sourceAValue}
                  onChange={(e) => setSourceAValue(parseFloat(e.target.value))}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white font-mono"
                />
              </div>
              <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
                <label className="block text-slate-400 mb-1">Source B (Secondary Aggregator Price):</label>
                <input
                  type="number"
                  step="0.1"
                  value={sourceBValue}
                  onChange={(e) => setSourceBValue(parseFloat(e.target.value))}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-white font-mono"
                />
              </div>
            </div>
            <button
              onClick={handleCheckConflict}
              disabled={isCheckingConflict}
              className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center space-x-1.5 transition-colors"
            >
              {isCheckingConflict ? <Activity className="w-3.5 h-3.5 animate-spin" /> : <ShieldCheck className="w-3.5 h-3.5" />}
              <span>Evaluate Source Integrity</span>
            </button>

            {conflictReport && (
              <div
                className={`p-4 rounded-xl border text-xs space-y-2 ${
                  conflictReport.has_conflict
                    ? 'bg-amber-950/20 border-amber-800/60 text-amber-200'
                    : 'bg-emerald-950/20 border-emerald-800/60 text-emerald-200'
                }`}
              >
                <div className="flex justify-between items-center font-bold">
                  <span>Status: {conflictReport.status}</span>
                  <span className="font-mono">Confidence: {(conflictReport.confidence * 100).toFixed(0)}%</span>
                </div>
                <p>{conflictReport.interpretation}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* --- TAB 4: MOCK BROKERAGE (READ-ONLY) --- */}
      {activeTab === 'broker' && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-xl">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center space-x-2">
              <Building className="w-4 h-4 text-indigo-400" />
              <span>External Broker Integration (Read-Only Paper Sandbox)</span>
            </h3>
            <span className="px-2.5 py-1 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 text-[11px] font-bold">
              DEMO BROKER (Mock Data)
            </span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Connects to a simulated external brokerage sandbox (e.g. Zerodha Kite Mock / Interactive Brokers Paper Trading).
            In accordance with MATS Governance, this adapter is strictly <strong>READ-ONLY</strong>. Direct trade execution, order transmission, or capital transfers are completely prohibited.
          </p>

          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-3">
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-400">Sandbox Account:</span>
              <span className="font-mono font-bold text-white">ACC-DEMO-9942 (Paper Trading)</span>
            </div>
            <div className="flex justify-between items-center text-xs">
              <span className="text-slate-400">Permission Scope:</span>
              <span className="font-bold text-emerald-400">READ_PORTFOLIO_ONLY</span>
            </div>
            <button
              onClick={handleSyncBroker}
              disabled={isSyncingBroker}
              className="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center justify-center space-x-2 transition-colors"
            >
              {isSyncingBroker ? <Activity className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
              <span>Sync Simulated Broker Holdings</span>
            </button>
          </div>

          {brokerSyncResult && (
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-2 text-xs">
              <div className="flex justify-between items-center font-bold text-emerald-400">
                <span>✓ Synchronized {brokerSyncResult.synced_holdings_count} Mock Positions</span>
                <span>{new Date(brokerSyncResult.last_synced_at).toLocaleTimeString()}</span>
              </div>
              <p className="text-slate-400 text-[11px] italic">{brokerSyncResult.disclaimer}</p>
            </div>
          )}
        </div>
      )}

      {/* --- TAB 5: FINANCIAL EDUCATION & IMPACT METRICS --- */}
      {activeTab === 'impact' && (
        <div className="space-y-6">
          {/* Social Impact Metric Cards */}
          {impactData && (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl">
                <span className="text-[10px] uppercase font-bold text-slate-500">Retail Users</span>
                <span className="block text-xl font-bold text-white mt-1 font-mono">{impactData.users_onboarded}</span>
              </div>
              <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl">
                <span className="text-[10px] uppercase font-bold text-slate-500">Analyses Run</span>
                <span className="block text-xl font-bold text-indigo-400 mt-1 font-mono">{impactData.analyses_completed}</span>
              </div>
              <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl">
                <span className="text-[10px] uppercase font-bold text-slate-500">Surveillance Alerts</span>
                <span className="block text-xl font-bold text-amber-400 mt-1 font-mono">{impactData.alerts_generated}</span>
              </div>
              <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl">
                <span className="text-[10px] uppercase font-bold text-slate-500">Research Time Saved</span>
                <span className="block text-xl font-bold text-emerald-400 mt-1 font-mono">
                  {impactData.estimated_research_time_saved_hours}h <span className="text-[10px] text-slate-500 font-sans">(ESTIMATE)</span>
                </span>
              </div>
            </div>
          )}

          {/* Contextual Financial Concept Cards */}
          <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-xl">
            <h3 className="text-sm font-bold text-white flex items-center space-x-2">
              <GraduationCap className="w-4 h-4 text-indigo-400" />
              <span>Contextual Financial Education Mode ("Explain This to Me")</span>
            </h3>
            <div className="flex flex-wrap gap-2">
              {[
                { id: 'pe_ratio', label: 'P/E Ratio' },
                { id: 'volatility', label: 'Volatility' },
                { id: 'drawdown', label: 'Maximum Drawdown' },
                { id: 'diversification', label: 'Diversification' },
                { id: 'concentration', label: 'Concentration Risk' },
              ].map((c) => (
                <button
                  key={c.id}
                  onClick={() => setSelectedConcept(c.id)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
                    selectedConcept === c.id
                      ? 'bg-indigo-600 text-white'
                      : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                  }`}
                >
                  {c.label}
                </button>
              ))}
            </div>

            {conceptData && (
              <div className="bg-slate-950 p-5 rounded-xl border border-slate-800 space-y-3 text-xs">
                <h4 className="text-base font-bold text-white">{conceptData.title}</h4>
                <div className="space-y-1.5 text-slate-300">
                  <p><strong className="text-indigo-400">Simple Definition:</strong> {conceptData.simple_definition}</p>
                  <p><strong className="text-indigo-400">Concrete Example:</strong> {conceptData.example}</p>
                  <p><strong className="text-indigo-400">Why it Matters:</strong> {conceptData.why_it_matters}</p>
                  <p><strong className="text-indigo-400">Limitations:</strong> {conceptData.limitations}</p>
                </div>
                <div className="text-[10px] text-slate-500 pt-2 border-t border-slate-800">
                  {conceptData.disclaimer}
                </div>
              </div>
            )}
          </div>

          {/* Provider Health Telemetry */}
          {providerStatuses.length > 0 && (
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-xl">
              <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                <Activity className="w-4 h-4 text-emerald-400" />
                <span>External & Internal Data Provider Telemetry</span>
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {providerStatuses.map((p, idx) => (
                  <div key={idx} className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 flex justify-between items-center text-xs">
                    <div>
                      <span className="font-bold text-slate-200 block">{p.name}</span>
                      <span className="text-[10px] text-slate-500">{p.provider_type} • Latency: {p.latency_ms}ms</span>
                    </div>
                    <span className="px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800/40 font-bold text-[10px]">
                      {p.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
export default EcosystemPage;
