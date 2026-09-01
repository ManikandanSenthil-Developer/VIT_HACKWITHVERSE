import React, { useState } from 'react';
import { NetworkNode } from '../../types';
import { Activity, Search, Filter, Clock, Cpu } from 'lucide-react';

interface NetworkTableProps {
  nodes: NetworkNode[];
}

export const NetworkTable: React.FC<NetworkTableProps> = ({ nodes }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');

  const filteredNodes = nodes.filter((node) => {
    const matchesSearch =
      node.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      node.type.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'ALL' || node.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getStatusBadge = (status: NetworkNode['status']) => {
    switch (status) {
      case 'Active':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
      case 'Optimizing':
        return 'bg-orange-500/10 text-orange-400 border-orange-500/20';
      case 'Standby':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
      case 'Audited':
        return 'bg-purple-500/10 text-purple-400 border-purple-500/20';
      default:
        return 'bg-gray-500/10 text-gray-400 border-gray-500/20';
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border border-white/5">
      {/* Header and Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-purple-400" />
            <h2 className="text-lg font-bold text-white">Your Network & Autonomous Clusters</h2>
          </div>
          <p className="text-xs text-gray-400 mt-1">
            Real-time cluster telemetry, compute distribution, and agent latency
          </p>
        </div>

        {/* Filter controls */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative">
            <Search className="w-4 h-4 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search agent or node..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9 pr-4 py-1.5 rounded-xl bg-black/40 border border-white/10 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 transition-colors w-48 sm:w-60"
            />
          </div>

          <div className="flex items-center gap-1.5 bg-black/40 p-1 rounded-xl border border-white/10">
            <Filter className="w-3.5 h-3.5 text-gray-400 ml-1.5" />
            {['ALL', 'Active', 'Optimizing', 'Standby'].map((st) => (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
                className={`px-2.5 py-1 text-xs rounded-lg transition-all ${
                  statusFilter === st
                    ? 'bg-purple-600/30 text-purple-300 font-semibold border border-purple-500/40'
                    : 'text-gray-400 hover:text-gray-200'
                }`}
              >
                {st}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-white/5 text-[11px] uppercase tracking-wider text-gray-400 font-medium">
              <th className="pb-3 pl-2">Cluster Node</th>
              <th className="pb-3">Type</th>
              <th className="pb-3">Status</th>
              <th className="pb-3">Latency</th>
              <th className="pb-3">Throughput</th>
              <th className="pb-3">Accuracy</th>
              <th className="pb-3 pr-2 text-right">Heartbeat</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5 text-xs font-mono-numbers">
            {filteredNodes.length > 0 ? (
              filteredNodes.map((node) => (
                <tr
                  key={node.id}
                  className="hover:bg-white/[0.02] transition-colors group cursor-pointer"
                >
                  <td className="py-3.5 pl-2">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400 border border-purple-500/20 group-hover:border-purple-500/40">
                        <Cpu className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="font-semibold text-white font-sans text-sm group-hover:text-purple-300 transition-colors">
                          {node.name}
                        </div>
                        <div className="text-[11px] text-gray-500 font-mono-numbers">
                          ID: {node.id}
                        </div>
                      </div>
                    </div>
                  </td>

                  <td className="py-3.5 text-gray-300 font-sans">{node.type}</td>

                  <td className="py-3.5">
                    <span
                      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold border ${getStatusBadge(
                        node.status
                      )}`}
                    >
                      <span className="w-1.5 h-1.5 rounded-full bg-current" />
                      {node.status}
                    </span>
                  </td>

                  <td className="py-3.5 text-gray-300">{node.latency}</td>

                  <td className="py-3.5 text-gray-300">{node.throughput}</td>

                  <td className="py-3.5">
                    <span className="text-emerald-400 font-bold">{node.accuracy}</span>
                  </td>

                  <td className="py-3.5 pr-2 text-right text-gray-500">
                    <div className="flex items-center justify-end gap-1.5">
                      <Clock className="w-3 h-3 text-gray-400" />
                      <span>{node.lastUpdated}</span>
                    </div>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={7} className="text-center py-8 text-gray-500">
                  No matching network nodes found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
