import React from 'react';
import { KpiCard } from '../components/dashboard/KpiCard';
import { RevenueChart } from '../components/dashboard/RevenueChart';
import { NetworkTable } from '../components/dashboard/NetworkTable';
import { MarketOverview } from '../components/dashboard/MarketOverview';
import { RagSearchPanel } from '../components/dashboard/RagSearchPanel';
import { IntelligenceTerminal } from '../components/dashboard/IntelligenceTerminal';
import { PortfolioHealthWidget } from '../components/dashboard/PortfolioHealthWidget';
import { ProactiveIntelligenceFeed } from '../components/dashboard/ProactiveIntelligenceFeed';
import { DailyBriefCard } from '../components/dashboard/DailyBriefCard';
import { AutonomousMonitoringBar } from '../components/dashboard/AutonomousMonitoringBar';
import { FinancialDisclaimer } from '../components/common/FinancialDisclaimer';
import { mockKpis, mockRevenueForecast, mockNetworkNodes } from '../services/mockData';
import { useAuth } from '../store/authContext';
import { Calendar, Download, RefreshCw } from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const { user } = useAuth();

  const currentDate = new Intl.DateTimeFormat('en-US', {
    weekday: 'long',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(new Date());

  return (
    <div className="space-y-8">
      {/* Top Banner / Welcome */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Financial Intelligence Board
          </h1>
          <p className="text-xs sm:text-sm text-gray-400 mt-1">
            Welcome back, <span className="text-purple-300 font-semibold">{user?.full_name || 'Portfolio Architect'}</span>. 
            Phase 4 Autonomous Intelligence, Risk Engine & Proactive Surveillance are active.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white/[0.03] border border-white/10 text-xs text-gray-400 font-mono-numbers">
            <Calendar className="w-3.5 h-3.5 text-purple-400" />
            <span>{currentDate}</span>
          </div>

          <button
            onClick={() => window.location.reload()}
            className="p-2 rounded-xl bg-white/[0.03] hover:bg-white/[0.08] text-gray-300 hover:text-white border border-white/5 transition-all"
            title="Refresh Telemetry"
          >
            <RefreshCw className="w-4 h-4" />
          </button>

          <button
            className="px-3.5 py-2 rounded-xl bg-gradient-to-r from-purple-600 to-orange-500 hover:from-purple-500 hover:to-orange-400 text-white font-semibold text-xs shadow-glow-purple flex items-center gap-2 transition-all"
          >
            <Download className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Export Report</span>
          </button>
        </div>
      </div>

      {/* Phase 5: Financial Decision Support Disclaimer */}
      <div>
        <FinancialDisclaimer />
      </div>

      {/* Phase 4: Autonomous Surveillance & Demo Event Bar */}
      <div>
        <AutonomousMonitoringBar />
      </div>

      {/* Phase 4: Daily Financial Intelligence Brief */}
      <div>
        <DailyBriefCard />
      </div>

      {/* Phase 2: Live Market Surveillance Strip */}
      <div>
        <MarketOverview />
      </div>

      {/* Phase 4: Portfolio Risk Engine & Health Widget */}
      <div>
        <PortfolioHealthWidget />
      </div>

      {/* Phase 3: MATS Multi-Agent Autonomous Intelligence Terminal */}
      <div>
        <IntelligenceTerminal />
      </div>

      {/* 1. Top KPIs: ARR, Customers, Spend, Net Profit */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {mockKpis.map((kpi, idx) => (
          <KpiCard key={idx} metric={kpi} />
        ))}
      </div>

      {/* 2. Middle Section: Revenue Forecast Chart (Left 7 cols) + Proactive Intelligence Feed (Right 5 cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
        <div className="lg:col-span-7">
          <RevenueChart data={mockRevenueForecast} />
        </div>
        <div className="lg:col-span-5">
          <ProactiveIntelligenceFeed />
        </div>
      </div>

      {/* Phase 2: Financial RAG Knowledge Engine & Citations Panel */}
      <div>
        <RagSearchPanel />
      </div>

      {/* 3. Bottom Section: Your Network Table */}
      <div>
        <NetworkTable nodes={mockNetworkNodes} />
      </div>

      {/* Phase 5: Comprehensive Footer Disclaimer */}
      <div>
        <FinancialDisclaimer />
      </div>
    </div>
  );
};
