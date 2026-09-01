import React, { useState } from 'react';
import { Settings, Key, Server, Check } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const [copied, setCopied] = useState(false);

  const token = localStorage.getItem('mats_access_token') || 'None';

  const copyToken = () => {
    navigator.clipboard.writeText(token);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <div>
        <div className="flex items-center gap-2">
          <Settings className="w-6 h-6 text-gray-400" />
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
            Platform Settings & Configuration
          </h1>
        </div>
        <p className="text-xs sm:text-sm text-gray-400 mt-1">
          Manage system configurations, environment variables, and authentication tokens
        </p>
      </div>

      <div className="space-y-6">
        {/* System & Architecture Info */}
        <div className="glass-panel p-6 rounded-2xl border border-white/5 space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-white/5">
            <Server className="w-5 h-5 text-purple-400" />
            <h3 className="text-base font-bold text-white">System Architecture (Phase 1)</h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs font-mono-numbers">
            <div className="p-3.5 rounded-xl bg-black/30 border border-white/5">
              <span className="text-gray-400 block mb-1">Backend Engine</span>
              <span className="font-bold text-white">FastAPI + Python 3.11 + SQLAlchemy</span>
            </div>

            <div className="p-3.5 rounded-xl bg-black/30 border border-white/5">
              <span className="text-gray-400 block mb-1">Database & Migration</span>
              <span className="font-bold text-white">PostgreSQL / SQLite + Alembic</span>
            </div>

            <div className="p-3.5 rounded-xl bg-black/30 border border-white/5">
              <span className="text-gray-400 block mb-1">Frontend Framework</span>
              <span className="font-bold text-white">Vite + React 18 + TypeScript + Tailwind</span>
            </div>

            <div className="p-3.5 rounded-xl bg-black/30 border border-white/5">
              <span className="text-gray-400 block mb-1">Visualization & 3D</span>
              <span className="font-bold text-white">Recharts + Three.js WebGL</span>
            </div>
          </div>
        </div>

        {/* JWT & Security Credentials */}
        <div className="glass-panel p-6 rounded-2xl border border-white/5 space-y-4">
          <div className="flex items-center gap-2 pb-3 border-b border-white/5">
            <Key className="w-5 h-5 text-orange-400" />
            <h3 className="text-base font-bold text-white">Active Session Bearer Token</h3>
          </div>

          <p className="text-xs text-gray-400">
            Current JSON Web Token (JWT) used to authenticate REST API endpoints.
          </p>

          <div className="relative">
            <input
              type="text"
              readOnly
              value={token}
              className="w-full pl-3.5 pr-24 py-2.5 rounded-xl bg-black/50 border border-white/10 text-xs text-gray-300 font-mono-numbers focus:outline-none"
            />
            <button
              onClick={copyToken}
              className="absolute right-1.5 top-1/2 -translate-y-1/2 px-3 py-1.5 rounded-lg bg-purple-600/30 border border-purple-500/40 text-purple-300 text-xs hover:bg-purple-600/50 transition-colors flex items-center gap-1.5"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : null}
              <span>{copied ? 'Copied!' : 'Copy JWT'}</span>
            </button>
          </div>
        </div>

        {/* Phase 2 Preview alert */}
        <div className="glass-panel p-6 rounded-2xl border border-purple-500/20 bg-purple-950/10 space-y-2">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-purple-400 animate-ping" />
            <h4 className="text-sm font-bold text-white">Phase 2 Roadmap: Market Data & RAG Engine</h4>
          </div>
          <p className="text-xs text-gray-400 leading-relaxed">
            Phase 1 foundation is locked and operational. Upon completion of testing, Phase 2 will introduce 
            live WebSocket market feeds, Pinecone/Chroma vector embeddings, and LangChain/CrewAI autonomous agents.
          </p>
        </div>
      </div>
    </div>
  );
};
