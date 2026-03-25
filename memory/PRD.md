# PRD — Strategie & Expertise Sante

## Enonce du probleme
Application web complete en francais pour fournir des conseils sur les maladies professionnelles, accidents du travail et litiges assurantiels.

## Architecture
- **Frontend:** React + Shadcn/UI + Tailwind CSS + Recharts
- **Backend:** FastAPI + MongoDB
- **Theme:** Warm neutral noir/or (Manrope + Playfair Display)

## Entonnoir de Conversion (Mar 2026) — DONE
- **Chatbot** : Reponses utiles mais volontairement incompletes, ouverture systematique vers StrategiIA/Dossier Express
- Flow: Chatbot attire -> StrategiIA convertit -> Dossier Express monetise

## Page d'Accueil — Refonte (Mar 2026) — DONE
Hero premium sombre avec overlay, titre dore, responsive mobile-first

## Header — Refonte Premium (Mar 2026) — DONE
Fond sombre #0a0a08, navigation dropdowns, menu mobile opaque

## StrategiIA — Entonnoir 3 paliers (Mar 2026) — DONE
Palier 1/2/3, async polling, ReactMarkdown, barre de progression animee, option RATP/SNCF
- Options payantes mobile corrigees (Mar 2026): texte non coupe, prix aligne, PdfPreview conditionnel

## Optimisation Mobile Complete (Mar 2026) — DONE
- 100dvh fallback pour Safari iOS
- Safe area inset sur tous les elements flottants
- Input font-size min 16px (anti-zoom iOS)
- ChatBot plein ecran sur mobile
- Menu mobile fond opaque
- Hero responsive: titres adaptatifs, boutons full-width
- Bandeau Dossier Express responsive
- Footer formulaire single column mobile
- Teste sur 320px, 375px, 412px — 100% PASS

## Optimisation Mobile v2 (Mar 2026) — DONE
- Tableau maladies pro: cartes empilees sur mobile (md:hidden), table sur desktop (hidden md:block)
- ResourcesPage: 7 onglets avec wrap responsive (3 rangees sur mobile)
- MentionsLegalesPage: tabs en colonne simple sur mobile (grid-cols-1 sm:grid-cols-3)
- PdfCoverPreview modal: largeur responsive min(340px, calc(100vw-3rem))
- StrategiIA options payantes: flex justify-between, badges whitespace-nowrap, PDF preview conditionnel
- Teste iteration_103 — 100% PASS

## Mascotte Strate (Mar 2026) — DONE
Bulle pulsante, texte noir lisible, TTS francais, CRUD Admin + Stats

## Chatbot IA Expert (Mar 2026) — DONE
Animation d'attente enrichie, prompt optimise, entonnoir conversion

## Recherche IA (Mar 2026) — DONE
Barre -> IA chatbot + suggestions Algolia

## Tracking Conversions (Mar 2026) — DONE
/api/tracking/event + /api/tracking/stats

## Taches a venir
- **P1:** Dashboard admin pour stats tracking/conversions
- **P1:** Activer les paiements en production (Stripe/PayPal)
- **P2:** Integration HubSpot (en attente de credentials)
- **P2:** Audit logging complet
- **P3:** Finalisation du contenu legal
- **P3:** Refactoring EmailTemplateEditor.jsx

## Integrations 3rd party
- Stripe (test), PayPal (test), Claude Sonnet 4.5 (Emergent LLM Key), Resend (sandbox), Algolia Search, HubSpot (attente)
