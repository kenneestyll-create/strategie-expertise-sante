# PRD — Strategie & Expertise Sante

## Enonce du probleme
Application web complete en francais pour fournir des conseils sur les maladies professionnelles, accidents du travail et litiges assurantiels.

## Architecture
- **Frontend:** React + Shadcn/UI + Tailwind CSS + Recharts
- **Backend:** FastAPI + MongoDB
- **Theme:** Warm neutral noir/or (Manrope + Playfair Display)
- **Integrations:** Stripe (test), PayPal (test), Claude Sonnet 4.5 (Emergent LLM Key), Resend (sandbox)

## Mascotte "Strate" (Mar 2026)
- Composant: `/app/frontend/src/components/MascotteStrate.jsx`
- Design: trombone SVG avec bouclier, style noir/or
- Position: fixed bottom-7.5rem right-1.5rem (au-dessus ChatBot)
- Bulle auto-show apres 3s (sessionStorage)
- **Conseils depuis la base de donnees** via `/api/conseils/today` (rotation deterministe + priorite)
- **TTS: speakFrench() avec getVoices(), filtre fr-FR, onvoiceschanged** — CORRIGE
- Bouton action dynamique vers page pertinente + tracking clics
- Disclaimer juridique obligatoire
- Tests: 16/16 backend + 100% frontend (iteration 90)

## Admin Conseils Strate (Mar 2026)
- Composant: `/app/frontend/src/components/AdminConseilsStrate.jsx`
- Onglet "Strate" dans AdminDashboard (position 8)
- CRUD complet: creer, modifier, supprimer des conseils
- "Mettre en avant aujourd'hui" (priority override)
- Dates debut/fin pour planifier les conseils
- Preview TTS depuis le tableau et le formulaire
- KPIs: total, actifs, vues, clics
- Recherche + filtre par categorie
- 30 conseils seeds automatiques

## Contenu IP & PGPF (Mar 2026)
- 2 sections completes (definition, criteres, justificatifs, exemples, disclaimer)
- Integre dans: Ressources, Calculatrice IPP, Recherche, StrategiIA, AT page, Glossaire
- Tests: 12/12 passes (iteration 88)

## Scanner Documents (Mar 2026)
- Appareil photo natif (`<input capture="environment">`)
- Worker OffscreenCanvas (filtres, rotation, multi-pages, PDF)

## Taches a venir
- **P1:** Activer les paiements en production (Stripe/PayPal)
- **P2:** Integration HubSpot (en attente de credentials)
- **P2:** Audit logging complet
- **P3:** Finalisation du contenu legal
- **P3:** Refactoring EmailTemplateEditor.jsx

## Integrations 3rd party
- Stripe (test mode), PayPal (test mode)
- Claude Sonnet 4.5 (Emergent LLM Key)
- Resend (sandbox)
- HubSpot (partiellement, en attente credentials)
