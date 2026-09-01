import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { alertsService } from '../../services/alerts';
import {
  Bell,
  AlertTriangle,
  Zap,
  Info,
  CheckCircle2,
  ThumbsUp,
  X,
  ChevronRight,
  ShieldAlert,
  Cpu,
} from 'lucide-react';
import { AlertItem } from '../../types';

export const ProactiveIntelligenceFeed: React.FC = () => {
  const queryClient = useQueryClient();
  const [filterTab, setFilterTab] = useState<'ALL' | 'UNREAD' | 'URGENT'>('ALL');
  const [selectedAlert, setSelectedAlert] = useState<AlertItem | null>(null);

  // 1. Fetch live alerts
  const { data: alerts, isLoading } = useQuery({
    queryKey: ['alerts', filterTab],
    queryFn: () => {
      if (filterTab === 'UNREAD') {
        return alertsService.getAlerts({ status: 'NEW' });
      }
      if (filterTab === 'URGENT') {
        return alertsService.getAlerts({ priority: 'URGENT' });
      }
      return alertsService.getAlerts();
    },
    refetchInterval: 15000, // Background poll every 15s
  });

  // 2. Alert mutation
  const updateAlertMutation = useMutation({
    mutationFn: ({ id, status, feedback }: { id: number; status?: string; feedback?: string }) =>
      alertsService.updateAlert(id, { status, feedback }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
    },
  });

  // 3. Dismiss all
  const dismissAllMutation = useMutation({
    mutationFn: alertsService.dismissAll,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
    },
  });

  const handleOpenAlert = (alert: AlertItem) => {
    setSelectedAlert(alert);
    if (alert.status === 'NEW') {
      updateAlertMutation.mutate({ id: alert.id, status: 'SEEN' });
    }
  };

  const handleDismiss = (e: React.MouseEvent, id: number) => {
    e.stopPropagation();
    updateAlertMutation.mutate({ id, status: 'DISMISSED' });
  };

  const handleFeedback = (e: React.MouseEvent, id: number, feedback: 'HELPFUL' | 'NOT_HELPFUL') => {
    e.stopPropagation();
    updateAlertMutation.mutate({ id, feedback });
  };

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'URGENT':
        return {
          icon: AlertTriangle,
          badgeClass: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
          dotClass: 'bg-rose-400 animate-ping',
        };
      case 'IMPORTANT':
        return {
          icon: Zap,
          badgeClass: 'bg-orange-500/10 text-orange-400 border-orange-500/30',
          dotClass: 'bg-orange-400',
        };
      default:
        return {
          icon: Info,
          badgeClass: 'bg-purple-500/10 text-purple-300 border-purple-500/30',
          dotClass: 'bg-purple-400',
        };
    }
  };

  const unreadCount = alerts?.filter((a) => a.status === 'NEW').length || 0;

  return (
    <div className="glass-panel rounded-3xl p-6 border border-white/5 flex flex-col h-full space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-300">
            <Bell className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white tracking-tight">
              Proactive Intelligence Feed
            </h3>
            <span className="text-[11px] text-gray-400">
              Autonomous event detection & alerts
            </span>
          </div>
        </div>

        {unreadCount > 0 && (
          <span className="text-[11px] font-bold px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/30 font-mono-numbers">
            {unreadCount} Unread
          </span>
        )}
      </div>

      {/* Filter Tabs & Dismiss All */}
      <div className="flex items-center justify-between gap-2 border-b border-white/5 pb-3">
        <div className="flex items-center gap-1.5 text-xs">
          <button
            onClick={() => setFilterTab('ALL')}
            className={`px-2.5 py-1 rounded-xl transition-all ${
              filterTab === 'ALL'
                ? 'bg-purple-600/30 text-white font-bold border border-purple-500/30'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilterTab('UNREAD')}
            className={`px-2.5 py-1 rounded-xl transition-all ${
              filterTab === 'UNREAD'
                ? 'bg-purple-600/30 text-white font-bold border border-purple-500/30'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            Unread
          </button>
          <button
            onClick={() => setFilterTab('URGENT')}
            className={`px-2.5 py-1 rounded-xl transition-all ${
              filterTab === 'URGENT'
                ? 'bg-purple-600/30 text-white font-bold border border-purple-500/30'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            Urgent
          </button>
        </div>

        {alerts && alerts.length > 0 && (
          <button
            onClick={() => dismissAllMutation.mutate()}
            disabled={dismissAllMutation.isPending}
            className="text-[10px] text-gray-500 hover:text-gray-300 transition-colors"
          >
            Dismiss All
          </button>
        )}
      </div>

      {/* Alerts List */}
      <div className="space-y-3 overflow-y-auto max-h-[480px] pr-1">
        {isLoading ? (
          <div className="py-12 text-center text-xs text-gray-500 animate-pulse">
            Scanning active watchlists and holdings...
          </div>
        ) : alerts && alerts.length > 0 ? (
          alerts.map((alert) => {
            const badge = getPriorityBadge(alert.priority);
            const Icon = badge.icon;

            return (
              <div
                key={alert.id}
                onClick={() => handleOpenAlert(alert)}
                className={`p-4 rounded-2xl border transition-all cursor-pointer space-y-2.5 relative group ${
                  alert.status === 'NEW'
                    ? 'bg-white/[0.04] border-purple-500/40 shadow-glow-purple'
                    : 'bg-black/30 border-white/5 hover:border-white/20'
                }`}
              >
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full border flex items-center gap-1 ${badge.badgeClass}`}
                    >
                      <span className={`w-1.5 h-1.5 rounded-full ${badge.dotClass}`} />
                      <Icon className="w-2.5 h-2.5" />
                      {alert.priority}
                    </span>
                    <span className="text-xs font-extrabold text-white font-sans">
                      {alert.symbol}
                    </span>
                  </div>

                  <span className="text-[10px] text-gray-500 font-mono-numbers">
                    {new Date(alert.created_at).toLocaleTimeString([], {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </span>
                </div>

                <h4 className="text-xs font-bold text-gray-200 leading-snug">{alert.title}</h4>
                <p className="text-[11px] text-gray-400 line-clamp-2 leading-relaxed">
                  {alert.explanation}
                </p>

                {/* Actions & Feedback */}
                <div className="flex items-center justify-between pt-1 text-[10px]">
                  <span className="text-purple-400 font-semibold flex items-center gap-0.5 group-hover:translate-x-1 transition-transform">
                    <span>Investigate</span>
                    <ChevronRight className="w-3 h-3" />
                  </span>

                  <div className="flex items-center gap-2">
                    <button
                      onClick={(e) => handleFeedback(e, alert.id, 'HELPFUL')}
                      className={`p-1 rounded hover:bg-white/10 ${
                        alert.feedback === 'HELPFUL' ? 'text-emerald-400' : 'text-gray-500'
                      }`}
                      title="Mark Helpful"
                    >
                      <ThumbsUp className="w-3 h-3" />
                    </button>
                    <button
                      onClick={(e) => handleDismiss(e, alert.id)}
                      className="p-1 rounded hover:bg-white/10 text-gray-500 hover:text-rose-400"
                      title="Dismiss Alert"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })
        ) : (
          <div className="p-8 text-center glass-card rounded-2xl border border-white/5 space-y-2">
            <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto" />
            <h4 className="text-xs font-bold text-white">No Active Alerts</h4>
            <p className="text-[11px] text-gray-500">
              Automated surveillance verified baseline stability across your watchlists.
            </p>
          </div>
        )}
      </div>

      {/* Alert Audit Details Modal */}
      {selectedAlert && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-md flex items-center justify-center p-4">
          <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-white/10 max-w-xl w-full shadow-2xl space-y-6 max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between pb-4 border-b border-white/5">
              <div className="flex items-center gap-2.5">
                <ShieldAlert className="w-5 h-5 text-orange-400" />
                <div>
                  <h4 className="text-base font-bold text-white">Autonomous Alert Audit Details</h4>
                  <span className="text-[10px] text-gray-400 font-mono-numbers">
                    Alert ID: #{selectedAlert.id} • {selectedAlert.symbol}
                  </span>
                </div>
              </div>
              <button
                onClick={() => setSelectedAlert(null)}
                className="p-1 rounded-lg text-gray-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4 text-xs">
              <div className="p-4 rounded-2xl bg-black/50 border border-white/5 space-y-2">
                <span className="text-[10px] uppercase font-bold text-purple-400 tracking-wider">
                  Event Title & Overview
                </span>
                <h3 className="text-sm font-bold text-white">{selectedAlert.title}</h3>
                <p className="text-gray-300 leading-relaxed">{selectedAlert.explanation}</p>
              </div>

              {/* Multi-Agent Synthesis Breakdown */}
              {selectedAlert.agent_synthesis_json && (
                <div className="space-y-3">
                  <span className="text-[10px] uppercase font-bold text-gray-400 tracking-wider flex items-center gap-1.5">
                    <Cpu className="w-3.5 h-3.5 text-purple-400" />
                    Autonomous Multi-Agent Investigation Findings
                  </span>

                  {(() => {
                    try {
                      const syn = JSON.parse(selectedAlert.agent_synthesis_json);
                      return (
                        <div className="space-y-3">
                          <div className="p-3.5 rounded-xl bg-purple-950/20 border border-purple-500/20 space-y-1">
                            <span className="text-[10px] font-bold text-purple-300">
                              Overall Synthesis: {syn.overall_assessment || 'Completed'}
                            </span>
                            <p className="text-[11px] text-gray-300">
                              Confidence: {((syn.confidence || 0.8) * 100).toFixed(0)}%
                            </p>
                          </div>

                          {syn.agents && (
                            <div className="space-y-2">
                              {syn.agents.map((ag: any, idx: number) => (
                                <div key={idx} className="p-3 rounded-xl bg-black/40 border border-white/5 space-y-1">
                                  <div className="flex items-center justify-between text-[11px] font-bold">
                                    <span className="text-white uppercase">{ag.agent} Agent</span>
                                    <span className="text-orange-400">{ag.signal}</span>
                                  </div>
                                  <p className="text-[11px] text-gray-400">{ag.finding}</p>
                                </div>
                              ))}
                            </div>
                          )}

                          {syn.conflicts && syn.conflicts.length > 0 && (
                            <div className="p-3 rounded-xl bg-orange-950/20 border border-orange-500/30 text-orange-200 space-y-1">
                              <span className="text-[11px] font-bold">Signal Conflict Identified:</span>
                              <p className="text-[11px]">{syn.conflicts[0].description}</p>
                            </div>
                          )}
                        </div>
                      );
                    } catch {
                      return null;
                    }
                  })()}
                </div>
              )}
            </div>

            <button
              onClick={() => setSelectedAlert(null)}
              className="w-full py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white font-semibold text-xs transition-all"
            >
              Close Alert
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
