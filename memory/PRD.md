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
