# PRD — Strategie & Expertise Sante

## Enonce du probleme
Application web complete en francais pour fournir des conseils sur les maladies professionnelles, accidents du travail et litiges assurantiels.

## Architecture
- **Frontend:** React + Shadcn/UI + Tailwind CSS + Recharts
- **Backend:** FastAPI + MongoDB
- **Theme:** Warm neutral noir/or (Manrope + Playfair Display)

## Page d'Accueil — Refonte Conversion (Mar 2026) — DONE
Structure de la page:
1. **HERO** - Centré, noir & or, Playfair Display, titre empathique AT/MP
2. **Dossier Express Banner** - Urgence, 97€, livré sous 2h
3. **Section Risques** - 4 risques + accroche dorée + CTA
4. **Méthode S.E.S** - 5 étapes visuelles numérotées
5. **Solutions** - 3 cartes cliquables (Dossier Express, StratégiIA, Accompagnement)
6. **Chiffres clés** - Compteurs animés
7. **Confiance** - 4 points de crédibilité
8. **Fondateur** - Citation avec encadré noir/or
9. **Médecin Conseil** - Section stratégique avec CTA
10. **Témoignages** - 6 anonymisés
11. **Disclaimer** - Légal
12. **CTA Final** - Double bouton (Contacter + Analyser)
- Tests: 100% frontend (iteration 97)

## Page Medecin Conseil (Mar 2026) — DONE
- Page stratégique SEO/conversion: `/medecin-conseil`
- Route, liens Header/Footer/HomePage/ServicesPage/ExpertiseMedicalePage
- CTA Hero + CTA bas + Tracking clics/vues
- Tests: 100% backend + frontend (iteration 96)

## Mascotte Strate (Mar 2026) — DONE
- Bulle pulsante, Badge date rouge, TTS français
- CRUD Admin complet + Stats (Views, Clicks, CTR)

## Chatbot IA Expert (Mar 2026) — DONE
- FAQ restreinte (tarifs, contact) + signaux médicaux → Claude

## Recherche IA (Mar 2026) — DONE
- Barre → IA chatbot + suggestions Algolia

## Tracking Conversions (Mar 2026) — DONE
- `/api/tracking/event` + `/api/tracking/stats`

## Taches a venir
- **P1:** Dashboard admin pour stats tracking/conversions
- **P1:** Activer les paiements en production (Stripe/PayPal)
- **P2:** Intégration HubSpot (en attente de credentials)
- **P2:** Audit logging complet
- **P3:** Finalisation du contenu légal
- **P3:** Refactoring EmailTemplateEditor.jsx

## Integrations 3rd party
- Stripe (test), PayPal (test), Claude Sonnet 4.5 (Emergent LLM Key), Resend (sandbox), Algolia Search, HubSpot (attente)
