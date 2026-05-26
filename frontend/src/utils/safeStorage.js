/**
 * safeStorage.js — Façade résiliente sur localStorage / sessionStorage
 *
 * Objectif : éliminer définitivement les crashes React liés à un storage
 * indisponible (Chrome Mobile navigation privée, WebView Android/iOS,
 * paramètres cookies tiers, environnement sandboxé).
 *
 * Contrat :
 *   - JAMAIS de throw (try/catch obligatoire sur chaque accès).
 *   - Fallback silencieux : null en lecture, false en écriture, noop pour remove/clear.
 *   - Protection typeof window !== "undefined" (SSR / Jest / pré-render).
 *   - Compatible phase render React (aucun side-effect autre que storage).
 *   - Breadcrumb Sentry non-bloquant si Sentry disponible.
 *   - Logs DEV-only via console.debug (jamais en production).
 *
 * Ce module ne dépend d'aucun runtime React et peut être appelé n'importe où.
 */

// Import Sentry — l'import lui-même ne lance aucun appel réseau ni init.
// Si Sentry n'est pas initialisé (dev local sans DSN), addBreadcrumb est un noop.
import * as Sentry from "@sentry/react";

const IS_DEV =
  typeof process !== "undefined" &&
  process.env &&
  process.env.NODE_ENV !== "production";

/** Détecte si le `window` est disponible (SSR / build-time / Jest safe). */
function hasWindow() {
  return typeof window !== "undefined";
}

/** Log DEV-only — n'apparaît jamais en production. */
function devLog(...args) {
  if (IS_DEV && typeof console !== "undefined" && console.debug) {
    try {
      console.debug("[safeStorage]", ...args);
    } catch (_) {
      /* noop : console peut être bloqué */
    }
  }
}

/** Breadcrumb Sentry non-bloquant ; protégé par try/catch. */
function reportToSentry(storageType, operation, key, err) {
  try {
    if (typeof Sentry !== "undefined" && Sentry.addBreadcrumb) {
      Sentry.addBreadcrumb({
        category: "storage",
        level: "warning",
        message: `${storageType} ${operation} blocked`,
        data: {
          storageType,
          operation,
          key: typeof key === "string" ? key.slice(0, 80) : null,
          errorName: err && err.name ? err.name : null,
          errorMessage: err && err.message ? err.message.slice(0, 200) : null,
        },
      });
    }
  } catch (_) {
    /* noop : Sentry breadcrumb ne doit jamais crasher l'app */
  }
}

/** Récupère un storage natif (local ou session) de manière safe. */
function getNativeStorage(kind) {
  if (!hasWindow()) return null;
  try {
    // ATTENTION : l'accès `window.localStorage` peut lui-même throw SecurityError
    // sur certains navigateurs avant même getItem. D'où try/catch ici.
    return kind === "session" ? window.sessionStorage : window.localStorage;
  } catch (err) {
    devLog(`window.${kind}Storage access denied`, err && err.message);
    reportToSentry(kind === "session" ? "sessionStorage" : "localStorage", "access", null, err);
    return null;
  }
}

/** Construit une façade safe pour un type de storage donné. */
function buildSafeStorage(kind) {
  const label = kind === "session" ? "sessionStorage" : "localStorage";

  return {
    /**
     * Lit une clé. Retourne la string brute ou null en cas d'absence/erreur.
     */
    get(key) {
      const s = getNativeStorage(kind);
      if (!s) return null;
      try {
        return s.getItem(key);
      } catch (err) {
        devLog(`${label}.get(${key}) failed`, err && err.message);
        reportToSentry(label, "get", key, err);
        return null;
      }
    },

    /**
     * Écrit une string. Retourne true si succès, false sinon.
     * Coerce automatiquement les non-strings via String().
     */
    set(key, value) {
      const s = getNativeStorage(kind);
      if (!s) return false;
      try {
        s.setItem(key, value == null ? "" : String(value));
        return true;
      } catch (err) {
        devLog(`${label}.set(${key}) failed`, err && err.message);
        reportToSentry(label, "set", key, err);
        return false;
      }
    },

    /**
     * Supprime une clé. Toujours noop si storage inaccessible.
     */
    remove(key) {
      const s = getNativeStorage(kind);
      if (!s) return false;
      try {
        s.removeItem(key);
        return true;
      } catch (err) {
        devLog(`${label}.remove(${key}) failed`, err && err.message);
        reportToSentry(label, "remove", key, err);
        return false;
      }
    },

    /**
     * Vide tout le storage. Noop si inaccessible.
     */
    clear() {
      const s = getNativeStorage(kind);
      if (!s) return false;
      try {
        s.clear();
        return true;
      } catch (err) {
        devLog(`${label}.clear() failed`, err && err.message);
        reportToSentry(label, "clear", null, err);
        return false;
      }
    },

    /**
     * Lit une clé et la parse en JSON. Retourne defaultValue si absent, invalide
     * ou erreur. JAMAIS de throw.
     */
    getJSON(key, defaultValue = null) {
      const raw = this.get(key);
      if (raw == null || raw === "") return defaultValue;
      try {
        return JSON.parse(raw);
      } catch (err) {
        devLog(`${label}.getJSON(${key}) parse failed`, err && err.message);
        // Pas de breadcrumb Sentry sur parse error : c'est une donnée corrompue,
        // pas un blocage navigateur, et on ne veut pas polluer Sentry.
        return defaultValue;
      }
    },

    /**
     * Sérialise en JSON et écrit. Retourne true/false.
     */
    setJSON(key, value) {
      let serialized;
      try {
        serialized = JSON.stringify(value);
      } catch (err) {
        devLog(`${label}.setJSON(${key}) stringify failed`, err && err.message);
        return false;
      }
      return this.set(key, serialized);
    },
  };
}

export const safeStorage = buildSafeStorage("local");
export const safeSessionStorage = buildSafeStorage("session");

/** Helper bonus : indique si le storage local est utilisable (utile pour UI conditionnelle). */
export function isLocalStorageAvailable() {
  const s = getNativeStorage("local");
  if (!s) return false;
  try {
    const TEST_KEY = "__ses_safeStorage_probe__";
    s.setItem(TEST_KEY, "1");
    s.removeItem(TEST_KEY);
    return true;
  } catch (_) {
    return false;
  }
}

export default safeStorage;
