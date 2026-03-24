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

## Optimisation Mobile Complete (Mar 2026) — DONE
- 100dvh fallback pour Safari iOS (min-h-screen-safe)
- Safe area inset (env(safe-area-inset-bottom)) sur tous les elements flottants
- Input font-size min 16px pour eviter zoom iOS
- ChatBot plein ecran sur mobile (inset-0), positionne sur desktop
- Menu mobile fond opaque (bg-[#0a0a08])
- Hero responsive: titres adaptatifs (text-2xl -> text-5xl), boutons full-width
- Bandeau Dossier Express responsive avec CTA full-width mobile
- Footer formulaire partenaire en colonne simple sur mobile
- Pas de debordement horizontal (overflow-x: hidden + layouts flex)
- Teste sur 320px, 375px, 412px — 100% PASS

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
