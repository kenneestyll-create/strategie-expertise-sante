# Stratégie & Expertise Santé (S.E.S) — PRD

## Problème original
Application web premium de conseil en maladies professionnelles. Objectifs : scanner de documents fiable, contenu stratégique (IP/PGPF), mascotte IA "Straté" avec TTS et gestion Admin, dashboard Admin complet.

## Architecture
- Frontend: React + Tailwind CSS + Shadcn/UI
- Backend: FastAPI + MongoDB
- Intégrations: Anthropic Claude (clé API native), Stripe (test), Resend (sandbox)

## Ce qui est implémenté
- Scanner de documents natif (caméra mobile `<input capture>`) — DONE
- Contenu stratégique IP & PGPF intégré — DONE
- Mascotte Straté visuelle + TTS français robuste — DONE
- Backend CRUD `/api/conseils` complet — DONE
- Admin "Conseils Straté" tab fonctionnel — DONE
- Hero section avec image parisienne (Tour Eiffel) — DONE
- Frontend Freeze : layout-guardrails.css — DONE
- Hero déclaré ZONE GELÉE — DONE
- Admin > Config > Compteur visiteurs Hero (auto-incrément) — DONE
- Admin > Config > Base dossiers hebdomadaire — DONE
- Admin > Config > Le défi en chiffres — DONE
- Admin > Config > Tarifs & Promotions — DONE
- Admin > Guide interactif flottant (15 sections, 9 étapes Config, Ctrl+H) — DONE
- Admin > Tutoriel interactif d'onboarding Straté (6 étapes) — DONE
- Admin > Statistiques d'engagement du tutoriel — DONE
- Admin > Préparation Production (purge données test + reset compteurs) — DONE
- Hero renommé : "personnes accompagnées" → "visiteurs" — DONE
- Dossier Express : padding hero réduit (tout visible sans scroll desktop) — DONE (03/04/2026)
- Mascotte Straté : bouton "Écouter" whitespace-nowrap (plus de coupure) — DONE (03/04/2026)
- FAQ : correction champ `réponse` → `reponse` (réponses réaffichées) — DONE (03/04/2026)
- 3 blocs flottants Section 2 : animation vague au hover desktop — DONE (03/04/2026)
- 3 blocs flottants Section 2 : pulse doré + flottement permanent mobile+desktop — DONE (03/04/2026)
- Verrouillage Premium des 3 rapports PDF (10 missions) + Scoring qualité interne — DONE (03/04/2026)
- Navigation Admin mobile : Select dropdown avec optgroups remplace tabs horizontaux (03/04/2026)
- Audit mobile Admin Dashboard complet — corrigé 9 sections responsive (03/04/2026)
- Upgrade Chirurgical Premium des 3 prompts PDF (4 blocs premium + ciblage métier/sinistre/blocage) — DONE (03/04/2026)
- Clé API Anthropic native configurée — DONE
- Chatbot optimisé sur claude-haiku-4-5 — DONE
- Bug PDF Unicode résolu (police LiberationSans TTF) — DONE
- Téléchargement PDF admin : axios → fetch natif — DONE
- **Base de connaissances assurantielle** (`assurance_knowledge.py`) — DONE (04/04/2026)
- **Base de connaissances contestation IPP** (`contestation_knowledge.py`) — DONE (04/04/2026) : Procedures CCAS RATP + regime general CPAM. Contenu : architecture regime special RATP, procedure declaration MP (adresses GIS/PAP/ASOS B203, Medecine-conseil CH34), delais instruction (Art. R.441-10 : 30j AT, 2 mois MP, silence=reconnaissance), delai complementaire (Art. R.441-14), CSOM (taux 10-60%, accord 12/07/2024), Commission Medicale RATP (recours 2 mois, assistance medecin), Conseil de Prevoyance (31 rue Belliard), contestation CRA (G2210) vs CRAM (G1197), revision post-consolidation (L.443-1), recours tiers (L.454-1). Injection automatique par detection mots-cles.
  - 3 assureurs : GENERALI, GROUPAMA GAN VIE, CNP ASSURANCES
  - 7 garanties normalisées : ITT, ITP, IPT, IPP, PTIA, PE, DÉCÈS
  - Tableau comparatif inter-assureurs (7 critères)
  - Fonction `get_assurance_context()` injectable dans les prompts
- **Injection contexte assurantiel dans StrategiIA + Dossier Express** — DONE (04/04/2026)
  - Backend : injection automatique quand type_dossier = "assurance"
  - Frontend : dropdown dynamique "Régime" ↔ "Type de garantie concernée"
- **Détecteur automatique d'assureur** (`detect_insurer_from_text()`) — DONE (04/04/2026)
  - Détection par nom exact, variantes, acronymes, références contrat
  - Intégré dans StrategiIA + Dossier Express (non-bloquant)
  - Priorité : garantie > assureur détecté > fallback générique
  - Traçabilité discrète : `detected_insurer` stocké dans MongoDB

### Conformite RGPD & Amelioration continue (04/04/2026)
- Architecture RGPD : separation stricte entre donnees client (MongoDB) et base d'amelioration interne (`knowledge_patterns`)
- DataConsentBox enrichi : section "Amelioration continue du service" depliable + checkbox opt-out client
- Politique de Confidentialite : Section 12 ajoutee (texte juridique complet + 5 garanties essentielles + avertissement anonymisation)
- API knowledge-patterns : CRUD admin-only, validation manuelle, patterns anonymises, limite 500 chars, usage_autorise=false par defaut
- Champ improvement_optout : passe dans StrategiIA et DossierExpress, stocke dans les analyses MongoDB
- Regles verrouillees : pas de fine-tuning brut, pas de recuperation automatique, pas de donnees identifiantes dans knowledge_patterns

### Moteur d'enrichissement metier intelligent (04/04/2026)
- Moteur de selection knowledge_patterns avec scoring par priorite (exact match +10, categorie +5, tags +3)
- Limites strictes : max 5 patterns, 4 vigilances, 4 leviers (total 12)
- Anti-hallucination : formulations conditionnelles imposees dans le contexte injecte
- Injection dans SYSTEM prompt de StrategiIA et Dossier Express (enhanced_system)
- Respect improvement_optout : si true, aucun pattern injecte
- Si contexte trop faible ou base vide : aucune injection (Mission 8)
- 14 seed patterns de demarrage (blocages, vigilances, leviers, erreurs frequentes, pieces manquantes)
- Couverture : MP, AT, litige assurantiel, contestation IPP, multi-metiers, multi-garanties
  - 8/8 tests PASS (6 cas obligatoires + 2 bonus)
- **Enrichissement base assurantielle : GMF VIE (Accolia n°07001)** — DONE (04/04/2026)
  - 4e assureur intégré : GMF VIE (Groupe Covéa) — contrat temporaire décès
  - 2 garanties : Décès (capital double si accident, carence 6 mois) + PTIA (cessation 65 ans)
  - 9 red flags, lecture stratégique complète, notes globales
  - Tableau comparatif étendu à 9 critères (dont restriction géographique, doublement capital)
  - Détecteur mis à jour : "gmf", "accolia", "contrat 07001", "covea"
  - 9/9 tests PASS, zéro régression
- **Mapping contextuel dynamique du 2e dropdown** — DONE (04/04/2026)
  - Chaque type de dossier a son propre sous-menu contextuel :
    - AT / MP / Autre → "Régime" (conservé)
    - Litige assurantiel → "Type de garantie" (ITT, PTIA, etc.)
    - Expertise médicale → "Type d'expertise" (amiable, judiciaire, contre-expertise, CPAM, employeur)
    - Demande MDPH → "Type de demande MDPH" (AAH/PCH/RQTH/CMI/orientation/renouvellement refusés)
    - Faute inexcusable → "Phase judiciaire" (pré-contentieux, CPAM, tribunal, appel)
    - Recours / Contestation → "Type de recours" (CRA, contentieux, expertise de recours, médiation)
    - Contestation taux IPP (DE) → "Objet de la contestation"
  - Implémenté dans StrategiIA + DossierExpress
  - Reset automatique du 2e dropdown au changement de type
  - 15/15 tests PASS, zéro régression, zéro modification backend

### Base de connaissances MDPH (05/04/2026)
- **Fichier** : `/app/backend/constants/mdph_knowledge.py` — DONE
- Couverture complete : MDPH general, AAH (conditions, montants, deconjugalisation, cumuls), PCH (5 elements, plafonds), RQTH (avantages emploi, protection), CMI (3 types), pension invalidite (3 categories, cumul AAH), maladies invalidantes (14 pathologies, strategie dossier), voies de recours (RAPO obligatoire, contentieux), orientation professionnelle (milieu ordinaire, ESAT, CRP)
- `detect_mdph_context()` : detection automatique par mots-cles avec 7 types de retour (aah, pch, rqth, cmi, invalidite, maladie_invalidante, general)
- `get_mdph_context()` : injection contextuelle adaptee au type de demande detecte
- Integration non bloquante dans `strategiia.py` et `dossier_express.py` (meme pattern que contestation_knowledge)
- 25/25 tests PASS, zero regression sur contestation_knowledge et assurance_knowledge
- Articles de reference : L.821-1 CSS (AAH), L.245-1 CASF (PCH), L.5213-1 CT (RQTH), L.341-1 CSS (invalidite), R.241-33 CASF (silence vaut rejet MDPH)

### Pack Patterns MDPH Premium v1 (05/04/2026)
- **26 patterns MDPH** injectes dans `seed_patterns.py` et MongoDB (`source_type: seed_mdph_v1`)
- Repartition : blocage(7), vigilance(6), levier(5), erreur_frequente(4), piece_manquante(4)
- Sous-familles couvertes : aah_rsdae(4), rqth_emploi(3), pch_aides(2), maladie_invalidante(2), aah_taux_80(1), cmi_mobilite(1), refus_mdph(1) + 12 patterns transversaux
- Blocages principaux : probatoire, traduction_fonctionnelle, medical, qualification
- `seed_mdph_patterns()` : injection incrementale idempotente (skip si deja en base)
- Endpoint admin : `POST /api/knowledge-patterns/seed-mdph`
- Moteur de scoring existant inchangé — les patterns MDPH sont selectionnes automatiquement quand `type_dossier = demande_mdph`
- Anti-hallucination : formulations conditionnelles strictes ("ce type de dossier est souvent fragilise lorsque...")
- 22/22 tests PASS (testing agent iteration 170), zero regression AT/assurance/contestation
- **ZERO modification** : pdf.py, frontend, prompts USER, workflows, payments

### Protection Anti-Copie Premium (05/04/2026)
- **Hook** : `/app/frontend/src/hooks/useContentProtection.js` — centralisé, activable/désactivable par route
- **CSS** : `body.content-protected` dans `index.css` — `user-select: none` ciblé, inputs/textarea/select/boutons préservés
- **Intégration** : `ContentProtectionGuard` dans `App.js` (enfant de BrowserRouter)
- **Pages protégées** : `/`, `/a-propos`, `/accompagnements`, `/expertise-medicale`, `/mdph`, `/seminaires`, `/entreprises`, `/protection-juridique`, `/tarifs`, `/partenaires`, `/avis`, `/ressources`, `/medecin-conseil`
- **Pages NON protégées** : `/contact`, `/admin`, `/dossier-express`, `/espace-client`, `/forum`, `/simulateur`, `/calculatrice`, `/mentions-legales`, `/politique-confidentialite`, `/parrainage`, `/agenda`
- **Protections actives** : clic droit, sélection texte, copier/couper, drag images, Ctrl+C/U/S/P, F12, Ctrl+Shift+I/J/C
- **Toast discret** : "Contenu protégé" (max 1x/8s, supprimé sur mobile)
- 21/21 tests PASS (testing agent iteration 172), zero régression frontend

### GEL OFFICIEL — MOTEUR IA V1 VALIDE (05/04/2026)
- **Document de reference** : `/app/memory/IA_BASELINE_V1.md`
- **Commentaires de gel** injectes dans 9 fichiers critiques (prompts.py, llm.py, chatbot.py, quality_scoring.py, assurance_knowledge.py, contestation_knowledge.py, mdph_knowledge.py, seed_patterns.py, knowledge_patterns.py)
- **Hash MD5 de reference** des prompts geles :
  - STRATEGIIA_BASIC_PROMPT : 8ac30044d1c9
  - STRATEGIIA_PREMIUM_PROMPT : 994491b627fb
  - DOSSIER_EXPRESS_PROMPT : b676aa1ceebe
  - STRATEGIIA_SYSTEM_COMPACT : d53d54d48b99
  - DOSSIER_EXPRESS_SYSTEM_PROMPT : 371e5478b1ac
- **Protocole de future evolution** documente dans IA_BASELINE_V1.md (5 etapes obligatoires)
- 36/37 tests PASS (testing agent iteration 171), zero regression, zero modification fonctionnelle

## Animations blocs flottants (VALIDÉ — NE PAS MODIFIER)
- Fichier : `/app/frontend/src/pages/HomePage.jsx` (style tag en fin de `<main>`)
- `heroPulse` : respiration glow doré (box-shadow + border-color, 3s, permanent)
- `heroFloat` : oscillation verticale 4px (margin-top + margin-bottom, 3s, permanent)
- `heroWave` : vague hover desktop (translate standalone, 2s, hover only)
- Classe : `hero-bloc-wave` sur les 3 blocs de la Section 2
- margin-bottom utilisé pour le bloc Orientation (positionné via `bottom`, pas `top`)
- VALIDÉ sur Samsung Internet mobile + desktop

## P1 — À venir
- Checklist lancement live (clés Stripe/Anthropic production)
- Fournir identifiants AWS S3 (stockage documents persistant)
- Enrichir la base assurantielle avec de nouveaux contrats

## P2 — Backlog
- Intégration HubSpot CRM (en attente identifiants)
- Google Analytics / Plausible
- Finalisation contenu juridique
- Vérification domaine Resend
- Fix chatbot hallucinations (attente infos factuelles S.E.S.)

## Suggestions gardées pour plus tard
- **Accès Professionnel B2B** — Système à 3 niveaux (Client / Pro / Admin). Dashboard Pro dédié, rapports en marque blanche, tarif mensuel.
- **Amélioration OCR** — Google Vision API pour PDF scannés/photos.
- **Enrichir le prompt chatbot** — Ajouter faits réels sur S.E.S pour éviter hallucinations.

## Identifiants de test
- Admin: admin@accompagn-sante.fr / Admin2024!
- Client: demo@test.com / Password123!

## Règles strictes
- ZONE GELÉE sur le Hero : aucune modification sans commande explicite
- ZONE GELÉE sur le ChatBot mobile : bouton intégré dans le flex "Besoin urgent ?" de `HomePage.jsx` (ligne avec `data-testid="hero-chatbot-trigger"`), caché sur desktop (`sm:hidden`). Desktop : FAB global dans `ChatBot.jsx` (`fixed bottom-6 right-4`). VERROUILLÉ le 04/04/2026. INTERDICTION ABSOLUE de modifier le positionnement mobile du chatbot sans ordre explicite du responsable. Aucun agent Emergent ne doit prendre cette liberté.
- Animations blocs flottants : VALIDÉES, ne pas modifier
- Pas de refactoring opportuniste
- PDF : toujours LiberationSans (pas Helvetica)
- Blob downloads : toujours fetch() (pas axios)
- FAQ : champ `reponse` (sans accent) dans l'API
- Format de rapport obligatoire pour chaque fix UI
