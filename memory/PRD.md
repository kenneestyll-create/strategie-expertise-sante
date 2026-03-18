# PRD — Strategie & Expertise Sante

## Enonce du probleme
Application web complete en francais pour fournir des conseils sur les maladies professionnelles et les litiges d'assurance.

## Architecture
- **Frontend:** React + Shadcn/UI + Tailwind CSS + Recharts
- **Backend:** FastAPI + MongoDB
- **Theme:** Warm neutral (Manrope + Playfair Display)
- **Integrations:** Stripe (test), PayPal (test), Claude Sonnet 4.5 (Emergent LLM Key), Resend (sandbox), apscheduler, fpdf2, slowapi

## Scanner Documents (Mar 2026)
- **Architecture:** Worker OffscreenCanvas stateful + Hook fonctionnel simple
- **Camera:** `getUserMedia({ video: { facingMode } })` — resolution native de la camera (4:3), champ de vision complet
- **Affichage:** `object-fit: contain` — vue complete sans zoom/crop, fond noir
- **Worker:** scan, filter (bw/enhanced/original), rotate, save — 3.4 Ko leger
- **Auto-crop:** SUPPRIME (utilisateur a demande sa suppression)
- **Cache-busting:** `?v=${Date.now()}` sur l'URL du worker

## Taches a venir
- **P1:** Activer les paiements en production (Stripe/PayPal)
- **P2:** Integration HubSpot (en attente de credentials)
- **P2:** Audit logging complet
- **P3:** Finalisation du contenu legal
- **P3:** Refactoring EmailTemplateEditor.jsx

## Integrations 3rd party
- Stripe (test mode)
- PayPal (test mode)
- Claude Sonnet 4.5 (Emergent LLM Key)
- Resend (sandbox)
- HubSpot (partiellement, en attente credentials)
