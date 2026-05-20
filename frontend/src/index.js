import React from "react";
import ReactDOM from "react-dom/client";
import * as Sentry from "@sentry/react";
import "@/index.css";
import App from "@/App";

// ===== Sentry — Error monitoring only (no Replay, no Performance, no Analytics) =====
// Activated ONLY when REACT_APP_SENTRY_DSN is set AND environment is production.
// Tant que la variable est vide, Sentry reste totalement inactif (aucun appel réseau, aucun overhead).
const SENTRY_DSN = process.env.REACT_APP_SENTRY_DSN;
const ENVIRONMENT = process.env.REACT_APP_ENVIRONMENT || "production";
const BUILD_DATE =
  process.env.REACT_APP_BUILD_DATE || new Date().toISOString().slice(0, 10);

// ===== DIAGNOSTIC LOG (temporary, remove once Sentry confirmed working) =====
// eslint-disable-next-line no-console
console.log("[SENTRY INIT CHECK]", {
  dsn_present: !!SENTRY_DSN,
  dsn_prefix: SENTRY_DSN ? SENTRY_DSN.slice(0, 35) + "..." : null,
  env: ENVIRONMENT,
  will_init: !!(SENTRY_DSN && ENVIRONMENT === "production"),
});

if (SENTRY_DSN && ENVIRONMENT === "production") {
  Sentry.init({
    dsn: SENTRY_DSN,
    environment: ENVIRONMENT,
    release: `production-${BUILD_DATE}`,

    // Explicit integrations : ensure global error + unhandled rejection capture.
    integrations: [
      Sentry.browserApiErrorsIntegration(),
      Sentry.globalHandlersIntegration({ onerror: true, onunhandledrejection: true }),
    ],

    // Strict scope : runtime errors only.
    tracesSampleRate: 0,
    replaysSessionSampleRate: 0,
    replaysOnErrorSampleRate: 0,
    profilesSampleRate: 0,

    // Anti false-positives.
    ignoreErrors: [
      "ResizeObserver loop limit exceeded",
      "ResizeObserver loop completed with undelivered notifications",
      "ChunkLoadError",
      "Loading chunk",
      "Loading CSS chunk",
      "NetworkError",
      "Network request failed",
      "Failed to fetch",
      "Non-Error promise rejection captured",
      "TypeError: cancelled",
      "AbortError",
    ],
    denyUrls: [
      /chrome-extension:\/\//,
      /moz-extension:\/\//,
      /safari-extension:\/\//,
      /^https?:\/\/localhost/,
      /^https?:\/\/.*\.preview\.emergentagent\.com/,
      /^https?:\/\/.*\.preview\.emergent\.sh/,
    ],

    // Belt-and-suspenders : even if all else fails, never send from preview/dev.
    beforeSend(event) {
      const host = window.location.hostname || "";
      if (host.includes("preview.emergentagent.com")) return null;
      if (host.includes("preview.emergent.sh")) return null;
      if (host === "localhost" || host === "127.0.0.1") return null;
      return event;
    },
  });

  // ===== DIAGNOSTIC : log every event going to Sentry (remove once confirmed) =====
  Sentry.addEventProcessor((event) => {
    // eslint-disable-next-line no-console
    console.log("[SENTRY EVENT CAPTURED]", {
      type: event.type || "error",
      message: event.message,
      exception: event.exception?.values?.[0]?.value,
      event_id: event.event_id,
    });
    return event;
  });

  // Expose for manual testing : window.__sentryTest() in console
  if (typeof window !== "undefined") {
    window.__sentryTest = () => {
      Sentry.captureException(new Error("AGENT TEST SENTRY FINAL"));
      return Sentry.flush(2000);
    };
  }
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
