import { useEffect, useRef, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import { toast } from 'sonner';

const PROTECTED_PATHS = [
  '/',
  '/a-propos',
  '/accompagnements',
  '/expertise-medicale',
  '/accident-travail-maladie-professionnelle',
  '/mdph',
  '/seminaires',
  '/entreprises',
  '/protection-juridique',
  '/tarifs',
  '/partenaires',
  '/avis',
  '/ressources',
  '/medecin-conseil',
];

const UNPROTECTED_PREFIXES = [
  '/admin',
  '/espace-client',
  '/dossier-express',
  '/contact',
  '/simulateur',
  '/calculatrice',
  '/forum',
  '/parrainage',
  '/agenda',
  '/mentions-legales',
  '/politique-confidentialite',
];

function isProtectedPath(pathname) {
  if (UNPROTECTED_PREFIXES.some(function(p) { return pathname.startsWith(p); })) return false;
  return PROTECTED_PATHS.includes(pathname);
}

function isInteractiveElement(el) {
  if (!el) return false;
  const tag = el.tagName;
  if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return true;
  if (el.isContentEditable) return true;
  if (el.closest('input, textarea, select, [contenteditable="true"]')) return true;
  if (el.closest('[role="textbox"], [role="combobox"], [role="listbox"]')) return true;
  if (el.closest('.chatbot-container, [data-testid*="chat"], [data-testid*="input"]')) return true;
  return false;
}

function isMobile() {
  return /Android|iPhone|iPad|iPod|webOS|BlackBerry|Opera Mini|IEMobile/i.test(navigator.userAgent);
}

export function useContentProtection() {
  const { pathname } = useLocation();
  const lastToast = useRef(0);
  const active = isProtectedPath(pathname);

  const showToast = useCallback(function() {
    const now = Date.now();
    if (now - lastToast.current < 8000) return;
    lastToast.current = now;
    if (!isMobile()) {
      toast('Contenu prot\u00e9g\u00e9', {
        duration: 2000,
        style: {
          background: '#1a1a1a',
          color: '#C9A84C',
          border: '1px solid rgba(201,168,76,0.2)',
          fontSize: '13px',
        },
      });
    }
  }, []);

  useEffect(function() {
    if (!active) {
      document.body.classList.remove('content-protected');
      return;
    }

    document.body.classList.add('content-protected');

    function onContextMenu(e) {
      if (isInteractiveElement(e.target)) return;
      e.preventDefault();
      showToast();
    }

    function onKeyDown(e) {
      if (isInteractiveElement(e.target)) return;
      const ctrl = e.ctrlKey || e.metaKey;
      const shift = e.shiftKey;
      if (e.key === 'F12') { e.preventDefault(); return; }
      if (ctrl && !shift) {
        const k = e.key.toLowerCase();
        if (k === 'c' || k === 'u' || k === 's' || k === 'p') {
          e.preventDefault();
          if (k === 'c') showToast();
          return;
        }
      }
      if (ctrl && shift) {
        const k2 = e.key.toLowerCase();
        if (k2 === 'i' || k2 === 'j' || k2 === 'c') {
          e.preventDefault();
          return;
        }
      }
    }

    function onCopy(e) {
      if (isInteractiveElement(e.target)) return;
      e.preventDefault();
      showToast();
    }

    function onCut(e) {
      if (isInteractiveElement(e.target)) return;
      e.preventDefault();
    }

    function onDragStart(e) {
      const tag = e.target.tagName;
      if (tag === 'IMG' || tag === 'PICTURE') {
        e.preventDefault();
      }
    }

    function onSelectStart(e) {
      if (isInteractiveElement(e.target)) return;
      if (isMobile()) return;
      e.preventDefault();
    }

    document.addEventListener('contextmenu', onContextMenu);
    document.addEventListener('keydown', onKeyDown);
    document.addEventListener('copy', onCopy);
    document.addEventListener('cut', onCut);
    document.addEventListener('dragstart', onDragStart);
    document.addEventListener('selectstart', onSelectStart);

    return function() {
      document.body.classList.remove('content-protected');
      document.removeEventListener('contextmenu', onContextMenu);
      document.removeEventListener('keydown', onKeyDown);
      document.removeEventListener('copy', onCopy);
      document.removeEventListener('cut', onCut);
      document.removeEventListener('dragstart', onDragStart);
      document.removeEventListener('selectstart', onSelectStart);
    };
  }, [active, showToast]);
}
