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
- Admin > Config > Compteur Hero (personnes accompagnées, modifiable) — DONE
- Admin > Config > Base dossiers hebdomadaire — DONE
- Admin > Config > Le défi en chiffres (4 stats clés) — DONE
- Admin > Config > Tarifs & Promotions (9 forfaits, prix + badge promo) — DONE
- Admin > Guide interactif flottant avec recherche (15 sections, 7 étapes Config, Ctrl+H) — DONE (02/04/2026)
- Admin > Tutoriel interactif d'onboarding Straté (6 étapes, auto 1ère connexion, relançable) — DONE (02/04/2026)
- Clé API Anthropic native configurée — DONE
- Chatbot optimisé sur claude-haiku-4-5 — DONE
- Montant AAH mis à jour : 1 041,59 EUR — DONE
- Bug PDF Unicode résolu (police LiberationSans TTF) — DONE
- Téléchargement PDF admin : axios → fetch natif — DONE
- Bordure gauche textarea Firefox corrigée — DONE

## Tutoriel Onboarding Admin
- Composant : `/app/frontend/src/components/AdminOnboardingTour.jsx`
- 6 étapes : Bienvenue, StratégiIA, Dossier Express, Configuration, Mode Test, Aide & Guide
- Déclenchement automatique 1ère connexion (localStorage `ses_admin_onboarding_done`)
- Relançable via le bouton "Revoir le tutoriel Straté" dans le Help Panel
- Style : mascotte Straté avec bulles de dialogue + spotlight doré

## Image Hero
- Fichier : `/app/frontend/public/hero_paris_edited.png`
- Utilisée dans HomePage.jsx (Hero + Section 2)

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
