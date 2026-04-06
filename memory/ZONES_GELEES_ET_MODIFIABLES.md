# ZONES GELEES ET MODIFIABLES — Garde-fou operationnel
## Strategie & Expertise Sante
### Date de creation : 06/04/2026

---

Ce document sert de reference pour tout futur intervenant sur le projet.
Il determine ce qui peut etre touche, ce qui exige de la prudence, et ce qui est interdit sans autorisation explicite.

---

## A. ZONES GELEES — PROTECTION FORTE

Ces elements constituent le coeur du produit. Toute modification non autorisee peut degrader la qualite, casser la coherence ou creer une regression majeure.

### A.1 Prompts USER valides

| Element | Fichier | Raison du gel |
|---|---|---|
| STRATEGIIA_BASIC_PROMPT | `constants/prompts.py` L184-223 | Structure exacte du rapport gratuit (marqueurs, sections, longueur) |
| STRATEGIIA_PREMIUM_PROMPT | `constants/prompts.py` L225-310 | Structure du rapport premium payant (12 sections, phrase finale) |
| DOSSIER_EXPRESS_PROMPT | `constants/prompts.py` L416-485 | Structure du rapport Dossier Express (13 sections) |
| SYSTEM_PROMPT_LIGHT | `utils/chatbot.py` L142-150 | Prompt chatbot simple |
| SYSTEM_PROMPT_FULL | `utils/chatbot.py` L153-161 | Prompt chatbot complet |

**Risque si modifie** : Changement de la structure des rapports → PDF mal formate, scoring qualite fausse, readwall cassee, experience client degradee.

### A.2 Pipeline LLM

| Element | Fichier | Raison du gel |
|---|---|---|
| llm_stream_call | `utils/llm.py` L56-83 | Streaming httpx vers Emergent proxy |
| llm_async_call | `utils/llm.py` L86-179 | Split Premium (2 paralleles) + Split Dossier Express (2 sequentiels) |
| generate_dossier_report_multistage | `utils/llm.py` L212-354 | Pipeline 7 sections en 3 batches (Dossier Express) |

**Risque si modifie** : Rapports tronques, timeouts, incoherence entre sections, perte de la logique multi-stage.

### A.3 Scoring qualite

| Element | Fichier | Raison du gel |
|---|---|---|
| score_report() | `utils/quality_scoring.py` | 7 criteres calibres, seuils valides |
| GENERIC_PHRASES | `utils/quality_scoring.py` L24-53 | 36 formulations bannies |
| METIER_KEYWORDS | `utils/quality_scoring.py` L56-64 | Detection personnalisation metier |
| SINISTRE_KEYWORDS | `utils/quality_scoring.py` L67-75 | Detection personnalisation sinistre |

**Risque si modifie** : Scores fausses, perte de visibilite sur la qualite, regression silencieuse.

### A.4 Bases de connaissances metier

| Element | Fichier | Lignes |
|---|---|---|
| Base assurantielle complète | `constants/assurance_knowledge.py` | 975 |
| Base CCAS RATP / contestation | `constants/contestation_knowledge.py` | 497 |
| Base MDPH | `constants/mdph_knowledge.py` | 655 |

**Risque si modifie** : Injection de contexte errone dans les analyses → analyses factuellement fausses, perte de credibilite.

### A.5 Structure PDF

| Element | Fichier |
|---|---|
| generate_secured_pdf | `utils/pdf.py` |
| generate_dossier_pdf | `utils/pdf.py` |
| _clean_analysis | `utils/pdf.py` L34-50 |

**Risque si modifie** : PDF mal formate, logo absent, couverture cassee, encarts detruits, QR code manquant.

### A.6 Frontend public client

| Element | Pourquoi gele |
|---|---|
| HomePage.jsx | Page d'accueil — premier contact client |
| SimulateurPage.jsx | Tunnel StrategiIA — conversion |
| DossierExpressPage.jsx | Tunnel Dossier Express — conversion payante |
| TarifsPage.jsx | Tarification — impact commercial |
| Header.jsx, Footer.jsx | Navigation globale, mentions legales |
| StrategiIA.jsx | Rendu des rapports — readwall + sections |

### A.7 Paiements

| Element | Fichier |
|---|---|
| Stripe integration | `routes/payments.py` |
| Webhooks Stripe | `routes/strategiia.py` (webhook) |
| Tunnel premium | `routes/strategiia.py` L200+ |

**Risque si modifie** : Paiements non traites, double facturation, rapports non delivres.

---

## B. ZONES MODIFIABLES AVEC PRUDENCE

Ces elements peuvent etre enrichis ou ajustes, mais toute modification doit etre testee et documentee.

### B.1 Prompts SYSTEM enrichissables

| Element | Type de modification autorise | Procedure |
|---|---|---|
| STRATEGIIA_SYSTEM_PROMPT | Ajout de jurisprudences, baremes, classes metier | Protocole IA_BASELINE_V1.md |
| DOSSIER_EXPRESS_SYSTEM_PROMPT | Ajout de references documentaires | Protocole IA_BASELINE_V1.md |

**Interdit** : Supprimer des regles existantes, modifier le ton, retirer des formulations bannies.

### B.2 Knowledge patterns

| Action | Autorise | Procedure |
|---|---|---|
| Ajouter de nouveaux patterns | OUI | Respecter la structure, seed idempotent, test de non-regression |
| Modifier un pattern existant | NON sans validation admin | Modification → validation obligatoire |
| Supprimer un pattern | OUI (admin dashboard) | Pas d'impact si bien cible |
| Valider un pattern en attente | OUI (admin dashboard) | Active l'injection dans les analyses |

### B.3 Case outcomes et V2 readiness

| Element | Modifiable | Notes |
|---|---|---|
| Extraction de features | OUI avec prudence | Ajout de mots-cles possibles |
| Seuils V2 readiness | OUI | 200/500 cas actuels, ajustables |
| Scoring V2 | OUI | Poids des criteres ajustables |
| Historique V2 | OUI | Structure extensible |

### B.4 Configuration admin

| Element | Modifiable |
|---|---|
| Compteurs Hero (visiteurs, dossiers, etc.) | OUI (admin dashboard) |
| Tarifs affiches | OUI (admin dashboard) |
| Badges promo | OUI (admin dashboard) |
| Templates email | OUI (admin dashboard) |
| Conseils mascotte Strate | OUI (admin dashboard) |

### B.5 AdminDashboard.jsx

**Modifiable** mais avec une extreme prudence : fichier de 4000+ lignes, 14 onglets, nombreuses dependances. Toute modification doit etre testee exhaustivement pour eviter de casser un onglet adjacent.

---

## C. ZONES LIBRES — PEU RISQUEES

Ces elements peuvent etre modifies sans risque significatif pour le produit.

### C.1 Contenus admin secondaires

| Element | Impact si modifie |
|---|---|
| AdminOnboardingTour.jsx | Tour de presentation — zero impact client |
| AdminHelpPanel.jsx | Guide d'aide — zero impact client |
| AdminTestBanner.jsx | Bandeau mode test — zero impact client |
| AdminConversionAnalytics.jsx | Graphiques analytics — zero impact client |

### C.2 Documentation interne

| Element | Impact si modifie |
|---|---|
| PRD.md | Document de suivi projet |
| IA_BASELINE_V1.md | Documentation du gel V1 |
| Tous les fichiers /memory/*.md | Documentation strategique |

### C.3 Composants cosmetiques

| Element | Impact si modifie |
|---|---|
| GoldDustOverlay.jsx | Effet particules — purement decoratif |
| MascotteStrate.jsx | Mascotte — pas d'impact fonctionnel |
| ExitIntentPopup.jsx | Popup retention — pas d'impact fonctionnel |
| Logo.jsx | Composant logo — changement visuel uniquement |

### C.4 Donnees statiques frontend

| Element | Impact si modifie |
|---|---|
| data/maladiesProfessionnelles.js | Liste des tableaux MP — affichage informatif |
| data/mdphDirectory.js | Annuaire MDPH — affichage informatif |
| data/searchIndex.js | Index de recherche globale — affichage |

### C.5 Tests

| Element | Impact si modifie |
|---|---|
| backend/tests/*.py | Aucun impact production |
| test_reports/*.json | Rapports de test historiques |

---

## RESUME VISUEL

```
┌─────────────────────────────────────────────┐
│            ZONE GELEE (ROUGE)               │
│  Prompts USER, Pipeline LLM, Scoring,       │
│  Bases metier, Structure PDF, Paiements,     │
│  Frontend public client                      │
├─────────────────────────────────────────────┤
│         ZONE PRUDENTE (ORANGE)              │
│  Prompts SYSTEM (enrichissement),            │
│  Knowledge patterns, Case outcomes,          │
│  AdminDashboard, Config admin                │
├─────────────────────────────────────────────┤
│          ZONE LIBRE (VERT)                  │
│  Composants admin secondaires, Docs,         │
│  Cosmetique, Donnees statiques, Tests        │
└─────────────────────────────────────────────┘
```

---

*Document cree le 06/04/2026 — Kit d'Independance Projet S.E.S*
