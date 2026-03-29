# PRD — Strategie & Expertise Sante (S.E.S)

## Vision
Plateforme premium de conseil en maladies professionnelles avec deux agents IA specialises complementaires.

## Architecture
- **Frontend** : React 18 + Shadcn/UI + Tailwind CSS
- **Backend** : FastAPI + MongoDB
- **IA** : Anthropic Claude Sonnet 4 (`anthropic` SDK natif) + OpenAI GPT-4o (`openai` SDK natif)
- **PDF** : fpdf2 (backend) + jsPDF (frontend)
- **Email** : Resend | **Paiements** : Stripe + PayPal | **Stockage** : S3 (`boto3`) | **Recherche** : Algolia

## Autonomie : 100%
0 dependance a emergentintegrations. Tous SDK natifs.

## Agents IA V2 Premium (Valides le 29 mars 2026)

### StrategiIA — Note globale : 8.97/10
- 9 sections systematiques (100% conformite)
- Cible volume ajustee : 1400-1800 mots
- Citations juridiques reelles (articles CSS, jurisprudences Cour de cassation)
- Chiffrage realiste des indemnisations (IP, PGPF)

### Dossier Express IA — Note globale : 9.15/10
- 9 sections systematiques (100% conformite)
- Cible volume ajustee : 1500-2200 mots
- Pieces detectees, Chronologie reconstruite, Elements cles, Completude documentaire

### Articulation Dossier Express -> StrategiIA
- Chaine intelligente : DE structure la matiere -> StrategiIA produit lecture strategique enrichie

### Validation metier (29 mars 2026)
- 9/10 tests reels executes sur Claude Sonnet 4
- Grille a 8 criteres x 10 points
- **Verdict : COMMERCIALISABLE avec confiance**

## Pipeline de Securite Paiement (DONE - 29 mars 2026)

### Pre-paiement : LLM Health Check Bloquant
- Endpoint `/api/health/llm` verifie cle Anthropic, quota, reponse
- Checkout `/api/dossier-express/checkout` BLOQUE si LLM indisponible (HTTP 503)
- Frontend verifie AVANT de lancer le checkout
- Message client premium : "Le service est momentanement indisponible pour finalisation technique"

### Post-paiement : Pipeline Fail-safe Granulaire
- 8 etapes tracees : checkout_valide -> documents_recus -> extraction_en_cours -> analyse_ia -> pdf_en_cours -> stockage_en_cours -> email_en_cours -> termine
- 2 niveaux de statut : `delivery_status` + `processing_step`
- delivery_status : en_attente_traitement | incident_technique | livre_client | genere_sans_email
- processing_step : checkout_valide | documents_recus | extraction_en_cours | analyse_ia | pdf_en_cours | stockage_en_cours | email_en_cours | termine | erreur_ia | erreur_pdf | erreur_stockage | erreur_email | relance_admin
- Notification admin automatique en cas d'echec
- Email de delai professionnel au client en cas d'incident
- Validation analyse (>200 chars) avant PDF

### Admin Visibility
- 5 KPI cards : Total | Livres | En cours | En attente | Incidents
- Barre de filtres : Tous | Livres | En cours | Incidents | En attente
- Badges delivery_status colores + processing_step
- Bouton "Relancer" pour dossiers en erreur (avec retry_count)
- Endpoint `/api/admin/dossier-express/{id}/retry`

### Client UX Premium
- Pre-checkout : verification sante LLM, message rassurant si indisponible
- Processing : timeline 5 etapes avec detection incident
- Incident : page dediee "Votre dossier est bien pris en charge" avec message premium
- Erreur : zero mention technique, ton humain et rassurant

## Fonctionnalites Frontend (DONE)
- PremiumAnalysisRenderer : sections parsees avec icones dediees
- Dashboard Admin cockpit premium + Dark Mode Noir & Or
- Scanner documents natif, Upload chunke 45MB
- Admin Human Review, Badge "Relu par expert"
- Mascotte Strate + TTS francais + Admin CRUD

## Tests passes
- iteration_140 : Cockpit UI (35/35)
- iteration_141 : Dark Mode (14/14)
- iteration_142 : V2 Premium IA (12/12)
- iteration_143 : Pipeline Securite Paiement (16/16 — 9 backend + 7 frontend)
- Validation metier : 9 analyses reelles evaluees

## Backlog
### P1
- Activation paiements live (cles Stripe live + Anthropic)
### P2
- Integration HubSpot CRM
### P3
- Refactoring EmailTemplateEditor.jsx
- Consolidation moteurs PDF
### P4
- Finaliser contenu juridique
