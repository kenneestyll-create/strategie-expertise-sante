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

if (SENTRY_DSN && ENVIRONMENT === "production") {
  Sentry.init({
    dsn: SENTRY_DSN,
    environment: ENVIRONMENT,
    release: `production-${BUILD_DATE}`,

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
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
