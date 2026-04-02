# Stratégie & Expertise Santé (S.E.S) — PRD

## Problème original
Application web premium de conseil en maladies professionnelles. Objectifs : scanner de documents fiable, contenu stratégique (IP/PGPF), mascotte IA "Straté" avec TTS et gestion Admin, dashboard Admin complet.

## Architecture
- Frontend: React + Tailwind CSS + Shadcn/UI
- Backend: FastAPI + MongoDB
- Intégrations: Anthropic Claude (clé API native), Stripe (test), Resend (sandbox)

## Ce qui est implémenté
- Scanner de documents natif (caméra mobile `<input capture>`) — DONE
- Contenu stratégique IP & PGPF intégré (Ressources, Calculateur, Recherche, IA) — DONE
- Mascotte Straté visuelle + TTS français robuste (mobile/desktop) — DONE
- Backend CRUD `/api/conseils` complet (30 conseils, rotation, priorité, tracking, analytics) — DONE
- Admin "Conseils Straté" tab fonctionnel — DONE
- Hero section avec image parisienne (Tour Eiffel) — DONE
- Frontend Freeze : layout-guardrails.css + baselines Playwright — DONE
- Hero déclaré ZONE GELÉE — DONE
- Admin > Config > Compteur Hero — DONE
- Admin > Config > Base dossiers hebdomadaire — DONE
- Admin > Config > Le défi en chiffres — DONE
- Admin > Config > Tarifs & Promotions — DONE
- Admin > Guide interactif flottant (15 sections, 8 étapes Config, Ctrl+H) — DONE (02/04/2026)
- Admin > Tutoriel interactif d'onboarding Straté (6 étapes, auto 1ère connexion, relançable) — DONE (02/04/2026)
- Admin > Statistiques d'engagement du tutoriel (démarrages, complétion, abandon par étape) — DONE (02/04/2026)
- Clé API Anthropic native configurée — DONE
- Chatbot optimisé sur claude-haiku-4-5 — DONE
- Bug PDF Unicode résolu (police LiberationSans TTF) — DONE
- Téléchargement PDF admin : axios → fetch natif — DONE

## Tutoriel Onboarding Admin
- Composant : `/app/frontend/src/components/AdminOnboardingTour.jsx`
- 6 étapes : Bienvenue, StratégiIA, Dossier Express, Configuration, Mode Test, Aide & Guide
- Déclenchement automatique 1ère connexion (localStorage `ses_admin_onboarding_done`)
- Relançable via Help Panel ou widget Config
- Tracking : POST `/api/admin/onboarding/track` (events: start, step, skip, complete)
- Stats : GET `/api/admin/onboarding/stats` (taux complétion, vues par étape)
- Widget stats dans Admin > Config > "Tutoriel Straté"

## P1 — À venir
- Checklist lancement live (clés Stripe/Anthropic production)
- Fournir identifiants AWS S3 (stockage documents persistant)

## P2 — Backlog
- Intégration HubSpot CRM (en attente identifiants)
- Google Analytics / Plausible
- Finalisation contenu juridique
- Vérification domaine Resend

## Identifiants de test
- Admin: admin@accompagn-sante.fr / Admin2024!
- Client: demo@test.com / Password123!

## Règles strictes
- ZONE GELÉE sur le Hero : aucune modification sans commande explicite
- Pas de refactoring opportuniste
- PDF : toujours LiberationSans (pas Helvetica)
- Blob downloads : toujours fetch() (pas axios)
- Format de rapport obligatoire pour chaque fix UI
