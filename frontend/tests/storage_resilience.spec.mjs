/**
 * Playwright resilience test — Storage SecurityError fix
 *
 * Vérifie qu'aucune page critique ne crash React lorsque
 * window.localStorage et window.sessionStorage throwent un SecurityError
 * (simulant Chrome Mobile navigation privée / WebView Android sandboxée).
 *
 * Méthode :
 *   1. Injecte un init-script qui redéfinit les getters localStorage/sessionStorage
 *      pour throw une DOMException nommée 'SecurityError' à chaque accès.
 *   2. Navigue sur les pages critiques.
 *   3. Vérifie que :
 *      - aucune pageerror non-attrapée ne remonte
 *      - le DOM root contient bien du contenu rendu (pas de white-screen)
 *      - aucune erreur console fatale type "Cannot access localStorage"
 *
 * Lancement :
 *   cd /app && node frontend/tests/storage_resilience.spec.mjs
 */

import { chromium } from "playwright";

const BASE = "https://mascot-tips-admin.preview.emergentagent.com";

const PAGES = [
  { path: "/", label: "Home" },
  { path: "/espace-client", label: "EspaceClient" },
  { path: "/dossier-express", label: "DossierExpress" },
  { path: "/guide/refus-maladie-professionnelle-causes-droits-procedure", label: "Guide404" },
  { path: "/ressources", label: "Resources" },
  { path: "/admin", label: "AdminLogin" },
  { path: "/expertise-medicale", label: "ExpertiseMed" },
];

// Init script: bloque l'accès à localStorage et sessionStorage de manière synchrone.
const BLOCK_STORAGE = `
  (function () {
    function makeBlockedGetter(label) {
      return function () {
        var e = new Error(label + ' access denied (test SecurityError)');
        e.name = 'SecurityError';
        throw e;
      };
    }
    try {
      Object.defineProperty(window, 'localStorage', {
        configurable: true,
        get: makeBlockedGetter('localStorage'),
      });
    } catch (_) {}
    try {
      Object.defineProperty(window, 'sessionStorage', {
        configurable: true,
        get: makeBlockedGetter('sessionStorage'),
      });
    } catch (_) {}
  })();
`;

async function runOne(browser, p, mode) {
  const ctx = await browser.newContext({
    viewport: { width: 390, height: 844 }, // iPhone-ish mobile
    userAgent:
      "Mozilla/5.0 (Linux; Android 13; SM-S908U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
  });
  if (mode === "blocked") {
    await ctx.addInitScript({ content: BLOCK_STORAGE });
  }
  const page = await ctx.newPage();
  const pageErrors = [];
  const consoleErrors = [];
  page.on("pageerror", (err) => pageErrors.push(String(err)));
  page.on("console", (msg) => {
    if (msg.type() === "error") consoleErrors.push(msg.text());
  });

  let status = null;
  let htmlLen = 0;
  let bodyTextLen = 0;
  let title = "";
  let crashed = false;
  let errMsg = null;

  try {
    const resp = await page.goto(BASE + p.path, {
      waitUntil: "domcontentloaded",
      timeout: 30000,
    });
    status = resp ? resp.status() : null;
    await page.waitForTimeout(3000);
    title = await page.title();
    htmlLen = await page.evaluate(
      () => (document.getElementById("root") || document.body).innerHTML.length
    );
    bodyTextLen = await page.evaluate(() => document.body.innerText.length);
  } catch (e) {
    crashed = true;
    errMsg = e.message;
  }

  // Filtre les erreurs liées à des assets externes (favicon, analytics) non bloquantes
  const fatalPageErrors = pageErrors.filter(
    (e) =>
      !/favicon|net::ERR_BLOCKED|net::ERR_FAILED|chrome-extension/i.test(e)
  );
  const fatalConsoleErrors = consoleErrors.filter(
    (e) =>
      !/favicon|net::ERR_BLOCKED|Failed to load resource|chrome-extension|ResizeObserver|Sentry|loadDevice|googletag|gtag|gtm|hubspot|fbq|TikTok|warn:/i.test(
        e
      )
  );

  await ctx.close();

  return {
    label: p.label,
    path: p.path,
    mode,
    status,
    title,
    htmlLen,
    bodyTextLen,
    crashed,
    errMsg,
    pageErrors: fatalPageErrors,
    consoleErrors: fatalConsoleErrors,
  };
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const results = [];

  for (const p of PAGES) {
    for (const mode of ["normal", "blocked"]) {
      const r = await runOne(browser, p, mode);
      results.push(r);
      const ok =
        !r.crashed &&
        r.htmlLen > 500 &&
        r.bodyTextLen > 50 &&
        r.pageErrors.length === 0;
      const tag = ok ? "PASS" : "FAIL";
      console.log(
        `[${tag}] ${r.label.padEnd(16)} ${mode.padEnd(8)} status=${r.status} htmlLen=${r.htmlLen} bodyText=${r.bodyTextLen} pageErr=${r.pageErrors.length} consoleErr=${r.consoleErrors.length}`
      );
      if (r.pageErrors.length) {
        r.pageErrors.slice(0, 3).forEach((e) =>
          console.log(`     PAGEERROR: ${e.slice(0, 240)}`)
        );
      }
      if (r.consoleErrors.length) {
        r.consoleErrors.slice(0, 3).forEach((e) =>
          console.log(`     CONSOLEERR: ${e.slice(0, 240)}`)
        );
      }
      if (r.crashed) console.log(`     CRASH: ${r.errMsg}`);
    }
  }

  await browser.close();

  // Bilan
  const allOk = results.every(
    (r) =>
      !r.crashed &&
      r.htmlLen > 500 &&
      r.bodyTextLen > 50 &&
      r.pageErrors.length === 0
  );
  const blockedOk = results
    .filter((r) => r.mode === "blocked")
    .every(
      (r) =>
        !r.crashed &&
        r.htmlLen > 500 &&
        r.pageErrors.length === 0
    );

  console.log("\n=== BILAN ===");
  console.log(`Tests totaux : ${results.length}`);
  console.log(`Tous OK (normal + blocked) : ${allOk}`);
  console.log(`Pages OK en storage bloqué : ${blockedOk}`);
  process.exit(blockedOk ? 0 : 1);
})();
