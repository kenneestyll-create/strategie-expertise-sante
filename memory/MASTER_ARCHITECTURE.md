# MASTER ARCHITECTURE — Strategie & Expertise Sante
## Document de reference maitre — Architecture globale du projet
### Date de creation : 06/04/2026

---

## 1. VUE D'ENSEMBLE

Strategie & Expertise Sante (S.E.S) est une plateforme premium d'accompagnement en droit de la securite sociale et en expertise sante. Elle assiste les victimes d'accidents du travail, de maladies professionnelles, de litiges assurantiels et de demarches MDPH grace a une IA specialisee et a une expertise humaine structuree.

**Stack technique** : React (frontend) + FastAPI (backend) + MongoDB (base de donnees) + Claude Sonnet 4.5 (LLM)

**Trois modes d'acces** :
- **Public** : pages marketing, simulateur gratuit (StrategiIA Basic), chatbot d'orientation, ressources
- **Client** : espace personnel, suivi de dossier, Dossier Express IA (payant)
- **Admin** : tableau de bord complet de gestion, pilotage IA, scoring qualite, preparation V2

---

## 2. STRUCTURE GLOBALE DU PROJET

```
/app/
├── backend/                          # API FastAPI (port 8001)
│   ├── server.py                     # Point d'entree principal, configuration CORS, middleware, montage des routes
│   ├── config.py                     # Configuration centralisee (DB, cles, logger)
│   ├── models.py                     # Modeles Pydantic
│   ├── constants/                    # Donnees statiques et intelligence metier
│   │   ├── prompts.py                # TOUS les prompts LLM (GELE V1)
│   │   ├── assurance_knowledge.py    # Base assurantielle (GELE V1)
│   │   ├── contestation_knowledge.py # Base CCAS RATP / contestation (GELE V1)
│   │   ├── mdph_knowledge.py         # Base MDPH (GELE V1)
│   │   ├── seed_patterns.py          # Patterns d'initialisation (enrichissable)
│   │   ├── statuses.py               # Constantes de statuts
│   │   ├── workflows.py              # Constantes de workflows (quotas, limites)
│   │   └── guards.py                 # Validations metier
│   ├── routes/                       # Endpoints API
│   │   ├── strategiia.py             # Analyses IA (Basic gratuit + Premium payant)
│   │   ├── dossier_express.py        # Pipeline Dossier Express IA (payant)
│   │   ├── chatbot.py                # Chatbot d'orientation
│   │   ├── knowledge_patterns.py     # Moteur de patterns + scoring V2 readiness
│   │   ├── admin.py                  # CRUD admin, config, analytics
│   │   ├── client.py                 # Espace client
│   │   ├── payments.py               # Stripe
│   │   ├── public.py                 # Endpoints publics (contact, avis)
│   │   ├── upload.py                 # Upload de documents
│   │   ├── tracking.py               # Analytics et conversion
│   │   ├── conseils.py               # Conseils mascotte Strate
│   │   ├── forum.py                  # Forum communautaire
│   │   └── misc.py                   # Endpoints divers
│   └── utils/                        # Utilitaires
│       ├── llm.py                    # Pipeline LLM complet (GELE V1)
│       ├── chatbot.py                # Logique chatbot + FAQ (GELE V1)
│       ├── quality_scoring.py        # Scoring qualite des rapports (GELE V1)
│       ├── case_outcome_memory.py    # Collecte silencieuse V2
│       ├── pdf.py                    # Generation PDF StrategiIA
│       ├── pdf_guides.py             # Generation PDF guides thematiques
│       ├── auth.py                   # Authentification JWT
│       ├── email.py                  # Envoi emails (Resend)
│       ├── notifications.py          # Notifications admin
│       ├── push.py                   # Push notifications (VAPID)
│       ├── storage.py                # Stockage objets (S3)
│       ├── document_extraction.py    # Extraction texte PDF/images
│       └── ocr_gpt.py               # OCR via GPT Vision
│
├── frontend/                         # Application React (port 3000)
│   └── src/
│       ├── App.js                    # Routeur principal + anti-copie
│       ├── pages/                    # Pages de l'application
│       │   ├── HomePage.jsx          # Page d'accueil
│       │   ├── SimulateurPage.jsx    # Formulaire StrategiIA
│       │   ├── DossierExpressPage.jsx# Formulaire Dossier Express
│       │   ├── AdminDashboard.jsx    # Dashboard admin complet
│       │   ├── AdminLoginPage.jsx    # Connexion admin
│       │   ├── EspaceClientPage.jsx  # Espace client
│       │   ├── TarifsPage.jsx        # Page tarifs premium
│       │   ├── AboutPage.jsx         # A propos + positionnement
│       │   ├── ContactPage.jsx       # Formulaire contact
│       │   ├── ResourcesPage.jsx     # Ressources et guides
│       │   ├── MentionsLegalesPage   # Mentions legales + PI
│       │   └── [autres pages]        # MDPH, Expertise, Services...
│       ├── components/               # Composants reutilisables
│       │   ├── StrategiIA.jsx        # Rendu des analyses IA
│       │   ├── ChatBot.jsx           # Chatbot frontend
│       │   ├── MascotteStrate.jsx    # Mascotte avec TTS
│       │   ├── AdminV2Readiness.jsx  # Feu tricolore V2 (admin)
│       │   ├── AdminConseilsStrate   # Gestion conseils Strate
│       │   ├── DocumentScanner.jsx   # Camera mobile
│       │   └── [autres composants]
│       ├── data/                     # Donnees statiques frontend
│       ├── hooks/                    # Custom hooks React
│       ├── context/                  # Contextes React (auth)
│       └── styles/                   # CSS complementaire
│
└── memory/                           # Documentation strategique
    ├── PRD.md                        # Product Requirements Document
    ├── IA_BASELINE_V1.md             # Baseline officielle IA V1
    └── [documents du kit]            # Kit d'independance
```

---

## 3. LES GRANDES BRIQUES DU PRODUIT

### 3.1 StrategiIA — Moteur d'analyse strategique

**Role** : Produit coeur. Analyse une situation client (accident, maladie pro, litige) et genere un rapport strategique personnalise.

**Deux niveaux** :
- **Basic** (gratuit, 550 mots) : lecture ciblee, identification du vrai noeud, action prioritaire
- **Premium** (payant, 1800-2400 mots) : pilotage approfondi avec cadre juridique, leviers, evaluation, plan d'action complet

**Fichiers** : `routes/strategiia.py` (pipeline) + `constants/prompts.py` (STRATEGIIA_*) + `utils/llm.py` (appels LLM)

**Flux** : Formulaire client → enrichissement contexte (assurance/MDPH/contestation + patterns) → appel LLM → scoring qualite → generation PDF → stockage → notification admin (si premium)

### 3.2 Dossier Express IA — Pre-expertise documentaire

**Role** : Service payant premium. Analyse les documents fournis par le client (certificats medicaux, expertises, courriers) et genere un rapport de pre-expertise.

**Fichiers** : `routes/dossier_express.py` + `constants/prompts.py` (DOSSIER_EXPRESS_*) + `utils/llm.py` (generate_dossier_report_multistage)

**Flux** : Formulaire + upload documents → extraction texte (pdfplumber + OCR GPT) → enrichissement contexte → generation rapport multi-stage (7 sections en 3 batches paralleles) → scoring qualite → generation PDF → livraison client + notification admin

### 3.3 Chatbot — Orientation intelligente

**Role** : Assistant minimaliste. Oriente vers StrategiIA ou Dossier Express en 1-2 phrases max. Ne fait PAS d'analyse. Detection de complexite pour adapter le prompt.

**Fichiers** : `routes/chatbot.py` + `utils/chatbot.py` (FAQ, prompts, detection complexite)

**Modele** : Claude Haiku 4.5 (plus rapide, moins couteux — orientation uniquement)

### 3.4 Knowledge Patterns — Intelligence metier apprenante

**Role** : Base d'enseignements anonymises qui enrichit les analyses IA. Moteur de selection intelligent qui injecte les patterns les plus pertinents dans le contexte LLM.

**Fichiers** : `routes/knowledge_patterns.py` (moteur + CRUD admin) + `constants/seed_patterns.py` (initialisation)

**Scoring** : categorie (+5), type_sinistre (+10), metier (+3), blocage (+5), tags (+3 chacun)

### 3.5 Quality Scoring — Pilotage qualite interne

**Role** : Evalue chaque rapport genere sur 7 criteres (/100). Outil admin de pilotage, ne modifie PAS le rendu client.

**Fichiers** : `utils/quality_scoring.py`

**Criteres** : Personnalisation metier (20), sinistre (20), blocage (15), blocs premium (15), densite (15), faible genericite (10), coherence (5)

### 3.6 Case Outcome Memory — Preparation V2

**Role** : Module silencieux. Collecte des signaux structures (anonymises) a chaque analyse pour preparer la future V2 predictive. Respecte strictement l'opt-out RGPD.

**Fichiers** : `utils/case_outcome_memory.py` (extraction + stockage) + `routes/knowledge_patterns.py` (V2 readiness + historique)

### 3.7 Dashboard Admin — Centre de pilotage

**Role** : Interface complete de gestion. 14 onglets couvrant contacts, avis, parrainage, RDV, clients, relance, alertes, analyses IA, dossiers express, analytique, documents, conseils Strate, configuration, notifications, templates.

**Fichiers** : `pages/AdminDashboard.jsx` (4000+ lignes) + composants satellites (AdminV2Readiness, AdminConseilsStrate, AdminConversionAnalytics, etc.)

### 3.8 Bases de connaissances metier

**Role** : Dictionnaires metier injectes dans le contexte LLM pour enrichir les analyses avec des informations sectorielles precises.

**Trois bases** :
- Assurantielle (`assurance_knowledge.py`) : GENERALI, GROUPAMA, CNP — garanties, definitions, pieges
- CCAS RATP / Contestation (`contestation_knowledge.py`) : regime special RATP, procedures de contestation
- MDPH (`mdph_knowledge.py`) : AAH, PCH, RQTH, CMI, voies de recours

---

## 4. DEPENDANCES CRITIQUES

### Indispensable au fonctionnement
| Composant | Fichier(s) | Impact si absent |
|---|---|---|
| MongoDB | `config.py` (MONGO_URL) | Aucun stockage, application inutilisable |
| Cle LLM (Anthropic ou Emergent) | `utils/llm.py` | Aucune analyse IA possible |
| Prompts | `constants/prompts.py` | Rapports sans structure ni qualite |
| Pipeline LLM | `utils/llm.py` | Aucun appel IA possible |
| Auth JWT | `utils/auth.py` | Acces admin impossible |

### Secondaire (degradation gracieuse)
| Composant | Fichier(s) | Impact si absent |
|---|---|---|
| Stripe | `routes/payments.py` | Paiements impossibles, reste en mode test |
| Resend (email) | `utils/email.py` | Pas de notifications email |
| S3 (stockage) | `utils/storage.py` | PDF non telechargeables (actuellement bloque) |
| Push notifications | `utils/push.py` | Pas de push navigateur |

### Purement admin (invisible pour les clients)
| Composant | Role |
|---|---|
| Quality Scoring | Pilotage qualite interne des rapports |
| Case Outcome Memory | Collecte silencieuse V2 |
| V2 Readiness | Feu tricolore admin |
| Knowledge Patterns CRUD | Gestion des patterns |
| AdminOnboardingTour | Tutoriel interactif admin |
| AdminHelpPanel | Guide d'aide admin |

### Purement cosmetique (zero impact fonctionnel)
| Composant | Role |
|---|---|
| GoldDustOverlay | Effet visuel particules |
| MascotteStrate | Mascotte avec conseils TTS |
| ExitIntentPopup | Popup retention |
| Anti-copie (useContentProtection) | Protection selection/clic droit |

---

## 5. ZONES SENSIBLES

### Ce qui peut casser les sorties IA
- **`constants/prompts.py`** : toute modification de prompt change la qualite, le ton et la structure des rapports
- **`utils/llm.py`** : toute modification du pipeline (split, parallele, max_tokens) change le volume et la coherence
- **`utils/quality_scoring.py`** : modifier les seuils change l'evaluation interne
- **Injection contextuelle** : l'ordre et le contenu de l'enrichissement (assurance + contestation + MDPH + patterns) impacte directement la pertinence

### Ce qui ne doit jamais etre modifie a la legere
- **Structure markdown des rapports** : les sections (## titres) sont exploitees par le PDF, le scoring et le frontend
- **Logique RGPD** : le flag `improvement_optout` conditionne toute la collecte V2
- **Pipeline de paiement** : Stripe webhooks, tunnel client, generation PDF post-paiement
- **Pipeline d'extraction documentaire** : pdfplumber → OCR GPT → assemblage texte
- **Longueurs cibles des rapports** : 550 / 1800-2400 / 2000-2800 mots — calibrees pour la valeur percue

### Ce qui est delicat mais manipulable
- **Bases de connaissances** : enrichissables mais tout ajout impacte le contexte LLM (tokens, coherence)
- **Seed patterns** : ajout autorise sous protocole, modification des existants interdite
- **AdminDashboard** : fichier massif (4000+ lignes), toute modification exige prudence

---

## 6. MODELE DE DONNEES MONGODB

### Collections principales
| Collection | Usage | Criticite |
|---|---|---|
| `users` | Comptes admin | Haute |
| `strategiia_analyses` | Analyses StrategiIA (basic + premium) | Haute |
| `premium_analyses` | Analyses premium payantes | Haute |
| `dossier_express` | Dossiers Express IA | Haute |
| `contact_submissions` | Demandes de contact | Moyenne |
| `knowledge_patterns` | Patterns metier anonymises | Haute |
| `case_outcomes` | Collecte V2 silencieuse | Moyenne (futur haute) |
| `v2_readiness_history` | Historique score V2 | Basse |
| `conseils_strate` | Conseils mascotte | Basse |
| `client_reviews` | Avis clients | Moyenne |
| `chatbot_sessions` | Sessions chatbot | Basse |
| `email_logs` | Historique emails | Basse |
| `referrals` | Parrainages | Moyenne |
| `scheduled_campaigns` | Campagnes email | Moyenne |

---

## 7. FLUX PRINCIPAUX

### Analyse StrategiIA (flux complet)
```
Client remplit formulaire
    ↓
Backend recoit les donnees (situation, metier, sinistre, regime)
    ↓
Detection automatique du contexte :
  - assurance ? → get_assurance_context()
  - CCAS RATP ? → get_contestation_context()
  - MDPH ? → get_mdph_context()
    ↓
Selection des patterns pertinents :
  → get_knowledge_patterns_context(categorie, metier, sinistre, blocage)
    ↓
Construction du prompt USER avec contexte enrichi
    ↓
Appel LLM (Basic: 1 call / Premium: 2 calls paralleles)
    ↓
Scoring qualite (quality_scoring.score_report)
    ↓
Collecte silencieuse V2 (case_outcome_memory.store_case_outcome)
    ↓
Stockage MongoDB + generation PDF
    ↓
Notification admin (si premium)
```

---

*Document cree le 06/04/2026 — Kit d'Independance Projet S.E.S*
