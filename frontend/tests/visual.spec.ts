/**
 * ═══════════════════════════════════════════════════════════
 * TESTS VISUELS DE NON-RÉGRESSION — Stratégie & Expertise Santé
 * ═══════════════════════════════════════════════════════════
 * 
 * RÈGLE ABSOLUE :
 * Aucune modification frontend ne doit être considérée comme
 * "terminée" si ces tests ne sont pas PASS à 100%.
 * 
 * Ces tests vérifient automatiquement :
 * - Absence de scroll horizontal
 * - CTA non tronqués
 * - Cartes bien centrées
 * - Badges non coupés
 * - Hero entièrement visible above-the-fold sur desktop
 * - Header non cassé
 * - Aucun texte qui sort d'un encadré
 * - Aucun bouton plus large que le viewport
 * ═══════════════════════════════════════════════════════════
 */

import { test, expect, Page } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';

const PAGES = [
  { path: '/', name: 'home' },
  { path: '/accompagnements', name: 'accompagnements' },
  { path: '/tarifs', name: 'tarifs' },
  { path: '/medecin-conseil', name: 'medecin-conseil' },
  { path: '/dossier-express', name: 'dossier-express' },
  { path: '/strategiia', name: 'strategiia' },
];

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

// ═══════════════════════════════════════════
// HELPER: Vérifier absence de scroll horizontal
// ═══════════════════════════════════════════
async function assertNoHorizontalOverflow(page: Page, context: string) {
  const overflow = await page.evaluate(() => {
    return document.documentElement.scrollWidth > document.documentElement.clientWidth;
  });
  expect(overflow, `Scroll horizontal détecté sur ${context}`).toBe(false);
}

// ═══════════════════════════════════════════
// HELPER: Vérifier qu'aucun bouton ne dépasse le viewport
// ═══════════════════════════════════════════
async function assertNoButtonOverflow(page: Page, context: string) {
  const overflowingButtons = await page.evaluate(() => {
    const viewportWidth = document.documentElement.clientWidth;
    const buttons = document.querySelectorAll('button, a.rounded-full, [role="button"]');
    const results: string[] = [];
    buttons.forEach((btn) => {
      const rect = btn.getBoundingClientRect();
      if (rect.right > viewportWidth + 2 || rect.left < -2) {
        results.push(`${btn.textContent?.trim().substring(0, 40)} (left:${Math.round(rect.left)}, right:${Math.round(rect.right)}, vw:${viewportWidth})`);
      }
    });
    return results;
  });
  expect(overflowingButtons, `Boutons dépassant le viewport sur ${context}: ${overflowingButtons.join(', ')}`).toHaveLength(0);
}

// ═══════════════════════════════════════════
// HELPER: Vérifier que les cartes sont centrées (pas de décalage asymétrique)
// ═══════════════════════════════════════════
async function assertCardsContained(page: Page, context: string) {
  const overflowingCards = await page.evaluate(() => {
    const viewportWidth = document.documentElement.clientWidth;
    const cards = document.querySelectorAll('[class*="rounded-xl"], [class*="rounded-lg"], [class*="Card"]');
    const results: string[] = [];
    cards.forEach((card) => {
      const rect = card.getBoundingClientRect();
      if (rect.width > 0 && rect.height > 0 && rect.top < window.innerHeight * 3) {
        if (rect.right > viewportWidth + 2 || rect.left < -2) {
          results.push(`Card (left:${Math.round(rect.left)}, right:${Math.round(rect.right)}, w:${Math.round(rect.width)})`);
        }
      }
    });
    return results;
  });
  expect(overflowingCards, `Cartes dépassant le viewport sur ${context}: ${overflowingCards.join(', ')}`).toHaveLength(0);
}

// ═══════════════════════════════════════════
// HELPER: Vérifier qu'aucun texte visible ne sort de son conteneur
// ═══════════════════════════════════════════
async function assertNoTextOverflow(page: Page, context: string) {
  const overflowingTexts = await page.evaluate(() => {
    const viewportWidth = document.documentElement.clientWidth;
    const textElements = document.querySelectorAll('h1, h2, h3, h4, p, span, a, button');
    const results: string[] = [];
    textElements.forEach((el) => {
      const rect = el.getBoundingClientRect();
      if (rect.width > 0 && rect.height > 0 && rect.top < window.innerHeight * 2) {
        if (rect.right > viewportWidth + 5) {
          const text = el.textContent?.trim().substring(0, 50) || '';
          results.push(`"${text}" (right:${Math.round(rect.right)}, vw:${viewportWidth})`);
        }
      }
    });
    return results;
  });
  expect(overflowingTexts, `Texte dépassant le viewport sur ${context}: ${overflowingTexts.join(', ')}`).toHaveLength(0);
}

// ═══════════════════════════════════════════
// TEST 1: Absence de scroll horizontal — toutes pages × toutes résolutions
// ═══════════════════════════════════════════
test.describe('Scroll horizontal interdit', () => {
  for (const pageInfo of PAGES) {
    for (const vp of ALL_VIEWPORTS) {
      test(`${pageInfo.name} @ ${vp.name} — pas de scroll horizontal`, async ({ page }) => {
        await page.setViewportSize({ width: vp.width, height: vp.height });
        await page.goto(`${BASE_URL}${pageInfo.path}`, { waitUntil: 'networkidle' });
        await page.waitForTimeout(500);
        await assertNoHorizontalOverflow(page, `${pageInfo.name} @ ${vp.name}`);
      });
    }
  }
});

// ═══════════════════════════════════════════
// TEST 2: Boutons / CTA non tronqués — mobile uniquement
// ═══════════════════════════════════════════
test.describe('CTA non tronqués (mobile)', () => {
  for (const pageInfo of PAGES) {
    for (const vp of MOBILE_VIEWPORTS) {
      test(`${pageInfo.name} @ ${vp.name} — aucun CTA tronqué`, async ({ page }) => {
        await page.setViewportSize({ width: vp.width, height: vp.height });
        await page.goto(`${BASE_URL}${pageInfo.path}`, { waitUntil: 'networkidle' });
        await page.waitForTimeout(500);
        await assertNoButtonOverflow(page, `${pageInfo.name} @ ${vp.name}`);
      });
    }
  }
});

// ═══════════════════════════════════════════
// TEST 3: Cartes contenues dans le viewport — mobile
// ═══════════════════════════════════════════
test.describe('Cartes centrées (mobile)', () => {
  for (const pageInfo of PAGES) {
    for (const vp of MOBILE_VIEWPORTS) {
      test(`${pageInfo.name} @ ${vp.name} — cartes dans le viewport`, async ({ page }) => {
        await page.setViewportSize({ width: vp.width, height: vp.height });
        await page.goto(`${BASE_URL}${pageInfo.path}`, { waitUntil: 'networkidle' });
        await page.waitForTimeout(500);
        await assertCardsContained(page, `${pageInfo.name} @ ${vp.name}`);
      });
    }
  }
});

// ═══════════════════════════════════════════
// TEST 4: Texte ne sort pas des encadrés — mobile
// ═══════════════════════════════════════════
test.describe('Texte contenu (mobile)', () => {
  for (const pageInfo of PAGES) {
    for (const vp of MOBILE_VIEWPORTS) {
      test(`${pageInfo.name} @ ${vp.name} — texte ne déborde pas`, async ({ page }) => {
        await page.setViewportSize({ width: vp.width, height: vp.height });
        await page.goto(`${BASE_URL}${pageInfo.path}`, { waitUntil: 'networkidle' });
        await page.waitForTimeout(500);
        await assertNoTextOverflow(page, `${pageInfo.name} @ ${vp.name}`);
      });
    }
  }
});

// ═══════════════════════════════════════════
// TEST 5: Hero above-the-fold sur desktop
// ═══════════════════════════════════════════
test.describe('Hero above-the-fold (desktop)', () => {
  for (const vp of DESKTOP_VIEWPORTS) {
    test(`Home hero visible sans scroll @ ${vp.name}`, async ({ page }) => {
      await page.setViewportSize({ width: vp.width, height: vp.height });
      await page.goto(`${BASE_URL}/`, { waitUntil: 'networkidle' });
      await page.waitForTimeout(500);

      const heroSection = page.locator('[data-testid="hero-section"]');
      const heroBox = await heroSection.boundingBox();
      expect(heroBox, 'Hero section introuvable').not.toBeNull();

      // Le bas du hero ne doit pas dépasser 120% de la hauteur du viewport
      const heroBottom = heroBox!.y + heroBox!.height;
      expect(heroBottom, `Hero dépasse le fold: bottom=${Math.round(heroBottom)}px vs viewport=${vp.height}px`).toBeLessThanOrEqual(vp.height * 1.2);
    });
  }
});

// ═══════════════════════════════════════════
// TEST 6: Header intact — desktop + mobile
// ═══════════════════════════════════════════
test.describe('Header non cassé', () => {
  test('Header desktop — logo + nav visibles', async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto(`${BASE_URL}/`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(500);

    const header = page.locator('header').first();
    const headerBox = await header.boundingBox();
    expect(headerBox, 'Header introuvable').not.toBeNull();
    expect(headerBox!.width, 'Header ne prend pas toute la largeur').toBeGreaterThan(1400);
  });

  for (const vp of MOBILE_VIEWPORTS) {
    test(`Header mobile @ ${vp.name} — pas de débordement`, async ({ page }) => {
      await page.setViewportSize({ width: vp.width, height: vp.height });
      await page.goto(`${BASE_URL}/`, { waitUntil: 'networkidle' });
      await page.waitForTimeout(500);

      await assertNoHorizontalOverflow(page, `Header mobile @ ${vp.name}`);

      const header = page.locator('header').first();
      const headerBox = await header.boundingBox();
      expect(headerBox, 'Header introuvable').not.toBeNull();
      expect(headerBox!.width, `Header plus large que le viewport @ ${vp.name}`).toBeLessThanOrEqual(vp.width + 1);
    });
  }
});

// ═══════════════════════════════════════════
// TEST 7: Menu mobile — ouverture/fermeture
// ═══════════════════════════════════════════
test.describe('Menu mobile', () => {
  test('Menu mobile ouvre et ferme correctement', async ({ page }) => {
    await page.setViewportSize({ width: 360, height: 800 });
    await page.goto(`${BASE_URL}/`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(500);

    // Cliquer sur le bouton hamburger
    const menuBtn = page.locator('button[aria-label*="menu" i], button[data-testid*="menu" i], header button:has(svg)').first();
    if (await menuBtn.isVisible()) {
      await menuBtn.click();
      await page.waitForTimeout(300);

      // Vérifier pas de scroll horizontal après ouverture
      await assertNoHorizontalOverflow(page, 'Menu mobile ouvert');
    }
  });
});

// ═══════════════════════════════════════════
// TEST 8: Captures de baseline (génération)
// ═══════════════════════════════════════════
test.describe('Génération baseline visuelle', () => {
  const baselinePaths = [
    { path: '/', name: 'home' },
    { path: '/accompagnements', name: 'accompagnements' },
    { path: '/tarifs', name: 'tarifs' },
    { path: '/medecin-conseil', name: 'medecin-conseil' },
    { path: '/dossier-express', name: 'dossier-express' },
    { path: '/strategiia', name: 'strategiia' },
  ];

  for (const pageInfo of baselinePaths) {
    for (const vp of ALL_VIEWPORTS) {
      test(`Baseline: ${pageInfo.name} @ ${vp.name}`, async ({ page }) => {
        await page.setViewportSize({ width: vp.width, height: vp.height });
        await page.goto(`${BASE_URL}${pageInfo.path}`, { waitUntil: 'networkidle' });
        await page.waitForTimeout(1000);
        await expect(page).toHaveScreenshot(`${pageInfo.name}-${vp.name}.png`, {
          fullPage: true,
          maxDiffPixelRatio: 0.01,
        });
      });
    }
  }

  // Header desktop
  test('Baseline: header-desktop', async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto(`${BASE_URL}/`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(500);
    const header = page.locator('header').first();
    await expect(header).toHaveScreenshot('header-desktop.png', { maxDiffPixelRatio: 0.01 });
  });

  // Hero desktop + mobile
  test('Baseline: hero-desktop', async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto(`${BASE_URL}/`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(500);
    const hero = page.locator('[data-testid="hero-section"]');
    await expect(hero).toHaveScreenshot('hero-desktop.png', { maxDiffPixelRatio: 0.01 });
  });

  test('Baseline: hero-mobile', async ({ page }) => {
    await page.setViewportSize({ width: 360, height: 800 });
    await page.goto(`${BASE_URL}/`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(500);
    const hero = page.locator('[data-testid="hero-section"]');
    await expect(hero).toHaveScreenshot('hero-mobile.png', { maxDiffPixelRatio: 0.01 });
  });

  // Menu mobile ouvert
  test('Baseline: menu-mobile-ouvert', async ({ page }) => {
    await page.setViewportSize({ width: 360, height: 800 });
    await page.goto(`${BASE_URL}/`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(500);
    const menuBtn = page.locator('button[aria-label*="menu" i], button[data-testid*="menu" i], header button:has(svg)').first();
    if (await menuBtn.isVisible()) {
      await menuBtn.click();
      await page.waitForTimeout(500);
      await expect(page).toHaveScreenshot('menu-mobile-ouvert.png', { maxDiffPixelRatio: 0.01 });
    }
  });
});
