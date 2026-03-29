# PRD — Stratégie & Expertise Santé (S.E.S)

## Vision
Plateforme premium de conseil en maladies professionnelles avec deux agents IA spécialisés complémentaires.

## Architecture
- **Frontend** : React 18 + Shadcn/UI + Tailwind CSS
- **Backend** : FastAPI + MongoDB
- **IA** : Anthropic Claude Sonnet 4 (`anthropic` SDK natif) + OpenAI GPT-4o (`openai` SDK natif)
- **PDF** : fpdf2 (backend) + jsPDF (frontend)
- **Email** : Resend | **Paiements** : Stripe + PayPal | **Stockage** : S3 (`boto3`) | **Recherche** : Algolia

## Autonomie : 100%
0 dépendance à emergentintegrations. Tous SDK natifs.

## Agents IA V2 Premium (Validés le 29 mars 2026)

### StratégiIA — Note globale : 8.97/10
- 9 sections systématiques (100% conformité)
- Cible volume ajustée : 1400-1800 mots
- Citations juridiques réelles (articles CSS, jurisprudences Cour de cassation)
- Chiffrage réaliste des indemnisations (IP, PGPF)
- Micro-calibrations appliquées : volume augmenté, préjudices extra-patrimoniaux, aide juridictionnelle

### Dossier Express IA — Note globale : 9.15/10
- 9 sections systématiques (100% conformité)
- Cible volume ajustée : 1500-2200 mots
- Pièces détectées, Chronologie reconstruite, Éléments clés, Complétude documentaire
- Gestion exemplaire de l'incertitude documentaire
- Micro-calibrations appliquées : volume augmenté, préjudices extra-patrimoniaux

### Articulation Dossier Express → StratégiIA
- Chaîne intelligente : DE structure la matière → StratégiIA produit lecture stratégique enrichie
- Injection automatique du contexte documentaire quand Dossier Express existe

### Validation métier (29 mars 2026)
- 9/10 tests réels exécutés sur Claude Sonnet 4
- Grille à 8 critères × 10 points
- Rapport complet : `/app/test_reports/VALIDATION_METIER_V2_PREMIUM.md`
- **Verdict : COMMERCIALISABLE avec confiance**

## Fonctionnalités Frontend (DONE)
- PremiumAnalysisRenderer : sections parsées avec icônes dédiées
- Dashboard Admin cockpit premium + Dark Mode Noir & Or
- Scanner documents natif, Upload chunké 45MB
- Admin Human Review, Badge "Relu par expert"
- Mascotte Straté + TTS français + Admin CRUD

## Tests passés
- iteration_140 : Cockpit UI (35/35)
- iteration_141 : Dark Mode (14/14)
- iteration_142 : V2 Premium IA (12/12)
- Validation métier : 9 analyses réelles évaluées

## Backlog
### P1
- Activation paiements live (clés Stripe live + Anthropic)
### P2
- Intégration HubSpot CRM
### P3
- Refactoring EmailTemplateEditor.jsx
- Consolidation moteurs PDF
### P4
- Finaliser contenu juridique
