# PRD — Stratégie & Expertise Santé

## Énoncé du problème
Application web complète en français pour fournir des conseils sur les maladies professionnelles et les litiges d'assurance. Nommée "Stratégie & Expertise Santé".

## Architecture
- **Frontend:** React + Shadcn/UI + Tailwind CSS + Recharts
- **Backend:** FastAPI + MongoDB
- **Thème:** Noir et Or (warm neutral: Manrope + Playfair Display)
- **Intégrations:** Stripe (test), PayPal (test), Claude Sonnet 4.5 (Emergent LLM Key), Resend (sandbox), apscheduler (cron), fpdf2 (PDF)

## Fonctionnalités implémentées

### Core
- Authentification (admin + client), Dashboard client/admin (15 onglets)
- StratégiIA (analyse IA), Scoring qualité, Forum, chatbot, calculatrices

### StratégiIA Phase 1 — Score & Analyse de dossier (Feb 2026)
- **Endpoint:** `GET /api/client/dossier-analysis` (authenticated)
- **Score composite "Solidité du dossier":** 0-100, basé sur complétude (40%), qualité docs (20%), analyses réalisées (15%), progression globale (15%), volume de pièces (10%)
- **Messages dynamiques:** 5 seuils (<30%, 30-50%, 50-70%, 70-85%, >85%)
- **Points de fragilité:** Détection automatique (documents manquants, illisibles, pas de validation, pas d'analyse IA, aucun document)
- **Alertes de risque:** Spécifiques par type de dossier (AT, MP, MDPH, assurance, expertise, faute inexcusable, recours) avec messages détaillés et actions recommandées
- **Compteur d'actions:** "X éléments à traiter pour renforcer votre dossier"
- **Détail du score:** Ventilation interactive avec barres de progression par critère
- **Documents manquants:** Liste avec boutons "Ajouter" redirigeant vers l'espace documents
- **Indicateur navbar:** Score compact (mini-ring + statut coloré), version mobile compacte, clic → scroll, mise à jour temps réel, micro-indicateur "+X%"

### StratégiIA Phase 2 — Feedback & Actions Recommandées (Feb 2026)
- **Actions recommandées (max 3) :** Section "Prochaines actions recommandées" avec CTAs cliquables priorisés
  - Badges de priorité colorés : haute (rouge), moyenne (ambre), faible (vert)
  - Limité à 3 actions maximum pour guider efficacement sans surcharger
  - Chaque action affiche : titre, description, badge d'impact estimé (+X%), badge de priorité
  - Actions contextuelles : upload de document, lancer analyse IA, dossier express
- **Feedback temps réel :** Toast animé après chaque action montrant l'impact concret
  - "Votre score a augmenté de +X%" avec mise à jour immédiate
  - "Cette action renforce significativement votre dossier"
  - Événement `dossier:refresh` déclenché après upload ET suppression

### Score détaillé — Métriques clés toujours visibles (Feb 2026)
- **3 métriques clés** affichées directement dans la carte de score (sans toggle) :
  - Complétude XX% — présence des documents essentiels
  - Qualité XX% — ratio validé/en attente/illisible
  - Cohérence XX% — alignement documents-dossier-analyses
- **Objectif :** Permettre à l'utilisateur de comprendre immédiatement pourquoi il a ce score

### StratégiIA Phase 3 — Prédictif & Premium (Feb 2026)
- **Anticipation des motifs de refus:** Section "Anticipation des motifs de refus" avec badge "Prédictif"
  - Logique prédictive par type de dossier (AT, MP, MDPH, assurance, expertise, recours)
  - Cartes extensibles avec probabilité (Certaine/Élevée/Moyenne), détail et conséquence
  - Conséquences affichées dans un encadré rouge pour maximum de visibilité
- **CTA Premium "Analyse Expert":** Carte dorée avec gradient, couronne, badge Premium
  - 4 features affichées en grille 2 colonnes
  - Bouton doré "Demander une analyse expert"
  - Contexte score : "Votre dossier est à X%. Un expert peut vous aider..."
  - Affiché uniquement si score < 85 ET aucune analyse premium

### Système de notifications
- Emails complétion (50/80/100%) + relances inactivité (J+7/14/21)
- Cron hybride, tracking engagement, KPIs, CSV export, alertes, A/B testing

### Éditeur de templates email
- CRUD complet, aperçu live, toggle actif/brouillon, 3 templates défaut
- Variables dynamiques, mode test, historique, campagnes programmées

### Guides PDF téléchargeables
- 6 guides PDF générés à la volée via fpdf2 avec branding et police DejaVu Sans

## Fichiers clés
- `/app/frontend/src/components/DossierAnalysis.jsx` — Analyse complète (Phase 1+2+3)
- `/app/frontend/src/components/ProgressDashboard.jsx` — Dashboard progression
- `/app/frontend/src/pages/EspaceClientPage.jsx` — Espace client + navbar indicator
- `/app/frontend/src/components/ClientDocuments.jsx` — Upload + refresh dossier
- `/app/frontend/src/components/StrategiIA.jsx` — Modal StrategiIA
- `/app/backend/routes/client.py` — Endpoint dossier-analysis complet
- `/app/backend/routes/strategiia.py` — Endpoints StrategiIA/Dossier Express
- `/app/backend/routes/admin.py` — Endpoints admin
- `/app/backend/utils/pdf_guides.py` — Génération PDF

## Tâches en attente (bloquées)
- **HubSpot (P2):** En attente du HUBSPOT_PORTAL_ID
- **Paiements production (P2):** En attente des clés Stripe/PayPal production
- **Contenu juridique (P3):** En attente du contenu utilisateur

## Backlog
- Refactoring AdminDashboard.jsx (~2700 lignes)
- Refactoring EmailTemplateEditor.jsx (monolithique)
- Intégration templates ↔ A/B testing
- Statistiques d'utilisation par template
- Campagnes récurrentes

## Credentials de test
- Admin: `admin@accompagn-sante.fr` / `Admin2024!`
- Client: `test-analysis@test.com` / `Password123!`
