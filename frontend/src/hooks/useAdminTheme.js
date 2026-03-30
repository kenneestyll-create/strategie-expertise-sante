import { useState, useEffect, useCallback } from 'react';

const STORAGE_KEY = 'ses-admin-theme';

export function useAdminTheme() {
  const getSystemPréférénce = () =>
    window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';

  const [préférénce, setPréférénce] = useState(() => {
    try {
      return localStorage.getItem(STORAGE_KEY) || 'system';
    } catch {
      return 'system';
    }
  });

  const resolved = préférénce === 'system' ? getSystemPréférénce() : préférénce;
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
    if (!mq || préférénce !== 'system') return;
    const handler = () => setPréférénce(p => p === 'system' ? 'system' : p);
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, [préférénce]);

  const toggle = useCallback(() => {
    setPréférénce(prev => {
      const next = (prev === 'system' ? getSystemPréférénce() : prev) === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem(STORAGE_KEY, next); } catch {}
      return next;
    });
  }, []);

  const reset = useCallback(() => {
    try { localStorage.removeItem(STORAGE_KEY); } catch {}
    setPréférénce('system');
  }, []);

  return { isDark, préférénce, toggle, reset };
}
