import React, { useEffect, useRef } from 'react';
import { ShieldCheck, X, Database, Cpu, AlertTriangle, Lock, Ban, CheckCircle } from 'lucide-react';

interface TrustCenterModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const TrustCenterModal: React.FC<TrustCenterModalProps> = ({ isOpen, onClose }) => {
  const modalRef = useRef<HTMLDivElement>(null);

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
      aria-labelledby="trust-center-title"
      className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 overflow-y-auto"
    >
      <div
        ref={modalRef}
        className="glass-panel p-6 sm:p-8 rounded-3xl border border-white/10 max-w-2xl w-full shadow-2xl space-y-6 max-h-[90vh] overflow-y-auto my-8 relative animate-fade-in"
      >
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-white/5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <h2 id="trust-center-title" className="text-lg font-bold text-white tracking-tight">
                MATS Trust, Safety & Governance Center
              </h2>
              <p className="text-xs text-gray-400">
                Institutional transparency • Zero financial hallucination • Decision support boundary
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            aria-label="Close Trust Center"
            className="p-1.5 rounded-xl text-gray-400 hover:text-white hover:bg-white/10 transition-colors focus:outline-none focus:ring-1 focus:ring-purple-500"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Pillars */}
        <div className="space-y-4 text-xs">
          {/* Pillar 1: Where Data Comes From */}
          <div className="p-4 rounded-2xl bg-black/40 border border-white/5 space-y-2">
            <div className="flex items-center gap-2 text-purple-300 font-bold">
              <Database className="w-4 h-4" />
              <span>1. Verified Data Provenance</span>
            </div>
            <p className="text-gray-400 leading-relaxed">
              MATS sources quotes, historical prices, and corporate balance sheets directly from normalized financial data providers (Finnhub, Yahoo Finance, and verified datasets). Regulatory documents are ingested directly from official SEC Form 10-K, 10-Q, and 8-K repositories. Stock metrics are never invented.
            </p>
          </div>

          {/* Pillar 2: How AI Works & Zero-Fabrication */}
          <div className="p-4 rounded-2xl bg-black/40 border border-white/5 space-y-2">
            <div className="flex items-center gap-2 text-orange-400 font-bold">
              <Cpu className="w-4 h-4" />
              <span>2. Multi-Agent Consensus & Zero Hallucination</span>
            </div>
            <p className="text-gray-400 leading-relaxed">
              Research requests are decomposed across specialized autonomous agents: Technical Momentum, Fundamental Valuation, Sentiment Analysis, and RAG Filings. If data is unavailable or evidence is insufficient, the system outputs: <em>&quot;Insufficient reliable evidence&quot;</em> rather than guessing.
            </p>
          </div>

          {/* Pillar 3: What Confidence Means */}
          <div className="p-4 rounded-2xl bg-black/40 border border-white/5 space-y-2">
            <div className="flex items-center gap-2 text-yellow-400 font-bold">
              <CheckCircle className="w-4 h-4" />
              <span>3. Meaning of AI Confidence Scores</span>
            </div>
            <p className="text-gray-400 leading-relaxed">
              Confidence (e.g. 82%) measures the mathematical agreement between active agents and the empirical coverage of retrieved citations. It is <strong>not a probability</strong> of market gain or return certainty.
            </p>
          </div>

          {/* Pillar 4: Signal Conflict Preservation */}
          <div className="p-4 rounded-2xl bg-black/40 border border-white/5 space-y-2">
            <div className="flex items-center gap-2 text-rose-400 font-bold">
              <AlertTriangle className="w-4 h-4" />
              <span>4. Transparent Disagreement & Conflict Detection</span>
            </div>
            <p className="text-gray-400 leading-relaxed">
              When Technical analysis is bullish but Fundamental valuation is bearish, MATS never masks or averages out the discrepancy. Conflicts are displayed prominently to empower the investor with full perspective.
            </p>
          </div>

          {/* Pillar 5: What MATS Does NOT Do */}
          <div className="p-4 rounded-2xl bg-rose-950/20 border border-rose-500/20 space-y-2">
            <div className="flex items-center gap-2 text-rose-300 font-bold">
              <Ban className="w-4 h-4" />
              <span>5. Absolute Non-Negotiable Boundaries</span>
            </div>
            <ul className="space-y-1 text-gray-300">
              <li>• MATS <strong>never</strong> executes trades or routes orders to brokerages.</li>
              <li>• MATS <strong>never</strong> requests or stores broker trading credentials.</li>
              <li>• MATS <strong>never</strong> guarantees profits or claims risk-free yield.</li>
            </ul>
          </div>

          {/* Pillar 6: User Privacy & Sovereignty */}
          <div className="p-4 rounded-2xl bg-black/40 border border-white/5 space-y-2">
            <div className="flex items-center gap-2 text-emerald-400 font-bold">
              <Lock className="w-4 h-4" />
              <span>6. Data Privacy & GDPR Sovereignty</span>
            </div>
            <p className="text-gray-400 leading-relaxed">
              Your portfolios, watchlists, proactive alerts, and research history belong strictly to your authenticated session. Passwords use BCrypt hashing. Users can request immediate permanent deletion of all account data at any time via <code>DELETE /api/v1/user/me</code>.
            </p>
          </div>
        </div>

        <button
          onClick={onClose}
          className="w-full py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white font-semibold text-xs transition-all focus:outline-none focus:ring-1 focus:ring-purple-500"
        >
          Understood & Close
        </button>
      </div>
    </div>
  );
};
