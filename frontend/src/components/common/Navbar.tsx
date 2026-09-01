import React, { useState } from 'react';
import { Search, Bell, Menu, ShieldCheck, Activity, BarChart3 } from 'lucide-react';
import { useAuth } from '../../store/authContext';
import { TrustCenterModal } from './TrustCenterModal';
import { SystemStatusModal } from './SystemStatusModal';
import { ObservabilityModal } from './ObservabilityModal';

interface NavbarProps {
  onToggleMobileSidebar: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onToggleMobileSidebar }) => {
  const { user } = useAuth();
  const [showTrustCenter, setShowTrustCenter] = useState(false);
  const [showSystemStatus, setShowSystemStatus] = useState(false);
  const [showObservability, setShowObservability] = useState(false);

  return (
    <>
      <header className="h-16 border-b border-white/5 bg-[#090a0f]/80 backdrop-blur-xl sticky top-0 z-30 flex items-center justify-between px-4 sm:px-8">
        {/* Mobile Menu Toggle & Breadcrumbs */}
        <div className="flex items-center gap-4">
          <button
            onClick={onToggleMobileSidebar}
            aria-label="Toggle mobile navigation"
            className="md:hidden p-2 rounded-xl bg-white/5 text-gray-300 hover:text-white focus:outline-none focus:ring-1 focus:ring-purple-500"
          >
            <Menu className="w-5 h-5" />
          </button>

          <div className="hidden sm:flex items-center gap-2 text-xs">
            <span className="text-gray-400">Environment:</span>
            <span className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold font-mono-numbers">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Production Hardened v1.0.0
            </span>
          </div>
        </div>

        {/* Global Command Bar / Search */}
        <div className="hidden md:flex items-center w-72 lg:w-80 relative">
          <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" aria-hidden="true" />
          <input
            type="text"
            placeholder="Search tickers, models, or press Ctrl+K..."
            aria-label="Search tickers and financial models"
            className="w-full pl-9 pr-8 py-1.5 rounded-xl bg-black/40 border border-white/10 text-xs text-white placeholder-gray-400 focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500/50 transition-all font-sans"
          />
          <span className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[10px] text-gray-400 border border-white/10 px-1 rounded font-mono">
            ⌘K
          </span>
        </div>

        {/* Right Controls */}
        <div className="flex items-center gap-2.5">
          {/* Trust Center Trigger */}
          <button
            onClick={() => setShowTrustCenter(true)}
            aria-label="Open Trust & Safety Governance Center"
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/20 text-xs font-semibold transition-all focus:outline-none focus:ring-1 focus:ring-emerald-500"
            title="Trust, Safety & Zero-Hallucination Policy"
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Trust & Safety</span>
          </button>

          {/* System Status Telemetry Trigger */}
          <button
            onClick={() => setShowSystemStatus(true)}
            aria-label="Open System Health and Telemetry"
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-purple-500/10 hover:bg-purple-500/20 text-purple-300 border border-purple-500/20 text-xs font-semibold transition-all focus:outline-none focus:ring-1 focus:ring-purple-500"
            title="System Health Telemetry"
          >
            <Activity className="w-3.5 h-3.5" />
            <span className="hidden md:inline">Telemetry</span>
          </button>

          {/* Operational Metrics Trigger */}
          <button
            onClick={() => setShowObservability(true)}
            aria-label="Open Operational Telemetry and Metrics"
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-orange-500/10 hover:bg-orange-500/20 text-orange-300 border border-orange-500/20 text-xs font-semibold transition-all focus:outline-none focus:ring-1 focus:ring-orange-500"
            title="Observability & Agent Latency Metrics"
          >
            <BarChart3 className="w-3.5 h-3.5" />
            <span className="hidden md:inline">Metrics</span>
          </button>

          {/* Notifications */}
          <button
            aria-label="View notifications"
            className="relative p-2 rounded-xl bg-white/[0.03] hover:bg-white/[0.08] text-gray-300 hover:text-white border border-white/5 transition-colors focus:outline-none focus:ring-1 focus:ring-purple-500"
          >
            <Bell className="w-4 h-4" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-orange-500 ring-2 ring-[#090a0f]" />
          </button>

          {/* User Pill */}
          <div className="flex items-center gap-2.5 pl-2 border-l border-white/10">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-purple-600 to-orange-500 flex items-center justify-center text-white text-xs font-bold shadow-sm">
              {user?.full_name?.charAt(0) || user?.email?.charAt(0) || 'U'}
            </div>
            <div className="hidden sm:block text-left">
              <div className="text-xs font-semibold text-white leading-tight">
                {user?.full_name || 'Quantitative User'}
              </div>
              <div className="text-[10px] text-gray-400">Authenticated</div>
            </div>
          </div>
        </div>
      </header>

      {/* Modals */}
      <TrustCenterModal isOpen={showTrustCenter} onClose={() => setShowTrustCenter(false)} />
      <SystemStatusModal isOpen={showSystemStatus} onClose={() => setShowSystemStatus(false)} />
      <ObservabilityModal isOpen={showObservability} onClose={() => setShowObservability(false)} />
    </>
  );
};
