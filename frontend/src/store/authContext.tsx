import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { User, AuthTokens } from '../types';
import { authService } from '../services/auth';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('mats_user');
    return saved ? JSON.parse(saved) : null;
  });
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const setAuthData = (tokens: AuthTokens) => {
    localStorage.setItem('mats_access_token', tokens.access_token);
    localStorage.setItem('mats_refresh_token', tokens.refresh_token);
    if (tokens.user) {
      localStorage.setItem('mats_user', JSON.stringify(tokens.user));
      setUser(tokens.user);
    }
  };

  const logout = useCallback(() => {
    localStorage.removeItem('mats_access_token');
    localStorage.removeItem('mats_refresh_token');
    localStorage.removeItem('mats_user');
    setUser(null);
  }, []);

  const refreshUser = useCallback(async () => {
    const token = localStorage.getItem('mats_access_token');
    if (!token) {
      setIsLoading(false);
      return;
    }
    try {
      const userData = await authService.getMe();
      setUser(userData);
      localStorage.setItem('mats_user', JSON.stringify(userData));
    } catch {
      logout();
    } finally {
      setIsLoading(false);
    }
  }, [logout]);

  useEffect(() => {
    refreshUser();

    const handleAuthLogout = () => logout();
    window.addEventListener('mats-auth-logout', handleAuthLogout);
    return () => window.removeEventListener('mats-auth-logout', handleAuthLogout);
  }, [refreshUser, logout]);

  const login = async (email: string, password: string) => {
    const tokens = await authService.login({ email, password });
    setAuthData(tokens);
    if (!tokens.user) {
      const freshUser = await authService.getMe();
      setUser(freshUser);
      localStorage.setItem('mats_user', JSON.stringify(freshUser));
    }
  };

  const register = async (email: string, password: string, fullName?: string) => {
    const tokens = await authService.register({ email, password, full_name: fullName });
    setAuthData(tokens);
    if (!tokens.user) {
      const freshUser = await authService.getMe();
      setUser(freshUser);
      localStorage.setItem('mats_user', JSON.stringify(freshUser));
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        login,
        register,
        logout,
        refreshUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
