# PRD — Stratégie & Expertise Santé

## Énoncé du problème
Application web complète en français pour fournir des conseils sur les maladies professionnelles et les litiges d'assurance. Nommée "Stratégie & Expertise Santé".

## Architecture
- **Frontend:** React + Shadcn/UI + Tailwind CSS + Recharts
- **Backend:** FastAPI + MongoDB
- **Thème:** Noir et Or
- **Intégrations:** Stripe (test), PayPal (test), Claude Sonnet 4.5 (Emergent LLM Key), Resend (sandbox), apscheduler (cron)

## Fonctionnalités implémentées

### Core
- Authentification (admin + client)
- Dashboard client avec progression du dossier
- Dashboard admin avec 15 onglets
- StratégiIA (analyse IA des dossiers)
- Scoring qualité des dossiers
- Forum, chatbot, calculatrice

### Système de notifications
- Emails automatiques de complétion (50%, 80%, 100%)
- Relances d'inactivité (J+7, J+14, J+21)
- Cron job hybride (automatique + manuel)
- Tracking d'engagement (ouvertures, clics)
- Dashboard KPIs d'engagement
- Export CSV, alertes de performance, tests A/B

### Éditeur de templates email
- Interface visuelle CRUD dans l'onglet "Templates" admin
- Aperçu live HTML, toggle actif/brouillon
- 3 templates par défaut : rassurant, incitatif, urgent

### Variables dynamiques
- 5 variables : `{{prenom}}`, `{{nom}}`, `{{completeness}}`, `{{documents_missing}}`, `{{date_inscription}}`
- Barre d'insertion cliquable + coloration syntaxique
- Résolution automatique au preview et à l'envoi

### Mode test email
- Bouton "Envoyer un test" avec dialog, email préfixé [TEST]
- Valeurs éditables des variables, avertissement sandbox

### Historique des tests
- Enregistrement de chaque test dans `email_test_history`
- Indicateurs visuels sur chaque carte + section historique dans le dialog

### Campagnes programmées (Complété - Feb 2026)
- Bouton "Programmer" (icône calendrier violet) sur chaque template
- Dialog avec sélecteur date/heure, cible (inactifs/tous), test A/B optionnel
- Message informatif sur le fonctionnement
- Tableau de bord des campagnes en bas de l'onglet Templates
- Statuts visuels : Programmé (jaune), En cours (bleu), Envoyé (vert), Annulé (gris), Échoué (rouge)
- Actions : annuler (campagnes programmées), supprimer (terminées)
- Backend : scheduler vérifie toutes les 60s les campagnes dues
- Exécution : résolution des variables par client, tracking KPI, intégration A/B
- Endpoints : `POST /api/admin/campaigns/schedule`, `GET /api/admin/campaigns`, `PUT /api/admin/campaigns/{id}/cancel`, `DELETE /api/admin/campaigns/{id}`
- Composant séparé : `CampaignsDashboard.jsx`

## Tâches en attente (bloquées)
- **HubSpot (P2):** En attente du HUBSPOT_PORTAL_ID
- **Paiements production (P2):** En attente des clés Stripe/PayPal production
- **Contenu juridique (P3):** En attente du contenu utilisateur

## Backlog / Améliorations futures
- Refactoring AdminDashboard.jsx (~2700 lignes)
- Intégration complète templates ↔ A/B testing (variantes depuis l'éditeur)
- Statistiques d'utilisation par template

## Fichiers clés
- `/app/frontend/src/components/EmailTemplateEditor.jsx` — Éditeur complet
- `/app/frontend/src/components/CampaignsDashboard.jsx` — Tableau campagnes
- `/app/frontend/src/pages/AdminDashboard.jsx` — Dashboard admin
- `/app/backend/routes/admin.py` — Endpoints admin
- `/app/backend/utils/email.py` — Logique d'envoi, variables
- `/app/backend/server.py` — Schedulers (cron + campagnes)

## Collections MongoDB
- `email_templates` — Templates email
- `email_test_history` — Historique des tests
- `scheduled_campaigns` — Campagnes programmées
- `inactivity_reminders` — Relances d'inactivité
- `ab_tests` — Tests A/B

## Credentials de test
- Admin: `admin@accompagn-sante.fr` / `Admin2024!`
- Client: `demo@test.com` / `Password123!`
