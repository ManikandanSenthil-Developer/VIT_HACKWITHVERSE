import React from 'react';
import { X, ShieldCheck, Clock, Layers, FileText } from 'lucide-react';

interface DataProvenanceModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  sourceTitle?: string;
  provider?: string;
  hierarchy?: 'PRIMARY' | 'OFFICIAL' | 'REGULATORY' | 'SECONDARY' | 'TERTIARY';
  retrievedAt?: string;
  publishedAt?: string;
  freshness?: 'RECENT' | 'CACHED' | 'STALE';
  confidence?: number;
  lineageNodes?: Array<{
    level: string;
    title: string;
    description: string;
    confidence: number;
  }>;
}

export const DataProvenanceModal: React.FC<DataProvenanceModalProps> = ({
  isOpen,
  onClose,
  title = 'Data Provenance & Source Lineage Inspector',
  sourceTitle = 'Official SEC EDGAR Form 10-K & Live Exchange Telemetry',
  provider = 'SEC EDGAR & Market Normalization Service',
  hierarchy = 'OFFICIAL',
  retrievedAt = new Date().toISOString(),
  publishedAt = '2024-03-15T00:00:00Z',
  freshness = 'RECENT',
  confidence = 0.96,
  lineageNodes,
}) => {
  if (!isOpen) return null;

  const defaultLineage = lineageNodes || [
    {
      level: 'CONCLUSION',
      title: 'Synthesized Consensus Assessment',
      description: 'Multi-agent consensus combining technical breakout and balance sheet quality.',
      confidence: 0.90,
    },
    {
      level: 'AGENT_FINDING',
      title: 'Technical & Fundamental Agent Findings',
      description: 'RSI = 62.4, SMA-20 > SMA-50 crossover confirmed, operating margin = 34.2%.',
      confidence: 0.92,
    },
    {
      level: 'METRIC',
      title: 'Normalized Historical Market Bars & Ratios',
      description: '30-day continuous OHLCV price series & reported FY2024 audited balance sheet.',
      confidence: 0.98,
    },
    {
      level: 'SOURCE',
      title: 'Audited Regulatory Source (SEC EDGAR & Primary Feed)',
      description: 'Direct SEC Form 10-K annual report filing with 384-dim semantic vector embeddings.',
      confidence: 1.0,
    },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
      <div
        className="w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6 shadow-2xl overflow-y-auto max-h-[90vh]"
        role="dialog"
        aria-modal="true"
        aria-labelledby="provenance-title"
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center">
              <ShieldCheck className="w-4 h-4 text-indigo-400" />
            </div>
            <div>
              <h3 id="provenance-title" className="text-sm font-bold text-white">
                {title}
              </h3>
              <p className="text-[11px] text-slate-400">Auditable chain of custody and data provenance</p>
            </div>
          </div>
          <button
            onClick={onClose}
            aria-label="Close modal"
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Provenance Metadata Badges */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 text-xs">
          <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
            <span className="text-[10px] text-slate-500 block uppercase tracking-wider font-semibold">Hierarchy</span>
            <span
              className={`inline-block mt-1 px-2 py-0.5 rounded text-[11px] font-bold ${
                hierarchy === 'OFFICIAL'
                  ? 'bg-purple-950/80 text-purple-300 border border-purple-800/60'
                  : hierarchy === 'PRIMARY'
                  ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-800/60'
                  : 'bg-slate-800 text-slate-300'
              }`}
            >
              {hierarchy} SOURCE
            </span>
          </div>

          <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
            <span className="text-[10px] text-slate-500 block uppercase tracking-wider font-semibold">Freshness</span>
            <span className="inline-flex items-center mt-1 px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800/40 text-[11px] font-medium">
              <Clock className="w-3 h-3 mr-1" />
              {freshness}
            </span>
          </div>

          <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
            <span className="text-[10px] text-slate-500 block uppercase tracking-wider font-semibold">Confidence</span>
            <span className="block mt-1 font-bold text-slate-200 text-sm font-mono">
              {(confidence * 100).toFixed(0)}%
            </span>
          </div>

          <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
            <span className="text-[10px] text-slate-500 block uppercase tracking-wider font-semibold">Provider</span>
            <span className="block mt-1 font-medium text-slate-300 truncate" title={provider}>
              {provider}
            </span>
          </div>
        </div>

        {/* Source Origin Card */}
        <div className="bg-slate-950/50 p-4 rounded-xl border border-slate-800/80 space-y-2 text-xs">
          <div className="flex items-center space-x-2 text-slate-300 font-semibold">
            <FileText className="w-4 h-4 text-indigo-400" />
            <span>Document & Source Origin</span>
          </div>
          <p className="text-slate-200 font-medium">{sourceTitle}</p>
          <div className="flex justify-between text-[11px] text-slate-400 pt-1 border-t border-slate-800/50">
            <span>Retrieved: {new Date(retrievedAt).toLocaleString()}</span>
            <span>Published: {publishedAt ? new Date(publishedAt).toLocaleDateString() : 'Continuous'}</span>
          </div>
        </div>

        {/* 4-Layer Lineage Chain of Custody */}
        <div className="space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
            <Layers className="w-3.5 h-3.5 text-indigo-400" />
            <span>4-Layer Data Lineage Chain of Custody</span>
          </h4>

          <div className="relative border-l-2 border-indigo-900/60 ml-3 space-y-4 pl-4 py-1">
            {defaultLineage.map((node, idx) => (
              <div key={idx} className="relative">
                <div className="absolute -left-[23px] top-1.5 w-3.5 h-3.5 rounded-full bg-indigo-600 border-2 border-slate-900" />
                <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800/60 space-y-1">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-bold text-white">{node.title}</span>
                    <span className="text-[10px] font-mono text-indigo-400">
                      Layer: {node.level}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400">{node.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end pt-2 border-t border-slate-800">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition-colors"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
};
export default DataProvenanceModal;
