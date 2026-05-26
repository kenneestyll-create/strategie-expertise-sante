import { useState, useEffect, useCallback } from 'react';
import { safeStorage } from '../utils/safeStorage';

const STORAGE_KEY = 'ses-admin-theme';

export function useAdminTheme() {
  const getSystemPreference = () =>
    window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';

  const [preference, setPreference] = useState(() => safeStorage.get(STORAGE_KEY) || 'system');

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
      safeStorage.set(STORAGE_KEY, next);
      return next;
    });
  }, []);

  const reset = useCallback(() => {
    safeStorage.remove(STORAGE_KEY);
    setPreference('system');
  }, []);

  return { isDark, preference, toggle, reset };
}
