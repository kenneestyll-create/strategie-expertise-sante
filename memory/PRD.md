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
- [x] Email unique: contact@strategie-expertise-sante.fr
- [x] Admin UI changement mot de passe + création admin secondaire
- [x] SEO Fundamentals (Title, Meta, OG, Canonical, Sitemap dynamique)
- [x] Favicon transparent SVG/PNG Shield
- [x] SEO /entreprises : contenu texte + FAQ Schema.org FAQPage
- [x] SEO /parrainage : contenu texte + FAQ Schema.org FAQPage (10% parrainage + 15% fidélité)

## SEO Phase 2 — 15 Pages Guides Actives (COMPLET)
### Bloc A — 5 Pages existantes étoffées (800-1200 mots)
1. /guide/refus-mdph-aah-que-faire (MDPH)
2. /guide/taux-ipp-5-pourcent-contester (Indemnisation)
3. /guide/expertise-medicale-defavorable-recours (Expertise)
4. /guide/accident-travail-non-declare-employeur (AT)
5. /guide/refus-maladie-professionnelle-cpam-recours (AT)

### Bloc B — 5 Nouvelles pages SEO
6. /guide/faute-inexcusable-employeur (AT)
7. /guide/inaptitude-travail-droits-recours (Emploi)
8. /guide/rente-accident-travail-calcul-contestation (Indemnisation)
9. /guide/recours-tribunal-judiciaire-pole-social (Indemnisation)
10. /guide/delai-prescription-maladie-professionnelle (AT)

### Bloc C — 5 Pages FAQ transformées en guides
11. /guide/comment-preparer-expertise-medicale (Expertise)
12. /guide/comment-demander-rqth-strategic (MDPH)
13. /guide/comment-faire-reconnaitre-maladie-professionnelle (AT)
14. /guide/maladie-professionnelle-definition-droits (AT)
15. /guide/ptia-definition-droits-strategie (Indemnisation)

### Structure de chaque page
- 6 blocs : contexte, limites, blocages, erreurs, stratégie, orientation
- Réassurance + CTA contextuel (dossier_express ou accompagnement)
- Maillage interne (2-3 liens par page)
- Schema.org FAQPage JSON-LD (2 questions/réponses par page)
- Sitemap dynamique incluant les 15 pages

## En Cours / Non Terminé
- [x] P1 : Configuration Webhook Stripe (whsec_ configuré et vérifié)
- [ ] P2 : Intégration HubSpot CRM (en attente identifiants)

## Backlog
- [ ] P2 : IA Prédictive V2
- [ ] P3 : Module Devis personnalisé

## Credentials Admin
- Admin: admin@accompagn-sante.fr / Admin2024!
- Backup Admin: backup@strategie-expertise-sante.fr / AdminSecours2026!
- Client test: demo@test.com / Password123!
