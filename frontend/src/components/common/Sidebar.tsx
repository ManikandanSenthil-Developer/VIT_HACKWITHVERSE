import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  PieChart,
  Eye,
  User,
  Settings,
  LogOut,
  BrainCircuit,
  ChevronLeft,
  ChevronRight,
  Bot,
  Layers,
  Globe,
} from 'lucide-react';
import { useAuth } from '../../store/authContext';

interface SidebarProps {
  collapsed: boolean;
  setCollapsed: (val: boolean) => void;
}

const navItems = [
  { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
  { name: 'Investor Copilot', path: '/copilot', icon: Bot },
  { name: 'Research Lab', path: '/research', icon: Layers },
  { name: 'Ecosystem & Voice', path: '/ecosystem', icon: Globe },
  { name: 'Portfolio', path: '/portfolio', icon: PieChart },
  { name: 'Watchlist', path: '/watchlist', icon: Eye },
  { name: 'Profile', path: '/profile', icon: User },
  { name: 'Settings', path: '/settings', icon: Settings },
];

export const Sidebar: React.FC<SidebarProps> = ({ collapsed, setCollapsed }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <aside
      className={`fixed top-0 left-0 h-screen z-40 flex flex-col transition-all duration-300 border-r border-white/5 bg-[#0b0d14]/90 backdrop-blur-2xl ${
        collapsed ? 'w-20' : 'w-64'
      }`}
    >
      {/* Brand Logo Header */}
      <div className="h-16 flex items-center justify-between px-5 border-b border-white/5">
        <div className="flex items-center gap-3 overflow-hidden cursor-pointer" onClick={() => navigate('/dashboard')}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-600 via-indigo-600 to-orange-500 flex items-center justify-center shadow-glow-purple flex-shrink-0">
            <BrainCircuit className="w-5 h-5 text-white" />
          </div>
          {!collapsed && (
            <div className="flex flex-col">
              <span className="text-base font-extrabold tracking-wider text-white">MATS</span>
              <span className="text-[10px] uppercase tracking-widest text-orange-400 font-semibold">Autonomous Core</span>
            </div>
          )}
        </div>

        <button
          onClick={() => setCollapsed(!collapsed)}
          className="hidden md:flex p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-white/5 transition-colors"
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 py-6 px-3 space-y-1.5 overflow-y-auto">
        <div className={`text-[11px] font-semibold tracking-wider uppercase text-gray-400 mb-3 px-3 ${collapsed ? 'text-center' : ''}`}>
          {collapsed ? '•••' : 'Platform Menu'}
        </div>

        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3.5 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-gradient-to-r from-purple-600/30 to-purple-800/10 text-white border border-purple-500/40 shadow-glow-purple'
                    : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
                } ${collapsed ? 'justify-center px-0' : ''}`
              }
              title={collapsed ? item.name : undefined}
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              {!collapsed && <span>{item.name}</span>}
            </NavLink>
          );
        })}
      </nav>

      {/* User profile & Logout Footer */}
      <div className="p-3 border-t border-white/5">
        <div className={`flex items-center gap-3 p-2 rounded-xl bg-white/[0.02] border border-white/5 ${collapsed ? 'justify-center p-2' : ''}`}>
          <div className="w-9 h-9 rounded-full bg-gradient-to-br from-purple-500 to-orange-500 flex items-center justify-center text-white font-bold text-xs flex-shrink-0 shadow-sm">
            {user?.full_name ? user.full_name.charAt(0).toUpperCase() : user?.email.charAt(0).toUpperCase() || 'M'}
          </div>

          {!collapsed && (
            <div className="flex-1 min-w-0">
              <p className="text-xs font-semibold text-white truncate">
                {user?.full_name || 'MATS Analyst'}
              </p>
              <p className="text-[11px] text-gray-400 truncate">
                {user?.email || 'analyst@mats.ai'}
              </p>
            </div>
          )}

          {!collapsed && (
            <button
              onClick={handleLogout}
              className="p-1.5 text-gray-400 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
              title="Sign Out"
            >
              <LogOut className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </aside>
  );
};
