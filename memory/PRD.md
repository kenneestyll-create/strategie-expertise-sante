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
- Admin > Config > Compteur visiteurs Hero (auto-incrément par visite) — DONE (02/04/2026)
- Admin > Config > Base dossiers hebdomadaire — DONE
- Admin > Config > Le défi en chiffres — DONE
- Admin > Config > Tarifs & Promotions — DONE
- Admin > Guide interactif flottant (15 sections, 8 étapes Config, Ctrl+H) — DONE
- Admin > Tutoriel interactif d'onboarding Straté (6 étapes) — DONE
- Admin > Statistiques d'engagement du tutoriel — DONE
- Admin > Préparation Production (purge données test + reset compteurs) — DONE (02/04/2026)
- Hero renommé : "personnes accompagnées" → "visiteurs" — DONE (02/04/2026)
- Clé API Anthropic native configurée — DONE
- Chatbot optimisé sur claude-haiku-4-5 — DONE
- Bug PDF Unicode résolu (police LiberationSans TTF) — DONE
- Téléchargement PDF admin : axios → fetch natif — DONE

## Préparation Production
- Panneau dans Admin > Config > "Préparation Production"
- 6 purges individuelles : contacts, StratégiIA, Dossier Express, avis, chatbot, onboarding
- 2 resets compteurs : visiteurs Hero, base dossiers hebdo
- 1 purge complète avec confirmation
- Endpoints : POST `/api/admin/cleanup/{section}`, `/api/admin/cleanup/counter-reset`, `/api/admin/cleanup/full-purge`

## P1 — À venir
- Checklist lancement live (clés Stripe/Anthropic production)
- Fournir identifiants AWS S3 (stockage documents persistant)

## P2 — Backlog
- Intégration HubSpot CRM (en attente identifiants)
- Google Analytics / Plausible
- Finalisation contenu juridique
- Vérification domaine Resend

## Suggestions gardées pour plus tard
- Statistiques d'engagement du tutoriel — IMPLÉMENTÉ, à enrichir si besoin
- **Accès Professionnel B2B** — Système à 3 niveaux (Client / Pro / Admin). Dashboard Pro dédié avec Dossier Express illimité, rapports en marque blanche (logo du pro), tarif mensuel (97-497€/mois). Phase 1 : rôle `pro` + dashboard simplifié. Phase 2 : personnalisation PDF. Phase 3 : facturation Stripe récurrente. Commencer par un partenaire pilote.
- **Amélioration OCR** — Remplacement de Tesseract par Google Vision API pour les PDF scannés/photos. Gain estimé : 72% → 93% de précision. Gratuit jusqu'à 1000 pages/mois. À valider après retours clients réels.
- **Enrichir le prompt chatbot** — Ajouter les faits réels sur S.E.S (fondateur, histoire, mission) pour éviter les hallucinations. Ajouter garde-fou "ne jamais inventer".

## Identifiants de test
- Admin: admin@accompagn-sante.fr / Admin2024!
- Client: demo@test.com / Password123!

## Règles strictes
- ZONE GELÉE sur le Hero : aucune modification sans commande explicite
- Pas de refactoring opportuniste
- PDF : toujours LiberationSans (pas Helvetica)
- Blob downloads : toujours fetch() (pas axios)
- Format de rapport obligatoire pour chaque fix UI
