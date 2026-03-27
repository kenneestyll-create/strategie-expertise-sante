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
- Stockage des fichiers originaux dans Emergent Object Storage
- Endpoint téléchargement sécurisé : `GET /api/admin/dossier-express/{id}/documents/{file_id}/download`
- Modification de l'analyse : `PUT /api/admin/dossier-express/{id}/analysis`
- Regénération PDF : `POST /api/admin/dossier-express/{id}/regenerate-pdf`
- UI "Revue expert" dans le modal admin dossier
- Auto-purge étendue aux fichiers originaux

### Badge "Relu par expert" côté client (DONE - 27 mars 2026)
- Badge doré "Expert" dans la navbar de l'espace client (discret, à côté du score)
- Bannière premium "Rapport vérifié par un expert" avec badge "Analyse premium" au-dessus de l'analyse
- Badge "Relu par expert" avec tooltip explicatif sous le score dans la carte principale
- Endpoint `/api/client/dossier-analysis` renvoie `human_reviewed` et `reviewed_at`
- Conditionnel : visible uniquement après validation par un expert admin

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
