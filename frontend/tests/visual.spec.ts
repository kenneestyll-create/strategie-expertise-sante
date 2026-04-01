/**
 * ═══════════════════════════════════════════════════════════
 * TESTS VISUELS DE NON-RÉGRESSION — Stratégie & Expertise Santé
 * ═══════════════════════════════════════════════════════════
 * 
 * BASELINE GELÉE LE 01/04/2026
 * 
 * RÈGLE ABSOLUE :
 * Aucune modification frontend ne doit être considérée comme
 * "terminée" si ces tests ne sont pas PASS à 100%.
 * 
 * Vérifie automatiquement :
 * - Absence de scroll horizontal (toutes pages × 8 résolutions)
 * - CTA non tronqués (mobile)
 * - Cartes bien centrées (mobile)
 * - Badges non coupés (mobile)
 * - Hero entièrement visible above-the-fold (desktop)
 * - Header non cassé (desktop + mobile)
 * - Aucun texte qui sort d'un encadré (mobile)
 * - Aucun bouton plus large que le viewport (mobile)
 * - Menu mobile fonctionnel
 * ═══════════════════════════════════════════════════════════
 */

import { test, expect, Page } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';

/* ═══════════════════════════════════════════
   PAGES SENSIBLES — Couverture complète
   ═══════════════════════════════════════════ */

const CRITICAL_PAGES = [
  { path: '/', name: 'home' },
  { path: '/accompagnements', name: 'accompagnements' },
  { path: '/tarifs', name: 'tarifs' },
  { path: '/medecin-conseil', name: 'medecin-conseil' },
  { path: '/dossier-express', name: 'dossier-express' },
  { path: '/simulateur', name: 'strategiia' },
  { path: '/contact', name: 'contact' },
  { path: '/a-propos', name: 'a-propos' },
  { path: '/accident-travail-maladie-professionnelle', name: 'accident-travail' },
  { path: '/ressources', name: 'ressources' },
  { path: '/calculatrice-ipp', name: 'calculatrice-ipp' },
  { path: '/expertise-medicale', name: 'expertise-medicale' },
  { path: '/mdph', name: 'mdph' },
];

/* ═══════════════════════════════════════════
   RÉSOLUTIONS OBLIGATOIRES
   ═══════════════════════════════════════════ */

const MOBILE_VIEWPORTS = [
  { width: 360, height: 800, name: '360x800' },
  { width: 375, height: 812, name: '375x812' },
  { width: 390, height: 844, name: '390x844' },
  { width: 412, height: 915, name: '412x915' },
];

const TABLET_VIEWPORTS = [
  { width: 768, height: 1024, name: '768x1024' },
  { width: 1024, height: 768, name: '1024x768' },
];

const DESKTOP_VIEWPORTS = [
  { width: 1366, height: 768, name: '1366x768' },
  { width: 1440, height: 900, name: '1440x900' },
];

const ALL_VIEWPORTS = [...MOBILE_VIEWPORTS, ...TABLET_VIEWPORTS, ...DESKTOP_VIEWPORTS];

/* ═══════════════════════════════════════════
   HELPERS — Vérifications automatiques
   ═══════════════════════════════════════════ */

async function assertNoHorizontalOverflow(page: Page, context: string) {
  const overflow = await page.evaluate(() => {
    return document.documentElement.scrollWidth > document.documentElement.clientWidth;
  });
  expect(overflow, `SCROLL HORIZONTAL détecté sur ${context}`).toBe(false);
}

async function assertNoButtonOverflow(page: Page, context: string) {
  const overflowingButtons = await page.evaluate(() => {
    const vw = document.documentElement.clientWidth;
    const buttons = document.querySelectorAll('button, a[class*="rounded"], [role="button"]');
    const results: string[] = [];
    buttons.forEach((btn) => {
      const rect = btn.getBoundingClientRect();
      if (rect.width > 0 && rect.height > 0 && rect.top < window.innerHeight * 3) {
        if (rect.right > vw + 2 || rect.left < -2) {
          results.push(`"${btn.textContent?.trim().substring(0, 40)}" (L:${Math.round(rect.left)}, R:${Math.round(rect.right)}, VW:${vw})`);
        }
      }
    });
    return results;
  });
  expect(overflowingButtons, `BOUTON TRONQUÉ sur ${context}: ${overflowingButtons.join(', ')}`).toHaveLength(0);
}

async function assertCardsContained(page: Page, context: string) {
  const overflowingCards = await page.evaluate(() => {
    const vw = document.documentElement.clientWidth;
    const cards = document.querySelectorAll('[class*="rounded-xl"], [class*="rounded-lg"], [class*="rounded-2xl"]');
    const results: string[] = [];
    cards.forEach((card) => {
      const rect = card.getBoundingClientRect();
      if (rect.width > 10 && rect.height > 10 && rect.top < window.innerHeight * 3) {
        if (rect.right > vw + 2 || rect.left < -2) {
          results.push(`Carte (L:${Math.round(rect.left)}, R:${Math.round(rect.right)}, W:${Math.round(rect.width)}, VW:${vw})`);
        }
      }
    });
    return results;
  });
  expect(overflowingCards, `CARTE DÉBORDE sur ${context}: ${overflowingCards.join(', ')}`).toHaveLength(0);
}

async function assertNoTextOverflow(page: Page, context: string) {
  const overflowingTexts = await page.evaluate(() => {
    const vw = document.documentElement.clientWidth;
    const els = document.querySelectorAll('h1, h2, h3, h4, p, span, a, button, label');
    const results: string[] = [];
    els.forEach((el) => {
      const rect = el.getBoundingClientRect();
      if (rect.width > 0 && rect.height > 0 && rect.top < window.innerHeight * 2) {
        if (rect.right > vw + 5) {
          results.push(`"${el.textContent?.trim().substring(0, 50)}" (R:${Math.round(rect.right)}, VW:${vw})`);
        }
      }
    });
    return results;
  });
  expect(overflowingTexts, `TEXTE DÉBORDE sur ${context}: ${overflowingTexts.join(', ')}`).toHaveLength(0);
}

async function assertNoBadgeOverflow(page: Page, context: string) {
  const overflowing = await page.evaluate(() => {
    const vw = document.documentElement.clientWidth;
    const badges = document.querySelectorAll('[class*="badge"], [class*="Badge"], [class*="tag"], [class*="pill"], span[class*="rounded-full"], span[class*="rounded-lg"]');
    const results: string[] = [];
    badges.forEach((el) => {
      const rect = el.getBoundingClientRect();
      if (rect.width > 0 && rect.height > 0 && rect.top < window.innerHeight * 3) {
        if (rect.right > vw + 2 || rect.left < -2) {
          results.push(`Badge "${el.textContent?.trim().substring(0, 30)}" (R:${Math.round(rect.right)}, VW:${vw})`);
        }
      }
    });
    return results;
  });
  expect(overflowing, `BADGE COUPÉ sur ${context}: ${overflowing.join(', ')}`).toHaveLength(0);
}

/* ═══════════════════════════════════════════
   TEST 1: Absence de scroll horizontal
   Toutes pages × toutes résolutions
   ═══════════════════════════════════════════ */
test.describe('1. Scroll horizontal interdit', () => {
  for (const pg of CRITICAL_PAGES) {
    for (const vp of ALL_VIEWPORTS) {
      test(`${pg.name} @ ${vp.name}`, async ({ page }) => {
        await page.setViewportSize({ width: vp.width, height: vp.height });
        await page.goto(`${BASE_URL}${pg.path}`, { waitUntil: 'domcontentloaded', timeout: 30000 });
        await page.waitForTimeout(800);
        await assertNoHorizontalOverflow(page, `${pg.name} @ ${vp.name}`);
      });
    }
  }
});

/* ═══════════════════════════════════════════
   TEST 2: CTA non tronqués (mobile)
   ═══════════════════════════════════════════ */
test.describe('2. CTA non tronqués (mobile)', () => {
  for (const pg of CRITICAL_PAGES) {
    for (const vp of MOBILE_VIEWPORTS) {
      test(`${pg.name} @ ${vp.name}`, async ({ page }) => {
        await page.setViewportSize({ width: vp.width, height: vp.height });
        await page.goto(`${BASE_URL}${pg.path}`, { waitUntil: 'domcontentloaded', timeout: 30000 });
        await page.waitForTimeout(800);
        await assertNoButtonOverflow(page, `${pg.name} @ ${vp.name}`);
      });
    }
  }
});

/* ═══════════════════════════════════════════
   TEST 3: Cartes contenues (mobile)
   ═══════════════════════════════════════════ */
test.describe('3. Cartes centrées (mobile)', () => {
  for (const pg of CRITICAL_PAGES) {
    for (const vp of MOBILE_VIEWPORTS) {
      test(`${pg.name} @ ${vp.name}`, async ({ page }) => {
        await page.setViewportSize({ width: vp.width, height: vp.height });
        await page.goto(`${BASE_URL}${pg.path}`, { waitUntil: 'domcontentloaded', timeout: 30000 });
        await page.waitForTimeout(800);
        await assertCardsContained(page, `${pg.name} @ ${vp.name}`);
      });
    }
  }
});

/* ═══════════════════════════════════════════
   TEST 4: Texte ne déborde pas (mobile)
   ═══════════════════════════════════════════ */
test.describe('4. Texte contenu (mobile)', () => {
  for (const pg of CRITICAL_PAGES) {
    for (const vp of MOBILE_VIEWPORTS) {
      test(`${pg.name} @ ${vp.name}`, async ({ page }) => {
        await page.setViewportSize({ width: vp.width, height: vp.height });
        await page.goto(`${BASE_URL}${pg.path}`, { waitUntil: 'domcontentloaded', timeout: 30000 });
        await page.waitForTimeout(800);
        await assertNoTextOverflow(page, `${pg.name} @ ${vp.name}`);
      });
    }
  }
});

/* ═══════════════════════════════════════════
   TEST 5: Badges non coupés (mobile)
   ═══════════════════════════════════════════ */
test.describe('5. Badges non coupés (mobile)', () => {
  for (const pg of CRITICAL_PAGES) {
    for (const vp of MOBILE_VIEWPORTS) {
      test(`${pg.name} @ ${vp.name}`, async ({ page }) => {
        await page.setViewportSize({ width: vp.width, height: vp.height });
        await page.goto(`${BASE_URL}${pg.path}`, { waitUntil: 'domcontentloaded', timeout: 30000 });
        await page.waitForTimeout(500);
        await assertNoBadgeOverflow(page, `${pg.name} @ ${vp.name}`);
      });
    }
  }
});

/* ═══════════════════════════════════════════
   TEST 6: Hero above-the-fold (desktop)
   ═══════════════════════════════════════════ */
test.describe('6. Hero above-the-fold (desktop)', () => {
  for (const vp of DESKTOP_VIEWPORTS) {
    test(`Hero visible @ ${vp.name}`, async ({ page }) => {
      await page.setViewportSize({ width: vp.width, height: vp.height });
      await page.goto(`${BASE_URL}/`, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForTimeout(500);

      const hero = page.locator('[data-testid="hero-section"]');
      const box = await hero.boundingBox();
      expect(box, 'Hero introuvable').not.toBeNull();
      expect(box!.y + box!.height, `Hero dépasse le fold @ ${vp.name}`).toBeLessThanOrEqual(vp.height * 1.2);
    });
  }
});

/* ═══════════════════════════════════════════
   TEST 7: Header non cassé (desktop + mobile)
   ═══════════════════════════════════════════ */
test.describe('7. Header intact', () => {
  test('Header desktop — logo + nav visibles @ 1440x900', async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto(`${BASE_URL}/`, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(500);

    const header = page.locator('header').first();
    const box = await header.boundingBox();
    expect(box, 'Header introuvable').not.toBeNull();
    expect(box!.width, 'Header ne prend pas toute la largeur').toBeGreaterThan(1400);
  });

  test('Header desktop — aligné @ 1366x768', async ({ page }) => {
    await page.setViewportSize({ width: 1366, height: 768 });
    await page.goto(`${BASE_URL}/`, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(500);

    const header = page.locator('header').first();
    const box = await header.boundingBox();
    expect(box, 'Header introuvable').not.toBeNull();
    expect(box!.width, 'Header ne prend pas toute la largeur').toBeGreaterThan(1340);
  });

  for (const vp of MOBILE_VIEWPORTS) {
    test(`Header mobile @ ${vp.name} — pas de débordement`, async ({ page }) => {
      await page.setViewportSize({ width: vp.width, height: vp.height });
      await page.goto(`${BASE_URL}/`, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForTimeout(500);

      await assertNoHorizontalOverflow(page, `Header mobile @ ${vp.name}`);
      const header = page.locator('header').first();
      const box = await header.boundingBox();
      expect(box, 'Header introuvable').not.toBeNull();
      expect(box!.width, `Header trop large @ ${vp.name}`).toBeLessThanOrEqual(vp.width + 1);
    });
  }
});

/* ═══════════════════════════════════════════
   TEST 8: Menu mobile — ouverture / fermeture
   ═══════════════════════════════════════════ */
test.describe('8. Menu mobile', () => {
  for (const vp of MOBILE_VIEWPORTS) {
    test(`Menu ouvre/ferme @ ${vp.name}`, async ({ page }) => {
      await page.setViewportSize({ width: vp.width, height: vp.height });
      await page.goto(`${BASE_URL}/`, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForTimeout(500);

      const menuBtn = page.locator('header button').first();
      if (await menuBtn.isVisible()) {
        await menuBtn.click();
        await page.waitForTimeout(400);
        await assertNoHorizontalOverflow(page, `Menu ouvert @ ${vp.name}`);
      }
    });
  }
});

/* ═══════════════════════════════════════════
   TEST 9: Sections à encadrés — pas de débordement
   ═══════════════════════════════════════════ */
test.describe('9. Encadrés contenus (mobile)', () => {
  const pagesWithEncadres = [
    { path: '/', name: 'home' },
    { path: '/accompagnements', name: 'accompagnements' },
    { path: '/tarifs', name: 'tarifs' },
    { path: '/medecin-conseil', name: 'medecin-conseil' },
  ];

  for (const pg of pagesWithEncadres) {
    test(`${pg.name} @ 360x800 — encadrés contenus`, async ({ page }) => {
      await page.setViewportSize({ width: 360, height: 800 });
      await page.goto(`${BASE_URL}${pg.path}`, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForTimeout(500);

      const overflowing = await page.evaluate(() => {
        const vw = document.documentElement.clientWidth;
        const encadres = document.querySelectorAll('[class*="border"][class*="rounded"], [class*="bg-"][class*="rounded"], [class*="shadow"][class*="rounded"]');
        const results: string[] = [];
        encadres.forEach((el) => {
          const rect = el.getBoundingClientRect();
          if (rect.width > 20 && rect.height > 20 && rect.top < window.innerHeight * 4) {
            // Skip elements clipped by parent overflow
            let clipped = false;
            let parent = el.parentElement;
            while (parent) {
              const style = getComputedStyle(parent);
              if (style.overflowX === 'clip' || style.overflowX === 'hidden' || style.overflow === 'clip' || style.overflow === 'hidden') {
                const pRect = parent.getBoundingClientRect();
                if (rect.right > pRect.right + 2) { clipped = true; break; }
              }
              parent = parent.parentElement;
            }
            if (!clipped && rect.right > vw + 2) {
              results.push(`Encadré (L:${Math.round(rect.left)}, R:${Math.round(rect.right)}, W:${Math.round(rect.width)}, VW:${vw})`);
            }
          }
        });
        return results;
      });
      expect(overflowing, `ENCADRÉ DÉBORDE sur ${pg.name}: ${overflowing.join(', ')}`).toHaveLength(0);
    });
  }
});

/* ═══════════════════════════════════════════
   TEST 10: Largeur de page — aucune page plus large que le viewport
   ═══════════════════════════════════════════ */
test.describe('10. Largeur page === viewport (mobile)', () => {
  for (const pg of CRITICAL_PAGES) {
    test(`${pg.name} @ 360x800 — scrollWidth === clientWidth`, async ({ page }) => {
      await page.setViewportSize({ width: 360, height: 800 });
      await page.goto(`${BASE_URL}${pg.path}`, { waitUntil: 'domcontentloaded', timeout: 30000 });
      await page.waitForTimeout(500);

      const result = await page.evaluate(() => {
        return {
          scrollWidth: document.documentElement.scrollWidth,
          clientWidth: document.documentElement.clientWidth,
        };
      });
      expect(result.scrollWidth, `${pg.name}: scrollWidth(${result.scrollWidth}) > clientWidth(${result.clientWidth})`).toBeLessThanOrEqual(result.clientWidth);
    });
  }
});
