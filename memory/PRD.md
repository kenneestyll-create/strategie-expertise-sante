# Stratégie & Expertise Santé (S.E.S) — PRD

## Problème original
Application web premium de conseil en maladies professionnelles. Objectifs : scanner de documents fiable, contenu stratégique (IP/PGPF), mascotte IA "Straté" avec TTS et gestion Admin, dashboard Admin complet.

## Architecture
- Frontend: React + Tailwind CSS + Shadcn/UI
- Backend: FastAPI + MongoDB
- Intégrations: Anthropic Claude (clé API native), Stripe (test), Resend (sandbox), AWS S3 (ses-documents-prod)

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

### Case Outcome Memory — V2 Preparation (05/04/2026)
- **Module** : `/app/backend/utils/case_outcome_memory.py` — collecte silencieuse, non bloquante
- **Collection MongoDB** : `case_outcomes` — enregistrements anonymises (blocages, pieces_manquantes, leviers, familles, complexite)
- **Extraction** : keyword-based (pas de LLM), 5 dictionnaires de detection (BLOCAGE, PIECE, LEVIER, FAMILLE)
- **Injection** : `strategiia.py` et `dossier_express.py` — try/except non bloquant, après quality scoring
- **RGPD** : respect strict de `improvement_optout` (pas de stockage si True)
- **Admin** : `GET /api/knowledge-patterns/case-outcomes/stats` — statistiques agregees admin-only
- **AUCUN affichage client** — aucune modification frontend, PDF ou prompts
- 27/27 tests PASS (testing agent iteration 173)

### GEL OFFICIEL — MOTEUR IA V1 VALIDE (05/04/2026)
- **Document de reference** : `/app/memory/IA_BASELINE_V1.md`
- **Commentaires IP + gel** dans 9 fichiers : prompts.py, llm.py, chatbot.py, quality_scoring.py, assurance_knowledge.py, contestation_knowledge.py, mdph_knowledge.py, seed_patterns.py, knowledge_patterns.py
- **Registre empreintes SHA-256** : 9 prompts traces dans IA_BASELINE_V1.md section H
- **Clause propriete intellectuelle** : documentee section G de IA_BASELINE_V1.md
- **Protocole de modification** : 6 etapes obligatoires documentees section I
- Verification integrite 9/9 prompts INTACTS apres marquage IP
- 36/37 tests PASS (iteration 171), zero regression, zero modification fonctionnelle

## Animations blocs flottants (VALIDÉ — NE PAS MODIFIER)
- Fichier : `/app/frontend/src/pages/HomePage.jsx` (style tag en fin de `<main>`)
- `heroPulse` : respiration glow doré (box-shadow + border-color, 3s, permanent)
- `heroFloat` : oscillation verticale 4px (margin-top + margin-bottom, 3s, permanent)
- `heroWave` : vague hover desktop (translate standalone, 2s, hover only)
- Classe : `hero-bloc-wave` sur les 3 blocs de la Section 2
- margin-bottom utilisé pour le bloc Orientation (positionné via `bottom`, pas `top`)
- VALIDÉ sur Samsung Internet mobile + desktop

## Completé récemment
- **Fix : CTA Tarifs "Première consultation gratuite" → Agenda Découverte** — DONE (11/04/2026)
  - Bug : le CTA "Nous contacter" redirigeait vers `/contact` (formulaire générique) au lieu de `/agenda` avec Appel Découverte
  - Correction : lien changé vers `/agenda?type=decouverte`, texte changé en "Réserver mon appel gratuit"
  - AgendaPage : lecture du param `type=decouverte` → pré-sélection automatique de l'Appel Découverte + nettoyage URL
  - 2 fichiers modifiés (TarifsPage.jsx ligne 578, AgendaPage.jsx useEffect), zéro régression
  - Testé pratiquement : clic CTA → page Agenda avec calendrier + "Appel Découverte 10 min — Gratuit" pré-sélectionné

- **Fix : Scanner de documents — Worker manquant** — DONE (11/04/2026)
  - Bug : `Uncaught SyntaxError: Unexpected token '<'` + "Initialisation du scanner..." en boucle infinie
  - Cause : fichier `/workers/scanner.worker.js` inexistant, le serveur renvoyait du HTML
  - Correction chirurgicale : création de `scanner.worker.js` (OffscreenCanvas, filtres N&B/Contraste+, rotation, multi-pages)
  - 1 fichier créé, 0 fichier modifié, zéro régression
  - Badge passe de "Initialisation du scanner..." (bloqué) à "Mode avancé — filtres, rotation, multi-pages" (vert)
  - Testé pratiquement : Worker `ready` signal reçu, scanner ouvert sans erreur console

- **Fix : Paiement Stripe obligatoire avant demande urgente** — DONE (11/04/2026)
  - Défaut identifié : le modal "Besoin urgent ?" enregistrait la demande SANS paiement malgré les prix affichés (50€/80€)
  - Correction : flux Stripe Checkout obligatoire avant enregistrement
  - Endpoints : `POST /api/alerte-urgente` (crée alerte pending + session Stripe), `GET /api/alerte-urgente/confirm-payment/{session_id}` (confirme après paiement), `DELETE /api/alerte-urgente/cancel/{alert_id}` (annulation)
  - Frontend : bouton "Payer et envoyer ma demande (50€/80€)", mention "Paiement sécurisé par Stripe", icône CreditCard, message de garantie conditionné au paiement
  - Écran récapitulatif avant paiement : formule, nom, tél, email, message, total à payer, bouton "Confirmer et payer", lien "Modifier ma demande" (retour au formulaire avec champs conservés)
  - Notification admin envoyée UNIQUEMENT après paiement confirmé
  - Note : nécessite clé Stripe réelle pour fonctionner en production
  - 100% testé (12/12 backend + frontend — iteration 184), zéro régression

- **Rapport hebdomadaire automatique par email** — DONE (09/04/2026)
  - Backend : 4 endpoints (`/api/weekly-report/config` GET/PUT, `/preview` GET, `/send` POST)
  - Données agrégées : contacts, analyses, dossiers, clients, chatbot, RDV, revenus, conversion, stockage S3, alertes S3, état V2
  - Scheduler backend : vérifie chaque heure, envoie max 1 rapport/jour au jour/heure configuré
  - Email HTML premium : branding S.E.S. (header noir, accent doré #C9A84C), tableau de métriques
  - Frontend Admin (Config tab) : carte "Rapport hebdomadaire" avec toggle, sélecteurs jour/heure, email, prévisualisation (8 cartes métriques), envoi manuel
  - Collection MongoDB : `weekly_report_history` (historique des envois, trigger auto/manual)
  - 100% testé (10/10 backend + frontend intégral — iteration 183), zéro régression

- **Système d'alertes de stockage S3** — DONE (09/04/2026)
  - Backend : 3 endpoints (`/api/documents/storage-alerts/config` GET/PUT, `/check` GET)
  - Config persistante MongoDB : seuils 500 Mo, 1 Go, 5 Go (activables individuellement), toggle global
  - Vérification automatique : statut ok/warning (≥80%)/exceeded par seuil
  - Historique alertes : `storage_alert_history` (1 alerte/jour max si seuil dépassé)
  - Frontend : carte "Alertes de stockage" avec toggle, barres de progression colorées (vert/orange/rouge), badges seuils cliquables, messages contextuels
  - 100% testé (11/11 backend + frontend intégral — iteration 182), zéro régression

- **Tableau de bord S3 + Mise à jour tutoriel admin** — DONE (09/04/2026)
  - Backend : endpoint `GET /api/documents/timeline` (uploads/jour, volume, types sur N jours)
  - Frontend : AreaChart "Uploads par jour" (30j), carte "Volume stocké" (Ko/Mo/Go auto), PieChart "Par type de fichier"
  - Onboarding tour : étape 7/10 "Documents stockés (S3)" ajoutée (cible `s3-documents-section`)
  - AdminHelpPanel : section Documents enrichie (5 étapes détaillées : documents clients, S3, Voir/Télécharger, tableau de bord, actualiser)
  - 100% testé (10/11 backend + frontend intégral — iteration 181), zéro régression

- **Intégration AWS S3 — Stockage persistant documents** — DONE (09/04/2026)
  - Backend : `utils/storage.py` (boto3), `upload.py` (chunking + S3), endpoints admin S3
  - Endpoints : GET `/api/documents` (liste paginée), GET `/api/documents/stats`, GET `/api/documents/{id}/url` (pre-signed URL)
  - Frontend : Onglet Documents enrichi avec section "Documents stockés (S3)" — stats, tableau, Voir/Télécharger
  - Bucket : `ses-documents-prod` (eu-west-3), accès public bloqué
  - Collection MongoDB : `documents` (metadata + storage_path)
  - 100% testé (13/13 backend + frontend intégral — iteration 180)
  - Zero régression

- **Alignement juridique discret (KAPSULES KORPORATION / Kbis)** — DONE (09/04/2026)
  - Mentions legales : identite complete (EI, RCS 824 339 584 Chartres, 4 Rue de la Corne du Parc 28310, resp. Laetitia GUSTAVE)
  - CGU Article 1 : identite exploitant ajoutee
  - Politique de confidentialite : responsable du traitement identifie
  - Footer : ligne juridique discrète (10px, opacity 20%)
  - Emails : mention "Service exploité par KAPSULES KORPORATION" en pied de mail (9px)
  - KAPSULES KORPORATION visible UNIQUEMENT dans les zones juridiquement necessaires
  - Placeholders conserves pour : hebergeur, TVA intracommunautaire

- **Systeme telephonique structure + paiement avant reservation** — DONE (09/04/2026)
  - 3 types d'appels : Decouverte (gratuit, 10min, 09h00/09h15, 1 seul par personne), Conseil (75€, 30min, 14h-16h30, Stripe obligatoire), Urgence (modal existante preservee)
  - Horaires : Lun-Ven 9h-17h uniquement (week-ends/soirs bloques)
  - Paiement Stripe avant confirmation (creneaux pending auto-expires apres 15min)
  - Garde-fous : 1 decouverte/email, appels payants rejetes sans checkout, conflit creneaux gere
  - UI premium : 3 cartes, calendrier, creneaux filtres, formulaire, recap, flux Stripe
  - Webhook Stripe mis a jour pour confirmer bookings payes
  - Note : Cle Stripe placeholder (sk_test_emergent) — necessite cle reelle pour production
  - 100% teste (11/11 backend + frontend integral — iteration 179)

- **GEL OFFICIEL DEFINITIF — HOME / RESPONSIVE / HERO** — ENREGISTRE (07/04/2026)
  - Rendu valide definitivement sur mobile, portable, desktop grand ecran
  - Perimetre gele : Hero, structure Home, containers, espacements, responsive, proportions image
  - Documentation mise a jour : ZONES_GELEES_ET_MODIFIABLES.md (section A.8)
  - AUCUNE modification visuelle autorisee sauf bug reel bloquant

- **Harmonisation Desktop Grand Ecran** — DONE (07/04/2026)
  - Hero : centrage vertical flex + max-width 1440px + image aspect-ratio 3/4 sur grands ecrans
  - Sections globales : containers elargis (max-w-7xl→1440px, max-w-6xl→1344px, max-w-5xl→1152px)
  - Media query ciblée : `(min-width: 1024px) and (min-height: 900px)` — zero impact portable/mobile
  - Verifie par screenshots : 1920x1080, 1366x650, 390x844

- **MISSION FINALE — Feedback Dossier Express + Synthese Intelligente** — DONE (06/04/2026)
  - Widget StrategicFeedback etendu a l'Espace Client (dossiers avec statut `termine` uniquement)
  - Endpoint GET `/api/feedback/synthesis` (admin-only) : aggregation rule-based des feedbacks
  - Synthese structuree : Top irritants, besoins non couverts, analyse clarte, signaux forts vs bruit, recommandations strategiques auto-generees
  - Seuil signal fort dynamique : max(2, 15% du total)
  - UI Admin "Synthese Intelligente" avec bouton Generer, barre clarte visuelle, badges signal fort/bruit, verbatims
  - 100% teste (8/8 backend + frontend integral — iteration 178)
  - Zero regression, zero impact parcours client existant

- **Admin V2 Readiness Status (Feu tricolore)** — DONE (06/04/2026)
- **Systeme de retour d'experience strategique** — DONE (06/04/2026)
- **V2 Predictive Dormante preinstallee** — DONE (06/04/2026)
- **Kit d'Independance Projet** — DONE (06/04/2026)
- **Historique hebdomadaire du score V2** — DONE (06/04/2026)
- **Mise à jour tutoriel admin** — DONE (06/04/2026)

## P1 — À venir
- **GEL REEL DU PRODUIT** — MISSION FINALE completee. Aucun nouveau module ou feature.
- Checklist lancement live (clés Stripe/Anthropic production)
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
