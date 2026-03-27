# PRD — Stratégie & Expertise Santé (S.E.S)

## Vision
Plateforme premium de conseil en maladies professionnelles, avec scanner de documents, analyse IA (StratégiIA + Dossier Express IA), système de paiement et dashboard Admin complet.

## Personas
- **Client** : Salarié victime de maladie professionnelle, cherche aide stratégique.
- **Admin/Expert** : Gère les dossiers, relecture experte, envoi de rapports finalisés.

## Architecture
- **Frontend** : React + Shadcn/UI + Tailwind CSS
- **Backend** : FastAPI + MongoDB + Emergent Object Storage
- **IA** : Anthropic Claude Sonnet 4.5 (via Emergent LLM Key)
- **PDF** : fpdf2 (backend) + jsPDF (frontend), visuellement standardisés
- **Email** : Resend (sandbox)
- **Paiements** : Stripe + PayPal (test mode)

## Fonctionnalités implémentées

### Core Features (DONE)
- Authentification Admin + Client
- Dashboard Admin complet (Contacts, Avis, FAQ, Parrainage, RDV, Relance, Alertes, Config, Notifications, Templates)
- Scanner de documents (caméra native mobile)
- StratégiIA (analyse rapide)
- Dossier Express IA (analyse complète avec paiement)
- Génération PDF premium standardisée (header dark + gold, watermark, badge expert)
- Système de paiement Stripe + PayPal (test mode)
- Mascotte "Straté" avec TTS français + Admin CRUD des conseils
- Contenu stratégique IP + PGPF intégrés partout
- Upload chunké async (testé jusqu'à 45MB)
- Auto-purge 30 jours (texte OCR + fichiers originaux)
- Politique de confidentialité + DataConsentBox

### Admin Human Review Workflow (DONE - 27 mars 2026)
- **Stockage des fichiers originaux** : Les documents clients (PDF/JPG/PNG) sont sauvegardés dans Emergent Object Storage pendant l'extraction
- **Endpoint téléchargement sécurisé** : `GET /api/admin/dossier-express/{id}/documents/{file_id}/download`
- **Modification de l'analyse** : `PUT /api/admin/dossier-express/{id}/analysis` — Marquage `human_reviewed=True`
- **Regénération PDF** : `POST /api/admin/dossier-express/{id}/regenerate-pdf` — PDF avec badge "Relu par expert", envoi email optionnel
- **UI "Revue expert"** : 4ème onglet dans le modal dossier admin avec :
  - Documents originaux téléchargeables
  - Indicateur de complétude (stockés, analysés, pages, % extraction)
  - Éditeur d'analyse IA avec sauvegarde
  - Notes internes admin
  - Boutons regénération PDF + envoi au client
- **Auto-purge étendue** : Les références aux fichiers originaux sont purgées avec le texte OCR après 30 jours

## Backlog

### P1 — Prochaines priorités
- Activation paiements live (Stripe/PayPal)

### P2 — En attente
- Intégration HubSpot CRM (attente identifiants utilisateur)
- Audit logging complet

### P3 — Futur
- Refactoring EmailTemplateEditor.jsx
- Consolidation moteurs PDF (FPDF seul côté backend)
- Contenu juridique final

## Intégrations 3P
- Anthropic Claude 3.5 Sonnet (Emergent LLM Key)
- Resend (sandbox)
- Stripe (test mode)
- PayPal (test mode)
- Emergent Object Storage
- HubSpot (attente)
