import React, { useEffect, useRef } from 'react';
import { Download, Printer, X, FileText, CheckCircle, AlertTriangle, ShieldCheck } from 'lucide-react';
import { AnalysisResponse, AgentFinding, SignalConflict } from '../../types';

interface ExportReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  analysis: AnalysisResponse | null;
}

export const ExportReportModal: React.FC<ExportReportModalProps> = ({ isOpen, onClose, analysis }) => {
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

  if (!isOpen || !analysis) return null;

  const handlePrint = () => {
    window.print();
  };

  const handleDownloadMarkdown = () => {
    const mdContent = `# MATS INSTITUTIONAL FINANCIAL INTELLIGENCE REPORT
Target Security: ${analysis.symbol}
Generated At: ${new Date().toUTCString()}
Analysis ID: ${analysis.request_id}
Overall Assessment: ${analysis.overall_assessment} (Confidence: ${Math.round(analysis.confidence * 100)}%)

---

## 1. Executive Summary
${analysis.summary}

## 2. Multi-Agent Findings
${analysis.agents.map((a: AgentFinding) => `### ${a.agent.toUpperCase()} AGENT (${a.signal})
- Confidence: ${Math.round(a.confidence * 100)}%
- Finding: ${a.finding}
- Evidence: ${a.evidence.join('; ')}
`).join('\n')}

## 3. Conflict Analysis & Consensus
${analysis.conflicts.length > 0 
  ? analysis.conflicts.map((c: SignalConflict) => `- **${c.conflict_type}**: ${c.description} (Severity: ${c.severity})`).join('\n')
  : '- Consensus reached. No direct signal contradictions detected among active agents.'}

## 4. Personalized Context & Risk Recommendation
- Assessment: ${analysis.recommendation?.assessment || 'HOLD'}
- Key Drivers: ${analysis.recommendation?.key_reasons?.join(', ') || 'N/A'}
- Primary Risks: ${analysis.recommendation?.risks?.join(', ') || 'N/A'}
- Key Factors To Monitor: ${analysis.recommendation?.what_to_monitor?.join(', ') || 'N/A'}
${analysis.recommendation?.personalization_note ? `- Investor Alignment: ${analysis.recommendation.personalization_note}` : ''}

## 5. RAG Sources & Data Provenance
${analysis.sources.map((s: string) => `- ${s}`).join('\n')}

---
### Regulatory Disclaimer
MATS is an autonomous decision-support system provided for informational research purposes only. It does not execute trades, manage funds, or offer personalized investment advice. All financial allocations require independent investor due diligence.
`;

    const blob = new Blob([mdContent], { type: 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `MATS_Report_${analysis.symbol}_${new Date().toISOString().slice(0, 10)}.md`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="report-modal-title"
      className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 overflow-y-auto"
    >
      <div
        ref={modalRef}
        className="glass-panel p-6 sm:p-8 rounded-3xl border border-white/10 max-w-3xl w-full shadow-2xl space-y-6 max-h-[90vh] overflow-y-auto my-8 relative animate-fade-in text-white"
      >
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-white/10 print:hidden">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <h2 id="report-modal-title" className="text-lg font-bold tracking-tight">
                Institutional Intelligence Report
              </h2>
              <p className="text-xs text-gray-400 font-mono-numbers">
                Analysis ID: {analysis.request_id} • Target: {analysis.symbol}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleDownloadMarkdown}
              aria-label="Download markdown report"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-xs font-semibold shadow-glow-purple transition-all focus:outline-none focus:ring-1 focus:ring-purple-400"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download .MD</span>
            </button>
            <button
              onClick={handlePrint}
              aria-label="Print or save as PDF"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-xs font-semibold transition-all focus:outline-none focus:ring-1 focus:ring-white"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>Print / PDF</span>
            </button>
            <button
              onClick={onClose}
              aria-label="Close report"
              className="p-1.5 rounded-xl text-gray-400 hover:text-white hover:bg-white/10 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Printable Report Body */}
        <div className="space-y-5 text-xs text-gray-300 font-sans leading-relaxed">
          {/* Executive Overview Banner */}
          <div className="p-4 rounded-2xl bg-black/40 border border-white/5 flex items-center justify-between">
            <div>
              <span className="text-[10px] text-gray-400 uppercase font-semibold">Consensus Assessment</span>
              <h3 className="text-base font-bold text-white uppercase">{analysis.overall_assessment}</h3>
            </div>
            <div className="text-right">
              <span className="text-[10px] text-gray-400 uppercase font-semibold">Agreement Confidence</span>
              <div className="text-base font-bold text-emerald-400 font-mono-numbers">
                {Math.round(analysis.confidence * 100)}%
              </div>
            </div>
          </div>

          {/* Synthesis */}
          <div className="space-y-1.5">
            <h4 className="text-xs font-bold text-purple-300 uppercase tracking-wider">1. Synthesis & Evidence</h4>
            <p className="p-3.5 rounded-xl bg-white/[0.02] border border-white/5 leading-relaxed text-gray-200">
              {analysis.summary}
            </p>
          </div>

          {/* Multi-Agent Breakdown */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold text-purple-300 uppercase tracking-wider">2. Autonomous Agent Cross-Examination</h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {analysis.agents.map((agent: AgentFinding, idx: number) => (
                <div key={idx} className="p-3 rounded-xl bg-black/40 border border-white/5 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-white capitalize">{agent.agent} Agent</span>
                    <span className="text-[10px] px-2 py-0.5 rounded-md bg-white/5 border border-white/10 font-bold uppercase">
                      {agent.signal}
                    </span>
                  </div>
                  <p className="text-[11px] text-gray-400">{agent.finding}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Conflict Detection */}
          <div className="space-y-1.5">
            <h4 className="text-xs font-bold text-purple-300 uppercase tracking-wider">3. Signal Disagreement & Conflict Resolution</h4>
            {analysis.conflicts && analysis.conflicts.length > 0 ? (
              analysis.conflicts.map((c: SignalConflict, i: number) => (
                <div key={i} className="p-3 rounded-xl bg-orange-950/20 border border-orange-500/20 space-y-1">
                  <div className="flex items-center gap-1.5 text-orange-400 font-bold">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    <span>{c.conflict_type}: {c.description}</span>
                  </div>
                  <p className="text-[11px] text-gray-300"><strong>Severity:</strong> {c.severity}</p>
                </div>
              ))
            ) : (
              <div className="p-2.5 rounded-xl bg-white/[0.02] border border-white/5 flex items-center gap-2 text-emerald-400 text-[11px]">
                <CheckCircle className="w-4 h-4" />
                <span>Zero signal contradictions detected. Multi-agent consensus achieved.</span>
              </div>
            )}
          </div>

          {/* Sources & Citations */}
          <div className="space-y-1.5">
            <h4 className="text-xs font-bold text-purple-300 uppercase tracking-wider">4. Verified Data Sources & Citations</h4>
            <ul className="p-3 rounded-xl bg-black/40 border border-white/5 space-y-1 text-[11px] text-gray-400 font-mono-numbers">
              {analysis.sources.map((s: string, i: number) => (
                <li key={i}>• {s}</li>
              ))}
            </ul>
          </div>

          {/* Footer Disclaimer */}
          <div className="p-3 rounded-xl bg-white/[0.02] border border-white/5 text-[10px] text-gray-400 space-y-1">
            <div className="flex items-center gap-1 text-gray-300 font-bold">
              <ShieldCheck className="w-3.5 h-3.5 text-purple-400" />
              <span>Decision Support Notice</span>
            </div>
            <p>
              This institutional intelligence report was autonomously synthesized by the MATS multi-agent system for decision-support purposes. It does not constitute investment advice or order execution. Past performance does not guarantee future financial returns.
            </p>
          </div>
        </div>

        <button
          onClick={onClose}
          className="w-full py-2 rounded-xl bg-white/10 hover:bg-white/20 text-white font-semibold text-xs transition-all focus:outline-none focus:ring-1 focus:ring-purple-500 print:hidden"
        >
          Close Report Preview
        </button>
      </div>
    </div>
  );
};
