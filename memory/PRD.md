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
- Cachee sur /admin pages
- Bulle auto-show apres 3s (sessionStorage)
- Conseils depuis la base de donnees via `/api/conseils/today` (rotation deterministe + priorite)
- TTS: speakFrench() avec getVoices(), filtre fr-FR, onvoiceschanged
- Tracking deduplique: localStorage par conseil_id + date (1 vue/jour/conseil)
- Tracking clics: POST /api/conseils/click avec conseil_id
- Conversion tracking: export `trackStrateConversion(action)` pour Dossier Express, paiements, etc.
- Tests: 16/16 backend + 100% frontend (iteration 91)

## Admin Conseils Strate (Mar 2026)
- Composant: `/app/frontend/src/components/AdminConseilsStrate.jsx`
- Onglet "Strate" dans AdminDashboard (position 8)
- 5 KPIs globaux: Total, Actifs, Vues, Clics, Taux de clic
- Sous-onglets: "Gestion des conseils" / "Statistiques"
- CRUD complet: creer, modifier, supprimer des conseils
- "Mettre en avant aujourd'hui" (priority override)
- Colonne CTR par conseil dans le tableau
- Dates debut/fin pour planifier les conseils
- Preview TTS depuis le tableau et le formulaire
- Recherche + filtre par categorie
- 30 conseils seeds automatiques

## Statistiques Strate (Mar 2026)
- Collection: `strate_daily_stats` { conseil_id, category, date, views, clicks, conversions }
- Collection: `strate_conversions` { conseil_id, action, date, timestamp }
- Endpoint: `GET /api/conseils/admin/analytics?period=7d|30d&category=all|{cat}`
- Retourne: topConseils (Top 10), totals (views, clicks, conversions, ctr), timeseries, categories
- Dashboard admin:
  - 4 KPIs periode (vues, clics, taux, conversions)
  - Graphique courbe AreaChart (vues + clics par jour)
  - Graphique barres BarChart (performance par categorie)
  - Tableau Top 10 avec taux de clic colore
  - Filtres: periode (7j/30j) + categorie
- Tests: 16/16 backend + 100% frontend (iteration 91)

## Contenu IP & PGPF (Mar 2026)
- 2 sections completes (definition, criteres, justificatifs, exemples, disclaimer)
- Integre dans: Ressources, Calculatrice IPP, Recherche, StrategiIA, AT page, Glossaire

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
