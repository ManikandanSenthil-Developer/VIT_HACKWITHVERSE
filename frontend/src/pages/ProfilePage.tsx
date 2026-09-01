import React, { useState, useEffect } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { portfolioService } from '../services/portfolio';
import { User, Shield, Target, Clock, Check, Sparkles } from 'lucide-react';
import { useAuth } from '../store/authContext';

export const ProfilePage: React.FC = () => {
  const { user } = useAuth();

  const [riskTolerance, setRiskTolerance] = useState('moderate');
  const [horizon, setHorizon] = useState('medium');
  const [sectors, setSectors] = useState('Technology,Healthcare,Clean Energy');
  const [targetReturn, setTargetReturn] = useState(14.5);
  const [experience, setExperience] = useState('intermediate');
  const [savedSuccess, setSavedSuccess] = useState(false);

  const { data: profile, isLoading } = useQuery({
    queryKey: ['investorProfile'],
    queryFn: portfolioService.getProfile,
  });

  useEffect(() => {
    if (profile) {
      setRiskTolerance(profile.risk_tolerance || 'moderate');
      setHorizon(profile.investment_horizon || 'medium');
      setSectors(profile.preferred_sectors || 'Technology,Healthcare,Clean Energy');
      setTargetReturn(profile.target_return || 14.5);
      setExperience(profile.experience_level || 'intermediate');
    }
  }, [profile]);

  const updateMutation = useMutation({
    mutationFn: portfolioService.updateProfile,
    onSuccess: () => {
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    updateMutation.mutate({
      risk_tolerance: riskTolerance as any,
      investment_horizon: horizon as any,
      preferred_sectors: sectors,
      target_return: Number(targetReturn),
      experience_level: experience,
    });
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <div>
        <div className="flex items-center gap-2">
          <User className="w-6 h-6 text-purple-400" />
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white">
            Investor Profile & Risk Parameters
          </h1>
        </div>
        <p className="text-xs sm:text-sm text-gray-400 mt-1">
          Tune your quantitative profile used by autonomous agent swarms to calibrate risk/reward constraints
        </p>
      </div>

      {isLoading ? (
        <div className="py-20 flex justify-center">
          <div className="w-8 h-8 border-2 border-purple-500/20 border-t-purple-500 rounded-full animate-spin" />
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="glass-panel p-6 sm:p-8 rounded-3xl border border-white/5 space-y-8">
          {savedSuccess && (
            <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs flex items-center gap-2">
              <Check className="w-4 h-4" />
              <span>Investor profile parameters updated successfully.</span>
            </div>
          )}

          {/* Account Overview */}
          <div className="flex items-center gap-4 pb-6 border-b border-white/5">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-purple-600 to-orange-500 flex items-center justify-center text-white text-xl font-bold shadow-glow-purple">
              {user?.full_name?.charAt(0) || 'U'}
            </div>
            <div>
              <h3 className="text-base font-bold text-white">{user?.full_name || 'Autonomous Analyst'}</h3>
              <p className="text-xs text-gray-400">{user?.email}</p>
              <div className="mt-1 flex items-center gap-2">
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-semibold">
                  Verified Trader
                </span>
                <span className="text-[10px] text-gray-500 font-mono-numbers">
                  User ID: #{user?.id}
                </span>
              </div>
            </div>
          </div>

          {/* Risk Tolerance Selection */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-gray-400 mb-3 flex items-center gap-2">
              <Shield className="w-4 h-4 text-purple-400" />
              <span>Risk Tolerance Level</span>
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {[
                { id: 'conservative', label: 'Conservative', desc: 'Preserve capital & low drawdowns' },
                { id: 'moderate', label: 'Moderate', desc: 'Balanced growth & dynamic hedging' },
                { id: 'aggressive', label: 'Aggressive', desc: 'Alpha-seeking high conviction' },
                { id: 'speculative', label: 'Speculative', desc: 'Max volatility & leveraged arb' },
              ].map((r) => (
                <div
                  key={r.id}
                  onClick={() => setRiskTolerance(r.id)}
                  className={`p-4 rounded-xl border cursor-pointer transition-all ${
                    riskTolerance === r.id
                      ? 'bg-purple-600/20 border-purple-500 text-white shadow-glow-purple'
                      : 'bg-black/20 border-white/5 text-gray-400 hover:border-white/20'
                  }`}
                >
                  <div className="text-xs font-bold text-white capitalize">{r.label}</div>
                  <div className="text-[11px] text-gray-400 mt-1 leading-snug">{r.desc}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Investment Horizon & Target Return */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-gray-400 mb-2 flex items-center gap-2">
                <Clock className="w-4 h-4 text-orange-400" />
                <span>Investment Horizon</span>
              </label>
              <select
                value={horizon}
                onChange={(e) => setHorizon(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl bg-black/50 border border-white/10 text-xs text-white focus:outline-none focus:border-purple-500"
              >
                <option value="short">Short Term (&lt; 1 Year)</option>
                <option value="medium">Medium Term (1 - 5 Years)</option>
                <option value="long">Long Term (5+ Years)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-gray-400 mb-2 flex items-center gap-2">
                <Target className="w-4 h-4 text-emerald-400" />
                <span>Annual Target Return (%)</span>
              </label>
              <input
                type="number"
                step="0.1"
                value={targetReturn}
                onChange={(e) => setTargetReturn(parseFloat(e.target.value))}
                className="w-full px-4 py-2.5 rounded-xl bg-black/50 border border-white/10 text-xs text-white focus:outline-none focus:border-purple-500 font-mono-numbers"
              />
            </div>
          </div>

          {/* Preferred Sectors */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-gray-400 mb-2">
              Target Economic Sectors (comma-separated)
            </label>
            <input
              type="text"
              value={sectors}
              onChange={(e) => setSectors(e.target.value)}
              className="w-full px-4 py-2.5 rounded-xl bg-black/50 border border-white/10 text-xs text-white focus:outline-none focus:border-purple-500"
            />
          </div>

          {/* Save Button */}
          <div className="pt-4 border-t border-white/5 flex justify-end">
            <button
              type="submit"
              disabled={updateMutation.isPending}
              className="px-6 py-3 rounded-xl bg-gradient-to-r from-purple-600 to-orange-500 hover:from-purple-500 hover:to-orange-400 text-white font-bold text-xs shadow-glow-purple flex items-center gap-2 transition-all disabled:opacity-50"
            >
              <Sparkles className="w-4 h-4" />
              <span>{updateMutation.isPending ? 'Syncing Profile...' : 'Save Parameters'}</span>
            </button>
          </div>
        </form>
      )}
    </div>
  );
};
