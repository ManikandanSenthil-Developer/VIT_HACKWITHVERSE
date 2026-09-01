import React from 'react';
import { DollarSign, Users, CreditCard, TrendingUp, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { KpiMetric } from '../../types';

const iconMap = {
  DollarSign,
  Users,
  CreditCard,
  TrendingUp,
};

export const KpiCard: React.FC<{ metric: KpiMetric }> = ({ metric }) => {
  const Icon = iconMap[metric.iconName];

  const accentStyles = {
    purple: {
      border: 'hover:border-purple-500/40',
      iconBg: 'bg-purple-500/10 text-purple-400 border border-purple-500/20',
      glow: 'group-hover:shadow-[0_0_20px_rgba(139,92,246,0.15)]',
    },
    orange: {
      border: 'hover:border-orange-500/40',
      iconBg: 'bg-orange-500/10 text-orange-400 border border-orange-500/20',
      glow: 'group-hover:shadow-[0_0_20px_rgba(249,115,22,0.15)]',
    },
    emerald: {
      border: 'hover:border-emerald-500/40',
      iconBg: 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20',
      glow: 'group-hover:shadow-[0_0_20px_rgba(16,185,129,0.15)]',
    },
    blue: {
      border: 'hover:border-blue-500/40',
      iconBg: 'bg-blue-500/10 text-blue-400 border border-blue-500/20',
      glow: 'group-hover:shadow-[0_0_20px_rgba(59,130,246,0.15)]',
    },
  }[metric.accentColor];

  return (
    <div
      className={`group relative overflow-hidden rounded-2xl glass-panel p-5 transition-all duration-300 ${accentStyles.border} ${accentStyles.glow}`}
    >
      <div className="flex items-start justify-between">
        <span className="text-xs font-medium uppercase tracking-wider text-gray-400">
          {metric.title}
        </span>
        <div className={`p-2 rounded-xl ${accentStyles.iconBg}`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>

      <div className="mt-4">
        <div className="text-2xl lg:text-3xl font-bold tracking-tight text-white font-mono-numbers">
          {metric.value}
        </div>
        {metric.subValue && (
          <div className="text-xs text-gray-400 mt-1">
            {metric.subValue}
          </div>
        )}
      </div>

      <div className="mt-4 flex items-center justify-between border-t border-white/5 pt-3">
        <div
          className={`flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-full ${
            metric.isPositive
              ? 'text-emerald-400 bg-emerald-500/10 border border-emerald-500/20'
              : 'text-rose-400 bg-rose-500/10 border border-rose-500/20'
          }`}
        >
          {metric.isPositive ? (
            <ArrowUpRight className="w-3.5 h-3.5" />
          ) : (
            <ArrowDownRight className="w-3.5 h-3.5" />
          )}
          <span>{metric.change}</span>
        </div>
        <span className="text-[11px] text-gray-400">{metric.period}</span>
      </div>
    </div>
  );
};
