import { useState, useEffect, useCallback } from 'react';

const STORAGE_KEY = 'ses-admin-theme';

export function useAdminTheme() {
  const getSystemPreference = () =>
    window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';

  const [preference, setPreference] = useState(() => {
    try {
      return localStorage.getItem(STORAGE_KEY) || 'system';
    } catch {
      return 'system';
    }
  });

  const resolved = preference === 'system' ? getSystemPreference() : preference;
  const isDark = resolved === 'dark';

  // Sync body class for portals (dialogs, popovers, selects)
  useEffect(() => {
    if (isDark) {
      document.body.classList.add('admin-dark');
    } else {
      document.body.classList.remove('admin-dark');
    }
    return () => document.body.classList.remove('admin-dark');
  }, [isDark]);

  useEffect(() => {
    const mq = window.matchMedia?.('(prefers-color-scheme: dark)');
    if (!mq || preference !== 'system') return;
    const handler = () => setPreference(p => p === 'system' ? 'system' : p);
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, [preference]);

  const toggle = useCallback(() => {
    setPreference(prev => {
      const next = (prev === 'system' ? getSystemPreference() : prev) === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem(STORAGE_KEY, next); } catch {}
      return next;
    });
  }, []);

  const reset = useCallback(() => {
    try { localStorage.removeItem(STORAGE_KEY); } catch {}
    setPreference('system');
  }, []);

  return { isDark, preference, toggle, reset };
}
