import React from 'react';
import { Outlet, Link } from 'react-router-dom';
import { BrainCircuit } from 'lucide-react';

export const AuthLayout: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#08090d] text-foreground flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden">
      {/* Background ambient lighting */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[700px] h-[350px] bg-gradient-to-b from-purple-600/20 via-orange-500/10 to-transparent blur-[120px] pointer-events-none" />
      <div className="absolute bottom-0 right-10 w-[400px] h-[400px] bg-purple-900/15 blur-[140px] pointer-events-none" />

      {/* Header / Brand */}
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center relative z-10">
        <Link to="/" className="inline-flex items-center gap-3 group">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-purple-600 via-indigo-600 to-orange-500 flex items-center justify-center shadow-glow-purple group-hover:scale-105 transition-transform">
            <BrainCircuit className="w-6 h-6 text-white" />
          </div>
          <div className="text-left">
            <span className="text-2xl font-black tracking-wider text-white">MATS</span>
            <span className="block text-[10px] uppercase tracking-widest text-orange-400 font-bold">Autonomous Financial Intelligence</span>
          </div>
        </Link>
      </div>

      {/* Card container */}
      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md relative z-10 px-4 sm:px-0">
        <div className="glass-panel py-8 px-6 sm:px-10 rounded-3xl border border-white/10 shadow-2xl backdrop-blur-2xl">
          <Outlet />
        </div>
      </div>
    </div>
  );
};
