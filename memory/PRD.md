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

### Éditeur de templates email (Complété - Feb 2026)
- Interface visuelle dans l'onglet "Templates" admin
- CRUD complet (créer, modifier, dupliquer, supprimer)
- Aperçu live du HTML de l'email
- Toggle statut actif/brouillon
- 3 templates par défaut : rassurant, incitatif, urgent
- Composant séparé : `EmailTemplateEditor.jsx`

### Variables dynamiques pour emails (Complété - Feb 2026)
- 5 variables : `{{prenom}}`, `{{nom}}`, `{{completeness}}`, `{{documents_missing}}`, `{{date_inscription}}`
- Barre d'insertion cliquable au-dessus de chaque champ texte
- Coloration syntaxique en mode lecture (badges colorés)
- Aperçu avec résolution automatique des variables
- Backend : `resolve_template_variables()` + endpoint `/api/admin/email-templates/variables`

### Mode test email (Complété - Feb 2026)
- Bouton "Envoyer un test" (icône Send verte) sur chaque template
- Dialog avec : email destinataire, valeurs éditables pour chaque variable
- Avertissement sandbox Resend visible dans le dialog
- Email de test préfixé `[TEST]` + bandeau "EMAIL DE TEST" dans le HTML
- Aucune trace dans les KPIs/tracking
- Endpoint : `POST /api/admin/email-templates/send-test`

## Tâches en attente (bloquées)
- **HubSpot (P2):** En attente du HUBSPOT_PORTAL_ID utilisateur
- **Paiements production (P2):** En attente des clés Stripe/PayPal production
- **Contenu juridique (P3):** En attente du contenu utilisateur pour les pages légales

## Backlog / Améliorations futures
- Refactoring AdminDashboard.jsx (fichier volumineux, ~2700 lignes)
- Intégration complète templates ↔ A/B testing (utiliser les templates créés comme variantes)
- Statistiques d'utilisation des templates par email envoyé

## Fichiers clés
- `/app/frontend/src/pages/AdminDashboard.jsx` — Dashboard admin principal
- `/app/frontend/src/components/EmailTemplateEditor.jsx` — Éditeur de templates + variables + test
- `/app/backend/routes/admin.py` — Endpoints admin
- `/app/backend/utils/email.py` — Logique d'envoi, variables, résolution
- `/app/backend/server.py` — Scheduler, tracking

## Credentials de test
- Admin: `admin@accompagn-sante.fr` / `Admin2024!`
- Client: `demo@test.com` / `Password123!`
