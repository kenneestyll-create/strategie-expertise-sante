# PRD — Stratégie & Expertise Santé

## Énoncé du problème
Application web complète en français pour fournir des conseils sur les maladies professionnelles et les litiges d'assurance. Nommée "Stratégie & Expertise Santé".

## Architecture
- **Frontend:** React + Shadcn/UI + Tailwind CSS + Recharts
- **Backend:** FastAPI + MongoDB
- **Thème:** Noir et Or
- **Intégrations:** Stripe (test), PayPal (test), Claude Sonnet 4.5 (Emergent LLM Key), Resend (sandbox), apscheduler (cron), fpdf2 (PDF)

## Fonctionnalités implémentées

### Core
- Authentification (admin + client), Dashboard client/admin (15 onglets)
- StratégiIA (analyse IA), Scoring qualité, Forum, chatbot, calculatrices

### Système de notifications
- Emails complétion (50/80/100%) + relances inactivité (J+7/14/21)
- Cron hybride, tracking engagement, KPIs, CSV export, alertes, A/B testing

### Éditeur de templates email
- CRUD complet, aperçu live, toggle actif/brouillon, 3 templates défaut

### Variables dynamiques
- 5 variables : {{prenom}}, {{nom}}, {{completeness}}, {{documents_missing}}, {{date_inscription}}
- Barre d'insertion, coloration syntaxique, résolution automatique

### Mode test email + Historique
- Envoi test à une adresse, valeurs éditables, préfixe [TEST]
- Historique dans email_test_history, indicateurs visuels sur cartes

### Campagnes programmées
- Dialog date/heure + cible + A/B optionnel
- Scheduler vérifie toutes les 60s, exécution avec résolution variables
- Tableau de bord avec statuts colorés et actions

### Guides PDF téléchargeables (Bug fix - Feb 2026)
- CORRIGÉ : Les boutons "Télécharger le PDF" affichaient "Ce guide sera bientôt disponible" au lieu de télécharger
- 6 guides PDF générés à la volée via fpdf2 avec branding (header noir/or)
- Endpoint public : `GET /api/resources/pdf/{guide_id}`
- Contenu riche : guide_mp, guide_expertise, guide_mdph, guide_recours, guide_ipp, guide_assurance
- Tracking des téléchargements dans `resource_downloads`
- Fichier : `/app/backend/utils/pdf_guides.py`

## Tâches en attente (bloquées)
- **HubSpot (P2):** En attente du HUBSPOT_PORTAL_ID
- **Paiements production (P2):** En attente des clés Stripe/PayPal production
- **Contenu juridique (P3):** En attente du contenu utilisateur

## Backlog
- Refactoring AdminDashboard.jsx (~2700 lignes)
- Intégration templates ↔ A/B testing (variantes depuis l'éditeur)
- Statistiques d'utilisation par template
- Campagnes récurrentes (hebdomadaire, mensuelle)

## Fichiers clés
- `/app/frontend/src/components/EmailTemplateEditor.jsx` — Éditeur templates
- `/app/frontend/src/components/CampaignsDashboard.jsx` — Tableau campagnes
- `/app/frontend/src/pages/AdminDashboard.jsx` — Dashboard admin
- `/app/frontend/src/pages/ResourcesPage.jsx` — Page ressources
- `/app/backend/routes/admin.py` — Endpoints admin
- `/app/backend/routes/misc.py` — Endpoints publics (PDF, booking, FAQ)
- `/app/backend/utils/email.py` — Logique d'envoi, variables
- `/app/backend/utils/pdf_guides.py` — Génération PDF des guides
- `/app/backend/server.py` — Schedulers

## Credentials de test
- Admin: `admin@accompagn-sante.fr` / `Admin2024!`
- Client: `demo@test.com` / `Password123!`
