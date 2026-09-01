import React, { useState } from 'react';
import { EyeOff, Table } from 'lucide-react';

interface AccessibleChartAlternativeProps {
  chartTitle: string;
  summaryText: string;
  dataPoints?: Array<{ label: string; value: string | number }>;
  trendDescription?: string;
}

export const AccessibleChartAlternative: React.FC<AccessibleChartAlternativeProps> = ({
  chartTitle,
  summaryText,
  dataPoints = [],
  trendDescription,
}) => {
  const [showTable, setShowTable] = useState(false);

  return (
    <div className="mt-2 text-xs" role="region" aria-label={`Text alternative for ${chartTitle}`}>
      {/* Screen-reader only announcement */}
      <p className="sr-only">
        {chartTitle}: {summaryText} {trendDescription ? `Trend: ${trendDescription}` : ''}
      </p>

      {/* Accessible visual toggle for Senior / Low-Vision mode */}
      <div className="flex items-center justify-between bg-slate-950/40 px-3 py-2 rounded-lg border border-slate-800/60">
        <span className="text-[11px] text-slate-400 font-medium">
          Accessible Summary: <strong className="text-slate-200">{summaryText}</strong>
        </span>
        {dataPoints.length > 0 && (
          <button
            onClick={() => setShowTable(!showTable)}
            aria-expanded={showTable}
            className="text-[11px] text-indigo-400 hover:text-indigo-300 flex items-center space-x-1 transition-colors"
          >
            {showTable ? <EyeOff className="w-3 h-3" /> : <Table className="w-3 h-3" />}
            <span>{showTable ? 'Hide Data Table' : 'View Data Table'}</span>
          </button>
        )}
      </div>

      {showTable && dataPoints.length > 0 && (
        <div className="mt-2 overflow-x-auto rounded-lg border border-slate-800 bg-slate-950 p-2">
          <table className="w-full text-left text-[11px]">
            <caption className="sr-only">Data points for {chartTitle}</caption>
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="py-1 px-2">Metric / Date</th>
                <th className="py-1 px-2 text-right">Value</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-900 text-slate-300">
              {dataPoints.map((dp, idx) => (
                <tr key={idx}>
                  <td className="py-1 px-2 font-medium">{dp.label}</td>
                  <td className="py-1 px-2 text-right font-mono">{dp.value}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
export default AccessibleChartAlternative;
