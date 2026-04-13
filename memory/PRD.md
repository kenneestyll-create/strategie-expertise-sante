# Stratégie & Expertise Santé (S.E.S) — PRD

## Problème Original
Plateforme de conseil en santé : paiements sécurisés, conformité légale, stockage S3, UX fluide, SEO conversion.

## Architecture
- Frontend: React (Shadcn UI) | Backend: FastAPI + MongoDB
- Paiements: Stripe (LIVE) + PayPal (LIVE) | Stockage: AWS S3
- Email: Resend | IA: Claude Sonnet 4.5 | Recherche: Algolia | Hébergement: Vercel

## Fonctionnalités Implémentées
- [x] Stripe + PayPal Live sur TOUS les paiements (Tarifs, Agenda, Questions urgentes)
- [x] Conformité légale CGV/RGPD/L.221-28 + consent-log
- [x] AWS S3 + Admin metrics + alertes seuil
- [x] Rapport KPI hebdomadaire (Resend + APScheduler)
- [x] Scanner documents (Web Worker)
- [x] Mentions Légales (hébergeur Vercel, email définitif)
- [x] Fidélité corrigée : compteur uniquement après webhook paiement confirmé
- [x] Dashboard Admin Conseils Mascotte (CRUD + analytics)
- [x] Purge transactions (tests/tout) avec double confirmation
- [x] Comptabilité multi-périodes (jour/semaine/mois/trimestre/semestre/année)
- [x] Exit Intent Popup (mouseleave + visibilitychange)
- [x] Pages SEO Phase 1 : 5 guides /guide/:slug + hub /guides-pratiques + sitemap
- [x] Email unique: contact@strategie-expertise-sante.fr

## SEO Phase 1 — Pages actives
1. /guide/refus-mdph-aah-que-faire (MDPH)
2. /guide/taux-ipp-5-pourcent-contester (Indemnisation)
3. /guide/expertise-medicale-defavorable-recours (Expertise)
4. /guide/accident-travail-non-declare-employeur (AT)
5. /guide/refus-maladie-professionnelle-cpam-recours (AT)
Dashboard SEO et tracking avancé : codés mais NON activés (Phase 2)

## En Cours / Non Terminé
- [ ] P1 : Configuration URL Webhook Stripe (en attente whsec_)
- [ ] P2 : Intégration HubSpot CRM (en attente identifiants)

## Backlog
- [ ] P2 : IA Prédictive V2
- [ ] P3 : Module Devis personnalisé
- [ ] SEO Phase 2 : activation dashboard + scaling si résultats

## Credentials Admin
- Admin: admin@accompagn-sante.fr / Admin2024!
- Client test: demo@test.com / Password123!
