# PRD — Stratégie & Expertise Santé (S.E.S)

## Vision
Plateforme premium de conseil en maladies professionnelles avec deux agents IA spécialisés complémentaires.

## Architecture
- **Frontend** : React 18 + Shadcn/UI + Tailwind CSS
- **Backend** : FastAPI + MongoDB
- **IA** : Anthropic Claude Sonnet 4.5 (`anthropic` SDK natif) + OpenAI GPT-4o (`openai` SDK natif)
- **PDF** : fpdf2 (backend) + jsPDF (frontend)
- **Email** : Resend
- **Paiements** : Stripe (`stripe` SDK natif) + PayPal
- **Stockage** : S3 compatible (`boto3`)
- **Recherche** : Algolia

## Autonomie : 100%
0 dépendance à emergentintegrations. Tous SDK natifs et standards.

## Deux Agents IA (V2 Premium — 29 mars 2026)

### StratégiIA — Agent de Pilotage Stratégique
**Mission** : Copilote d'orientation, stratégie et structuration décisionnelle
**Sections du rapport premium** :
1. Votre situation analysée
2. **Lecture stratégique du dossier** (qualification: fort potentiel / à consolider / sensible)
3. Cadre juridique applicable
4. **Leviers prioritaires identifiés** (4-6 leviers concrets et actionnables)
5. **Points de vigilance** (rassurants, intelligents, premium)
6. **Angles potentiellement sous-exploités** (signature de valeur ajoutée)
7. Évaluation et perspectives
8. **Plan d'action recommandé** (hiérarchisé, immédiatement exploitable)
9. Notre engagement à vos côtés

### Dossier Express IA — Agent de Pré-Expertise Documentaire
**Mission** : Exploitation réelle du contenu documentaire, reconnaissance des catégories, extraction intelligente
**Sections du rapport premium** :
1. Synthèse du dossier
2. **Pièces détectées** (catégories documentaires reconnues)
3. **Chronologie synthétique du dossier** (frise reconstruite à partir des dates)
4. **Éléments clés identifiés** (extraction intelligente des éléments significatifs)
5. Droits et indemnisations identifiés
6. **Points potentiellement sous-exploités** (transparence et crédibilité)
7. **Complétude documentaire** (indicateur intelligent: Très complète → Nécessite relecture)
8. Stratégie recommandée et prochaines étapes
9. Conclusion

### Articulation entre les deux agents
- Chaîne intelligente: Dossier Express IA → structure la matière → StratégiIA → produit une lecture stratégique enrichie
- Quand un Dossier Express existe pour un client, StratégiIA reçoit automatiquement le contexte documentaire
- Séparés dans leur logique, complémentaires dans l'écosystème

### Contrôle Qualité
- Vérification croisée x3 (chronologique, médico-administrative, cohérence globale)
- Nuance intelligente ("cet élément semble...", "ce point mérite confirmation...")
- Jamais d'extrapolation abusive ni de certitude artificielle

## Fonctionnalités Frontend
- **PremiumAnalysisRenderer** : Composant React qui parse le markdown par sections ## et affiche chaque bloc avec icône dédiée, couleur contextuelle et badge "Premium"
- Utilisé dans StrategiIA.jsx (résultats premium) et AdminDashboard.jsx (dialog analyse Dossier Express)

## Autres fonctionnalités (DONE)
- Auth Admin + Client, Dashboard Admin cockpit premium
- Scanner documents natif (caméra mobile)
- PDF premium, Paiements Stripe + PayPal
- Mascotte Straté + TTS français + Admin CRUD
- Upload chunké async (45MB), Auto-purge 30j
- Admin Human Review, Badge "Relu par expert"
- Dark Mode Admin Noir & Or
- Portabilité complète, 0 URL hardcodée, Dockerized

## Tests
- iteration_140: Cockpit UI (35/35 pass)
- iteration_141: Dark Mode (14/14 pass)
- iteration_142: V2 Premium IA (12/12 pass — backend + frontend 100%)

## Backlog
### P1
- Activation paiements live (clés Stripe live + Anthropic)
### P2
- Intégration HubSpot CRM
### P3
- Refactoring EmailTemplateEditor.jsx
- Consolidation moteurs PDF (backend uniquement)
### P4
- Finaliser le contenu juridique
