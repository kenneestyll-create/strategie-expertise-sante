# PRD — Stratégie & Expertise Santé (S.E.S)

## Vision
Plateforme premium de conseil en maladies professionnelles, avec scanner de documents, analyse IA (StratégiIA + Dossier Express IA), système de paiement et dashboard Admin complet.

## Architecture
- **Frontend** : React + Shadcn/UI + Tailwind CSS
- **Backend** : FastAPI + MongoDB + Emergent Object Storage
- **IA** : Anthropic Claude Sonnet 4.5 (via Emergent LLM Key)
- **PDF** : fpdf2 (backend) + jsPDF (frontend)
- **Email** : Resend (sandbox)
- **Paiements** : Stripe + PayPal (test mode)

## Variables d'environnement centrales
| Variable | Fichier | Usage |
|----------|---------|-------|
| `SITE_URL` | backend/.env | URLs emails, sitemap, robots.txt, SEO backend |
| `REACT_APP_SITE_URL` | frontend/.env | SEO frontend, canonical, OpenGraph, structured data |
| `REACT_APP_BACKEND_URL` | frontend/.env | Appels API (fallback si SITE_URL absent) |

## Fonctionnalités implémentées

### Core Features (DONE)
- Authentification Admin + Client
- Dashboard Admin complet
- Scanner de documents (caméra native mobile)
- StratégiIA (analyse rapide) + Dossier Express IA (analyse complète)
- Génération PDF premium standardisée
- Paiement Stripe + PayPal (test mode)
- Mascotte "Straté" avec TTS français + Admin CRUD conseils
- Upload chunké async (testé jusqu'à 45MB)
- Auto-purge 30 jours (OCR + fichiers originaux)

### Admin Human Review Workflow (DONE - 27 mars 2026)
- Stockage fichiers originaux dans Object Storage
- Endpoints admin: download, modification analyse, regénération PDF
- UI "Revue expert" dans le modal admin dossier

### Badge "Relu par expert" côté client (DONE - 27 mars 2026)
- Badge doré navbar + Bannière premium + Tooltip avec date
- Conditionnel: visible uniquement après validation expert

### Portabilité SITE_URL (DONE - 28 mars 2026)
- Suppression de TOUTES les URLs preview hardcodées (0 occurrence)
- Variables d'environnement centrales: SITE_URL (backend) + REACT_APP_SITE_URL (frontend)
- Sitemap/robots.txt dynamiques via API backend
- Fichiers statiques nettoyés (sitemap.xml, robots.txt fallback)
- Ancien scanner worker supprimé
- Script nettoyage service workers obsolètes ajouté
- Balises anti-cache ajoutées dans index.html
- QR Code PDF pointe vers strategie-expertise-sante.fr (domaine final)
- Strip pattern PDF élargi à tout preview.emergentagent.com

## Portabilité du projet
| Composant | Portable | Dépendance |
|-----------|----------|------------|
| Frontend React | ✅ 100% | Aucune |
| Backend FastAPI | ⚠️ 85% | emergentintegrations (LLM, Stripe, Storage) |
| Admin Dashboard | ✅ 100% | Aucune |
| OCR (Tesseract/PyMuPDF) | ✅ 100% | Open source |
| PDF (fpdf2) | ✅ 100% | Open source |
| Emails (Resend) | ✅ 100% | Clé API portable |
| IA (Claude) | ❌ | Via emergentintegrations |
| Stripe | ❌ | Via emergentintegrations |
| Object Storage | ❌ | API Emergent |
| MongoDB | ⚠️ | Local conteneur, à migrer |

## Backlog

### P1
- Activation paiements live (Stripe/PayPal)

### P2
- Intégration HubSpot CRM (attente identifiants)

### P3
- Remplacement emergentintegrations → SDKs natifs (pour autonomie complète)
- Dockerfile + docker-compose.yml
- Refactoring EmailTemplateEditor.jsx
- Consolidation moteurs PDF

## Intégrations 3P
- Anthropic Claude 3.5 Sonnet (Emergent LLM Key)
- Resend (sandbox)
- Stripe + PayPal (test mode)
- Emergent Object Storage
- Algolia Search
- HubSpot (attente)
