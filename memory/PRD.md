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
- Admin > Guide interactif flottant avec recherche (15 sections documentées, Ctrl+H) — DONE (01/04/2026)
- Clé API Anthropic native configurée — DONE (01/04/2026)
- Chatbot optimisé sur claude-haiku-4-5 (coûts réduits) — DONE (01/04/2026)
- Montant AAH mis à jour : 1 041,59 € (avril 2026) — DONE (01/04/2026)
- Texte Dossier Express IA corrigé (remplacé "StratégiIA" par "Dossier Express IA") — DONE (01/04/2026)
- Compteur "dossiers analysés cette semaine" modifiable depuis Admin > Config — DONE (02/04/2026)
- Section "Chiffres du site" regroupée dans Admin > Config (Hero + Dossiers) — DONE (02/04/2026)
- Tarifs & Promotions modifiables depuis Admin > Config (9 forfaits, prix + badge promo) — DONE (02/04/2026)
- Le défi en chiffres modifiable depuis Admin > Config (4 stats clés page accueil) — DONE (02/04/2026)
- Bug PDF Unicode résolu (police LiberationSans TTF) — DONE (02/04/2026)
- Bug PDF fallback analyse résolu (recherche par email) — DONE (02/04/2026)
- Prompt IA : suppression des recommandations commerciales — DONE (02/04/2026)
- Temps d'attente StratégiIA : "10-15s" → "jusqu'à 2 minutes" — DONE (02/04/2026)
- Label conditionnel : "pré-analyse" (gratuit) vs "analyse" (premium) — DONE (02/04/2026)
- Bordure gauche textarea Firefox (Dossier Express) corrigée — DONE (02/04/2026)
- Téléchargement PDF admin : axios → fetch natif (fix erreur Emergent script) — DONE (02/04/2026)

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
