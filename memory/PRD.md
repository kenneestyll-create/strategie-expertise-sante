# Stratégie & Expertise Santé (S.E.S) — PRD

## Problème Original
Plateforme de conseil en santé offrant des services payants (consultations, analyses de dossiers, accompagnement MDPH, alertes urgentes). Nécessite paiements sécurisés, conformité légale stricte (CGV/RGPD), stockage S3 persistant, et UX fluide.

## Architecture
- **Frontend**: React (Shadcn UI)
- **Backend**: FastAPI + MongoDB
- **Paiements**: Stripe (LIVE) + PayPal (LIVE)
- **Stockage**: AWS S3 (eu-west-3)
- **Email**: Resend
- **IA**: Claude Sonnet 4.5 (Emergent Key)
- **Recherche**: Algolia

## Fonctionnalités Implémentées
- [x] Stripe Checkout LIVE (tous forfaits + alertes urgentes)
- [x] PayPal LIVE (configuré le 2026-02-XX)
- [x] Conformité légale : CGV, RGPD, cases à cocher obligatoires, consent-log
- [x] AWS S3 : upload, pre-signed URLs, métriques Admin, alertes seuil
- [x] Rapport KPI hebdomadaire automatisé (Resend + APScheduler)
- [x] Scanner de documents (OffscreenCanvas Web Worker)
- [x] Mentions Légales complètes (CGV/CGU/RGPD tabs)
- [x] Système de parrainage et fidélité
- [x] Dashboard Admin (S3 metrics, config email, alertes)

## En Cours / Non Terminé
- [x] P1 : Correction TTS Mascotte Straté (voix anglaise au lieu de française) — RÉSOLU
- [x] Bug overlay PostHog/PayPal corrigé (filtre erreurs tiers dans index.html)
- [ ] P1 : Dashboard Admin gestion conseils Mascotte (CRUD, planification)
- [ ] P1 : Configuration URL Webhook Stripe (côté Dashboard Stripe utilisateur)
- [ ] P2 : Intégration HubSpot CRM (en attente identifiants)

## Backlog
- [ ] P2 : IA Prédictive V2
- [ ] P3 : Module Devis personnalisé

## Schéma DB Clé
- `consent_log`: email, service, cgv_accepted, retractation_waived, cgv_version, ip_address, created_at
- `documents`: filename, s3_key, size, source, uploaded_at
- `bookings`: call_type, date, time, status, payment_intent_id
- `conseils_strate` (PENDING): text, category, active, startDate, endDate, priority
- `payment_transactions`: session_id, package_id, amount, currency, email, status, payment_status

## Credentials Admin
- Admin: admin@accompagn-sante.fr / Admin2024!
- Client test: demo@test.com / Password123!
