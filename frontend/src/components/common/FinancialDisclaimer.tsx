import React, { useState } from 'react';
import { ShieldAlert, ChevronDown, ChevronUp } from 'lucide-react';

export const FinancialDisclaimer: React.FC = () => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <aside
      aria-label="Financial and Legal Disclaimer"
      className="p-3.5 rounded-2xl bg-white/[0.02] border border-white/10 text-xs text-gray-400 space-y-2 transition-all"
    >
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-purple-400 shrink-0" aria-hidden="true" />
          <p className="text-[11px] leading-relaxed font-sans text-gray-300">
            <strong>Decision-Support Notice:</strong> MATS provides AI-generated financial research summaries and scenario stress testing for informational purposes only. It does not execute trades, place orders, or constitute personalized investment advice.
          </p>
        </div>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          aria-expanded={isExpanded}
          className="text-[10px] text-purple-400 hover:text-purple-300 font-semibold flex items-center gap-1 shrink-0 px-2 py-1 rounded-lg hover:bg-white/5 transition-colors focus:outline-none focus:ring-1 focus:ring-purple-500"
        >
          <span>{isExpanded ? 'Less' : 'Full Legal Disclosure'}</span>
          {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
        </button>
      </div>

      {isExpanded && (
        <div className="pt-2 border-t border-white/5 space-y-2 text-[10px] text-gray-400 leading-relaxed font-sans animate-fade-in">
          <p>
            MATS is not a registered investment advisor, broker-dealer, or financial analyst under FINRA, SEC, or international regulatory authorities. Content generated does not constitute an endorsement, recommendation, or solicitation to purchase, hold, or liquidate any security, derivative, or financial instrument.
          </p>
          <p>
            Market telemetry, historical volatility, and RAG document citations are retrieved from third-party sources (SEC Edgar, financial APIs). While MATS enforces zero-fabrication and deterministic calculations, past performance does not guarantee future results. Users maintain full responsibility for independent due diligence and capital allocation decisions.
          </p>
        </div>
      )}
    </aside>
  );
};
