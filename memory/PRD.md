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

---

## Agents IA V2 Premium (Valides le 29 mars 2026)

### StrategiIA — Note globale : 8.97/10
- 9 sections systematiques (100% conformite)
- Citations juridiques reelles
- Chiffrage realiste des indemnisations

### Dossier Express IA — Note globale : 9.15/10
- 9 sections systematiques (100% conformite)
- Pieces detectees, Chronologie reconstruite, Completude documentaire

---

## Pipeline de Securite Paiement (DONE - 29 mars 2026)

### Pre-paiement : Double Protection
1. **Launch Mode Check** : Mode Ouvert/Controle/Indisponible — bloque le checkout si indisponible
2. **LLM Health Check** : Verifie cle Anthropic, quota, reponse — bloque le checkout si IA down
- Message client premium : "Le service est momentanement indisponible"

### Post-paiement : Pipeline Fail-safe Granulaire
- 8 etapes tracees avec double statut (`delivery_status` + `processing_step`)
- Notification admin automatique + email delai client en cas d'echec
- Validation analyse (>200 chars) avant PDF

### Admin Visibility Operationnelle
- 5 KPI cards production : Total | Livres | En cours | En attente | Incidents
- Filtres : Tous | Livres | En cours | Incidents | En attente
- Bouton "Relancer" pour dossiers en erreur

---

## Preparation Bascule Commerciale (DONE - 29 mars 2026)

### Mode Soft Launch
- 3 etats systeme : **Ouvert** | **Ouverture controlee** | **Temporairement indisponible**
- Toggle admin en temps reel
- Impact direct sur la possibilite de commander
- Message client premium en mode indisponible

### Monitoring Live Dashboard (Admin)
- 7 KPIs temps reel :
  - Commandes du jour / 7 jours
  - Taux de reussite (7j)
  - Incidents du jour
  - Delai moyen de traitement
  - Dossiers en attente
  - Interventions requises
- Incidents recents avec details

### Suivi Client Temps Reel
- Page publique `/dossier-express/suivi?id={dossier_id}`
- Timeline 7 etapes visuelles :
  1. Dossier bien recu
  2. Documents en cours de preparation
  3. Lecture documentaire en cours
  4. Analyse en cours de finalisation
  5. Rapport en cours de preparation
  6. Envoi en cours
  7. Rapport disponible
- En cas d'incident : message premium rassurant
- Bouton de telechargement quand rapport pret
- Auto-refresh toutes les 15 secondes
- Zero terme technique visible

### Documents de Lancement
- `CHECKLIST_LIVE.md` : 35+ elements par categorie
- `STRATEGIE_SOFT_LAUNCH.md` : 3 phases de montee progressive
- `PROTOCOLE_TESTS_LIVE.md` : 8 scenarios de test avec criteres

---

## Tests Passes
- iteration_140 : Cockpit UI (35/35)
- iteration_141 : Dark Mode (14/14)
- iteration_142 : V2 Premium IA (12/12)
- iteration_143 : Pipeline Securite Paiement (16/16)
- iteration_144 : Bascule Commerciale (25/25)
- Validation metier : 9 analyses reelles evaluees

---

## Backlog
### P1
- Activation paiements live (cles Stripe live + Anthropic a fournir)
### P2
- Integration HubSpot CRM (en attente credentials)
### P3
- Refactoring EmailTemplateEditor.jsx
- Consolidation moteurs PDF
### P4
- Finaliser contenu juridique
