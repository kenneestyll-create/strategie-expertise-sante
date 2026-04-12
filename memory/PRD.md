# Stratégie & Expertise Santé (S.E.S) — PRD

## Problème Original
Plateforme de conseil en santé offrant des services payants. Paiements sécurisés, conformité légale stricte (CGV/RGPD), stockage S3, UX fluide.

## Architecture
- Frontend: React (Shadcn UI) | Backend: FastAPI + MongoDB
- Paiements: Stripe (LIVE) + PayPal (LIVE)
- Stockage: AWS S3 (eu-west-3) | Email: Resend | IA: Claude Sonnet 4.5 | Recherche: Algolia
- Hébergement: Vercel

## Fonctionnalités Implémentées
- [x] Stripe + PayPal Live (modal simplifiée 2 boutons)
- [x] Conformité légale CGV/RGPD/L.221-28 + consent-log
- [x] AWS S3 + Admin metrics + alertes seuil
- [x] Rapport KPI hebdomadaire (Resend + APScheduler)
- [x] Scanner documents (Web Worker)
- [x] Mentions Légales complètes (hébergeur Vercel renseigné)
- [x] Fidélité (-15%) corrigée : compteur uniquement après webhook paiement
- [x] Dashboard Admin Conseils Mascotte (CRUD + analytics)
- [x] Email unique: contact@strategie-expertise-sante.fr
- [x] Purge transactions (tests / tout) avec double confirmation
- [x] Comptabilité multi-périodes (jour/semaine/mois/trimestre/semestre/année)

## Corrections Récentes (11-12 avril 2026)
- [x] PayPal Live configuré
- [x] Bug overlay PostHog/PayPal corrigé (webpack overlay disabled)
- [x] Clé Stripe: load_dotenv(override=True)
- [x] BUG CRITIQUE fidélité: orders_count seulement après webhook
- [x] Modal paiement simplifiée (2 boutons alignés)
- [x] IDs frontend sans accents (preparation_expertise)
- [x] Email définitif implanté partout
- [x] Hébergeur Vercel dans mentions légales
- [x] Purge + Comptabilité dans Admin Analytique

## En Cours / Non Terminé
- [ ] P1 : Configuration URL Webhook Stripe (en attente whsec_ utilisateur)
- [ ] P2 : Intégration HubSpot CRM (en attente identifiants)

## Backlog
- [ ] P2 : IA Prédictive V2
- [ ] P3 : Module Devis personnalisé

## Credentials Admin
- Admin: admin@accompagn-sante.fr / Admin2024!
- Client test: demo@test.com / Password123!
