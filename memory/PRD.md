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
- Export CSV des données
- Alertes de performance configurables
- Tests A/B des emails

### Éditeur de templates email (Complété)
- Interface visuelle dans l'onglet "Templates" admin
- CRUD complet (créer, modifier, dupliquer, supprimer)
- Aperçu live du HTML de l'email
- Toggle statut actif/brouillon
- 3 templates par défaut : rassurant, incitatif, urgent

### Variables dynamiques pour emails (Complété)
- 5 variables : `{{prenom}}`, `{{nom}}`, `{{completeness}}`, `{{documents_missing}}`, `{{date_inscription}}`
- Barre d'insertion cliquable + coloration syntaxique
- Aperçu avec résolution automatique des variables
- Backend : `resolve_template_variables()` + endpoint `/api/admin/email-templates/variables`

### Mode test email (Complété)
- Bouton "Envoyer un test" sur chaque template
- Dialog avec email destinataire + valeurs éditables des variables
- Email préfixé `[TEST]` + bandeau "EMAIL DE TEST"
- Endpoint : `POST /api/admin/email-templates/send-test`

### Historique des tests email (Complété - Feb 2026)
- Chaque envoi de test enregistré dans `email_test_history` (template_id, email, statut, date, variables utilisées)
- Indicateur visuel sur chaque carte template : "Test il y a Xh → email@..." ou "Jamais testé"
- Section "Derniers tests envoyés" dans le dialog (5 derniers, défilable)
- Points colorés : vert = envoyé, rouge = échec
- Dates relatives en français (à l'instant, il y a Xmin, Xh, Xj)
- Endpoint : `GET /api/admin/email-templates/{id}/test-history`
- Rafraîchissement automatique après chaque envoi

## Tâches en attente (bloquées)
- **HubSpot (P2):** En attente du HUBSPOT_PORTAL_ID utilisateur
- **Paiements production (P2):** En attente des clés Stripe/PayPal production
- **Contenu juridique (P3):** En attente du contenu utilisateur pour les pages légales

## Backlog / Améliorations futures
- Refactoring AdminDashboard.jsx (fichier volumineux, ~2700 lignes)
- Intégration complète templates ↔ A/B testing
- Statistiques d'utilisation des templates par email envoyé

## Fichiers clés
- `/app/frontend/src/components/EmailTemplateEditor.jsx` — Éditeur de templates complet
- `/app/frontend/src/pages/AdminDashboard.jsx` — Dashboard admin principal
- `/app/backend/routes/admin.py` — Endpoints admin
- `/app/backend/utils/email.py` — Logique d'envoi, variables, résolution
- `/app/backend/server.py` — Scheduler, tracking

## Collections MongoDB
- `email_templates` — Templates email (name, label, subject, intro, motivation, cta_text, status)
- `email_test_history` — Historique des tests (template_id, template_name, email, subject, variables_used, status, error, sent_at)

## Credentials de test
- Admin: `admin@accompagn-sante.fr` / `Admin2024!`
- Client: `demo@test.com` / `Password123!`
