# PRD — Strategie & Expertise Sante

## Enonce du probleme
Application web complete en francais pour fournir des conseils sur les maladies professionnelles et les litiges d'assurance.

## Architecture
- **Frontend:** React + Shadcn/UI + Tailwind CSS + Recharts
- **Backend:** FastAPI + MongoDB
- **Theme:** Warm neutral (Manrope + Playfair Display)
- **Integrations:** Stripe (test), PayPal (test), Claude Sonnet 4.5 (Emergent LLM Key), Resend (sandbox), apscheduler, fpdf2, slowapi

## Scanner Documents (Mar 2026)
- **Architecture:** Appareil photo natif (`<input capture="environment">`) + Worker OffscreenCanvas
- **Prise de photo:** Utilise l'appareil photo natif du telephone (Samsung Camera, etc.) via `capture="environment"` — qualite maximale, autofocus, HDR
- **Galerie:** Input file sans `capture` — ouvre la galerie pour choisir une photo existante
- **Worker:** scan, filter (bw/enhanced/original), rotate, save — 3.4 Ko leger
- **Modes:** Simple (capture directe) / Avance (filtres, rotation, multi-pages, PDF)
- **Multi-pages:** Strip de pages, navigation, ajout/suppression, fusion PDF
- **Auto-crop:** SUPPRIME

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
