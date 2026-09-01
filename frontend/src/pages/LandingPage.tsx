import React from 'react';
import { Link } from 'react-router-dom';
import { Hero3D } from '../components/landing/Hero3D';
import {
  BrainCircuit,
  ArrowRight,
  TrendingUp,
  Shield,
  Sparkles,
  Zap,
  Activity,
} from 'lucide-react';
import { useAuth } from '../store/authContext';

export const LandingPage: React.FC = () => {
  const { isAuthenticated } = useAuth();

  return (
    <div className="min-h-screen bg-[#08090d] text-white flex flex-col relative overflow-hidden">
      {/* Background ambient gradient fields */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] bg-gradient-to-b from-purple-700/20 via-orange-600/10 to-transparent blur-[140px] pointer-events-none" />
      <div className="absolute top-1/3 -right-40 w-[500px] h-[500px] bg-purple-900/15 blur-[160px] pointer-events-none" />

      {/* Top Navbar */}
      <header className="border-b border-white/5 bg-[#090a0f]/60 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-600 via-indigo-600 to-orange-500 flex items-center justify-center shadow-glow-purple">
              <BrainCircuit className="w-5 h-5 text-white" />
            </div>
            <div>
              <span className="text-xl font-extrabold tracking-wider text-white">MATS</span>
              <span className="text-[10px] block uppercase tracking-widest text-orange-400 font-bold">
                Autonomous Financial Intelligence
              </span>
            </div>
          </div>

          <nav className="hidden md:flex items-center gap-8 text-sm text-gray-300">
            <a href="#features" className="hover:text-white transition-colors">Capabilities</a>
            <a href="#architecture" className="hover:text-white transition-colors">Agent Swarm</a>
            <a href="#telemetry" className="hover:text-white transition-colors">Telemetry</a>
          </nav>

          <div className="flex items-center gap-3">
            {isAuthenticated ? (
              <Link
                to="/dashboard"
                className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-orange-500 hover:from-purple-500 hover:to-orange-400 text-white font-semibold text-sm shadow-glow-purple flex items-center gap-2 transition-all"
              >
                <span>Enter Dashboard</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            ) : (
              <>
                <Link
                  to="/login"
                  className="px-4 py-2 rounded-xl text-sm font-medium text-gray-300 hover:text-white hover:bg-white/5 transition-all"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-orange-500 hover:from-purple-500 hover:to-orange-400 text-white font-semibold text-sm shadow-glow-purple flex items-center gap-2 transition-all"
                >
                  <span>Launch Platform</span>
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </>
            )}
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-12 lg:pt-20 pb-16 px-6 max-w-7xl mx-auto w-full flex-1 flex flex-col justify-center">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          {/* Left Column: Copy & CTAs */}
          <div className="lg:col-span-7 space-y-6 text-center lg:text-left z-10">
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full glass-panel border border-purple-500/30 text-xs font-semibold text-purple-300">
              <Sparkles className="w-3.5 h-3.5 text-orange-400" />
              <span>Phase 1 Foundation: Core Platform & Dashboard Shell</span>
            </div>

            <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight leading-[1.1]">
              Next-Gen Autonomous{' '}
              <span className="gradient-text-purple-orange">Financial Intelligence</span>
            </h1>

            <p className="text-base sm:text-lg text-gray-400 max-w-2xl mx-auto lg:mx-0 leading-relaxed">
              MATS powers institutional-grade quantitative modeling, predictive revenue trajectories, 
              and autonomous multi-agent portfolio coordination through unified real-time analytics.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4 pt-4">
              <Link
                to="/register"
                className="w-full sm:w-auto px-8 py-3.5 rounded-xl bg-gradient-to-r from-purple-600 via-indigo-600 to-orange-500 text-white font-bold text-sm shadow-glow-purple flex items-center justify-center gap-2.5 hover:opacity-95 transition-all"
              >
                <span>Get Started Free</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                to="/dashboard"
                className="w-full sm:w-auto px-7 py-3.5 rounded-xl glass-panel border border-white/10 hover:border-purple-500/40 text-gray-300 hover:text-white font-semibold text-sm transition-all flex items-center justify-center gap-2"
              >
                <Activity className="w-4 h-4 text-purple-400" />
                <span>Live Analytics Demo</span>
              </Link>
            </div>

            {/* Quick Metrics Bar */}
            <div className="pt-8 grid grid-cols-3 gap-6 border-t border-white/5 max-w-lg mx-auto lg:mx-0">
              <div>
                <div className="text-2xl font-bold text-white font-mono-numbers">99.4%</div>
                <div className="text-xs text-gray-400 mt-0.5">Model Accuracy</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-orange-400 font-mono-numbers">&lt;10ms</div>
                <div className="text-xs text-gray-400 mt-0.5">Cluster Latency</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-purple-400 font-mono-numbers">$1.28M</div>
                <div className="text-xs text-gray-400 mt-0.5">Simulated ARR</div>
              </div>
            </div>
          </div>

          {/* Right Column: 3D Animated Hero Visual */}
          <div className="lg:col-span-5 relative">
            <Hero3D />
          </div>
        </div>
      </section>

      {/* Feature Highlights Section */}
      <section id="features" className="py-20 px-6 border-t border-white/5 bg-[#090a0f]/50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-xs font-bold uppercase tracking-widest text-orange-400 mb-2">
              System Architecture
            </h2>
            <h3 className="text-3xl font-extrabold text-white">
              Engineered for High-Frequency Autonomous Operations
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="glass-panel p-8 rounded-2xl border border-white/5 hover:border-purple-500/30 transition-all">
              <div className="p-3 w-fit rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400 mb-5">
                <TrendingUp className="w-6 h-6" />
              </div>
              <h4 className="text-lg font-bold text-white mb-2">Predictive Telemetry</h4>
              <p className="text-sm text-gray-400 leading-relaxed">
                Recharts-powered real-time forecasting tracking ARR, customer volume, and cash burn against actuals.
              </p>
            </div>

            <div className="glass-panel p-8 rounded-2xl border border-white/5 hover:border-orange-500/30 transition-all">
              <div className="p-3 w-fit rounded-xl bg-orange-500/10 border border-orange-500/20 text-orange-400 mb-5">
                <Zap className="w-6 h-6" />
              </div>
              <h4 className="text-lg font-bold text-white mb-2">Autonomous Alerts</h4>
              <p className="text-sm text-gray-400 leading-relaxed">
                Automated risk flags, arbitrage spreads, and volatility anomaly alerts prioritized by confidence score.
              </p>
            </div>

            <div className="glass-panel p-8 rounded-2xl border border-white/5 hover:border-purple-500/30 transition-all">
              <div className="p-3 w-fit rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400 mb-5">
                <Shield className="w-6 h-6" />
              </div>
              <h4 className="text-lg font-bold text-white mb-2">Investor Profiling</h4>
              <p className="text-sm text-gray-400 leading-relaxed">
                Custom risk tolerance, investment horizon, and target return parameters configured per portfolio.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 py-8 px-6 text-center text-xs text-gray-400">
        <p>MATS Platform &copy; 2026. Built with FastAPI, React, TypeScript & Three.js.</p>
      </footer>
    </div>
  );
};
