# Stratégie & Expertise Santé (S.E.S) — PRD

## Problème original
Application web premium de conseil en maladies professionnelles. Objectifs : scanner de documents fiable, contenu stratégique (IP/PGPF), mascotte IA "Straté" avec TTS et gestion Admin.

## Architecture
- Frontend: React + Tailwind CSS + Shadcn/UI
- Backend: FastAPI + MongoDB
- Intégrations: Anthropic Claude (Emergent LLM Key), Stripe (test), Resend (sandbox)

## Ce qui est implémenté
- Scanner de documents natif (caméra mobile `<input capture>`) — DONE
- Contenu stratégique IP & PGPF intégré (Ressources, Calculateur, Recherche, IA) — DONE
- Mascotte Straté visuelle (composant flottant) — DONE
- Hero section avec image parisienne (Tour Eiffel) — DONE (validé 01/04/2026)
- Bloc Documents décalé droite sur section 2 — DONE (validé 01/04/2026)
- Frontend Freeze : layout-guardrails.css + 115 baselines Playwright — DONE
- Hero déclaré ZONE GELÉE — DONE
- Admin > Config > Compteur Hero (personnes accompagnées, modifiable) — DONE (01/04/2026)

## Image Hero
- Image éditée via OpenAI GPT Image 1 (édition de l'image originale, fond NYC → Paris)
- Fichier : `/app/frontend/public/hero_paris_edited.png`
- Utilisée ligne 310 (Hero) et ligne 414 (Section 2) de HomePage.jsx

## P0 — En attente
1. Bug TTS Mascotte Straté : voix lit en anglais au lieu de français
2. Backend CRUD `/api/conseils` + Admin UI pour les tips Straté

## P1 — À venir
- Checklist lancement live (clés Stripe/Anthropic production)
- Intégration HubSpot CRM (en attente identifiants utilisateur)

## P2 — Backlog
- Lien S3 PDF cassé (en attente identifiants AWS)
- Finalisation contenu juridique
- Refactoring EmailTemplateEditor.jsx

## Identifiants de test
- Admin: admin@accompagn-sante.fr / Admin2024!
- Client: demo@test.com / Password123!

## Règles strictes
- ZONE GELÉE sur le Hero : aucune modification sans commande explicite
- Pas de refactoring opportuniste
- Format de rapport obligatoire pour chaque fix UI
