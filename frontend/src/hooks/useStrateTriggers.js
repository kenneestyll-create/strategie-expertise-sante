import { useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import { safeStorage } from '../utils/safeStorage';

/**
 * useStrateTriggers — auto-open the reception chat based on:
 *   - scroll ≥ 40% OR 15s inactivity
 *   - limited to 1 auto-open per visitor per 24h (localStorage)
 *   - only on pages listed in ACTIVE_PAGES
 *   - never while an input/textarea is focused (tunnel in progress)
 *
 * The hook fires the provided `onTrigger` callback exactly once per session.
 */

// Patterns where Straté may auto-open. Static match OR regex prefix.
const ACTIVE_MATCHERS = [
  (p) => p === '/',
  (p) => p === '/tarifs',
  (p) => p === '/calculatrice-ipp',
  (p) => p === '/calculatrice-aah',
  (p) => p === '/mdph',
  (p) => p === '/accident-travail-maladie-professionnelle',
  (p) => p === '/expertise-medicale',
  (p) => p === '/medecin-conseil',
  (p) => p === '/protection-juridique',
  (p) => p.startsWith('/guide/'),
];

// Pages where Straté must never auto-open (tunnels + technical + admin).
const BLOCKED_MATCHERS = [
  (p) => p.startsWith('/admin'),
  (p) => p.startsWith('/strategiia'),
  (p) => p.startsWith('/dossier-express'),
  (p) => p.startsWith('/simulateur'),
  (p) => p.startsWith('/espace-client'),
  (p) => p.startsWith('/mentions-legales'),
  (p) => p.startsWith('/cgu'),
  (p) => p.startsWith('/cgv'),
  (p) => p.startsWith('/politique-confidentialite'),
  (p) => p.startsWith('/forum/nouveau'),
  (p) => p.startsWith('/avis'),
  (p) => p.startsWith('/contact'),
  (p) => p.startsWith('/rdv'),
  (p) => p.startsWith('/agenda'),
];

const LS_LAST_AUTO_OPEN = 'strate_last_auto_open_v1';
const COOLDOWN_MS = 24 * 60 * 60 * 1000; // 24h
const INACTIVITY_MS = 15000; // 15s
const SCROLL_THRESHOLD = 0.40; // 40%

export const canAutoOpenOnPath = (pathname) => {
  if (!pathname) return false;
  if (BLOCKED_MATCHERS.some((m) => m(pathname))) return false;
  return ACTIVE_MATCHERS.some((m) => m(pathname));
};

export const useStrateTriggers = ({ enabled = true, isOpen = false, onTrigger }) => {
  const location = useLocation();
  const firedRef = useRef(false);
  const inactivityTimerRef = useRef(null);

  useEffect(() => {
    // Reset per-session fired flag when path changes
    firedRef.current = false;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.pathname]);

  useEffect(() => {
    if (!enabled || isOpen) return;
    const path = location.pathname;
    if (!canAutoOpenOnPath(path)) return;

    // 24h cooldown
    const last = parseInt(safeStorage.get(LS_LAST_AUTO_OPEN) || '0', 10);
    if (last && Date.now() - last < COOLDOWN_MS) return;

    const maybeFire = (cause) => {
      if (firedRef.current) return;
      // Don't fire if user is typing in a form
      const active = document.activeElement;
      if (active && ['INPUT', 'TEXTAREA', 'SELECT'].includes(active.tagName)) return;
      firedRef.current = true;
      safeStorage.set(LS_LAST_AUTO_OPEN, String(Date.now()));
      onTrigger?.(cause);
    };

    // Inactivity timer
    const resetInactivity = () => {
      if (inactivityTimerRef.current) clearTimeout(inactivityTimerRef.current);
      inactivityTimerRef.current = setTimeout(() => maybeFire('inactivity'), INACTIVITY_MS);
    };

    // Scroll detector
    const onScroll = () => {
      const h = document.documentElement;
      const max = (h.scrollHeight || 1) - (h.clientHeight || 0);
      const ratio = max > 0 ? (window.scrollY || h.scrollTop) / max : 0;
      if (ratio >= SCROLL_THRESHOLD) maybeFire('scroll');
    };

    resetInactivity();
    const activityEvents = ['mousemove', 'keydown', 'click', 'touchstart'];
    activityEvents.forEach((ev) => window.addEventListener(ev, resetInactivity, { passive: true }));
    window.addEventListener('scroll', onScroll, { passive: true });

    return () => {
      if (inactivityTimerRef.current) clearTimeout(inactivityTimerRef.current);
      activityEvents.forEach((ev) => window.removeEventListener(ev, resetInactivity));
      window.removeEventListener('scroll', onScroll);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.pathname, enabled, isOpen]);
};

export default useStrateTriggers;
