import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { UserAccessibilityPreference } from '../types';
import { ecosystemService } from '../services/ecosystemService';

interface AccessibilityContextType {
  preferences: UserAccessibilityPreference;
  setLanguage: (lang: 'en' | 'ta' | 'hi') => void;
  setTextSize: (size: 'normal' | 'large' | 'extra_large') => void;
  setReducedMotion: (val: boolean) => void;
  setHighContrast: (val: boolean) => void;
  setVoiceEnabled: (val: boolean) => void;
  updatePreferences: (updates: Partial<UserAccessibilityPreference>) => Promise<void>;
}

const DEFAULT_PREFERENCES: UserAccessibilityPreference = {
  language: 'en',
  text_size: 'normal',
  reduced_motion: false,
  high_contrast: false,
  voice_enabled: true,
};

const AccessibilityContext = createContext<AccessibilityContextType | undefined>(undefined);

export const AccessibilityProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [preferences, setPreferences] = useState<UserAccessibilityPreference>(() => {
    const saved = localStorage.getItem('mats_accessibility_pref');
    return saved ? JSON.parse(saved) : DEFAULT_PREFERENCES;
  });

  useEffect(() => {
    // Apply classes to root html tag for universal CSS scaling
    const root = document.documentElement;

    // 1. Text size
    root.classList.remove('text-size-normal', 'text-size-large', 'text-size-extra_large');
    root.classList.add(`text-size-${preferences.text_size}`);

    // 2. High contrast
    if (preferences.high_contrast) {
      root.classList.add('high-contrast-mode');
    } else {
      root.classList.remove('high-contrast-mode');
    }

    // 3. Reduced motion
    if (preferences.reduced_motion) {
      root.classList.add('reduced-motion-mode');
    } else {
      root.classList.remove('reduced-motion-mode');
    }

    localStorage.setItem('mats_accessibility_pref', JSON.stringify(preferences));
  }, [preferences]);

  const updatePreferences = async (updates: Partial<UserAccessibilityPreference>) => {
    const next = { ...preferences, ...updates };
    setPreferences(next);
    try {
      if (localStorage.getItem('mats_access_token')) {
        await ecosystemService.updateAccessibilityPreferences(updates);
      }
    } catch (err) {
      // Local state still applies smoothly
    }
  };

  const setLanguage = (lang: 'en' | 'ta' | 'hi') => updatePreferences({ language: lang });
  const setTextSize = (size: 'normal' | 'large' | 'extra_large') => updatePreferences({ text_size: size });
  const setReducedMotion = (val: boolean) => updatePreferences({ reduced_motion: val });
  const setHighContrast = (val: boolean) => updatePreferences({ high_contrast: val });
  const setVoiceEnabled = (val: boolean) => updatePreferences({ voice_enabled: val });

  return (
    <AccessibilityContext.Provider
      value={{
        preferences,
        setLanguage,
        setTextSize,
        setReducedMotion,
        setHighContrast,
        setVoiceEnabled,
        updatePreferences,
      }}
    >
      {children}
    </AccessibilityContext.Provider>
  );
};

export const useAccessibility = (): AccessibilityContextType => {
  const context = useContext(AccessibilityContext);
  if (!context) {
    throw new Error('useAccessibility must be used within an AccessibilityProvider');
  }
  return context;
};
