# PRD — Strategie & Expertise Sante

## Enonce du probleme
Application web complete en francais pour fournir des conseils sur les maladies professionnelles, accidents du travail et litiges assurantiels.

## Architecture
- **Frontend:** React + Shadcn/UI + Tailwind CSS + Recharts
- **Backend:** FastAPI + MongoDB
- **Theme:** Warm neutral noir/or (Manrope + Playfair Display)

## Entonnoir de Conversion (Mar 2026) — DONE
- **Chatbot** : Réponses utiles mais volontairement incomplètes, ouverture systématique vers StratégiIA/Dossier Express
- **Prompt Light** : Questions simples, sans tableaux MP, réponse rapide
- **Prompt Full** : Questions complexes/médicales, avec tableaux MP, toujours limitée
- **CTA Visuels** : Boutons "Analyse complète avec StratégiIA" + "Dossier Express 97€" après chaque réponse IA
- Flow: Chatbot attire → StratégiIA convertit → Dossier Express monétise

## Page d'Accueil — Refonte (Mar 2026) — DONE
Hero premium sombre avec overlay, titre "accident du travail ou maladie professionnelle" en doré. Risques, Méthode S.E.S, Solutions, Confiance, Chiffres, Fondateur, Médecin Conseil, Témoignages, CTA

## Header — Refonte Premium (Mar 2026) — DONE
Fond sombre #0a0a08, navigation épurée mais complète: À propos, Accompagnements▾ (6 sous-pages), Outils▾ (11 sous-pages dont Simulateur, Calculatrice IPP/AAH, Ressources, Forum, etc.), StratégiIA (ouvre le modal d'analyse), Tarifs, Dossier Express IA. CTA "Réserver un appel" doré à droite. Menu mobile avec sections dépliables.

## Chatbot Mascotte Straté (Mar 2026) — DONE
Bouton robot SVG noir/or, bulle texte "StratégiIA — Je vous aide à analyser votre situation", animation pulse, apparition après 2.5s, indicateur online vert.

## Page Medecin Conseil (Mar 2026) — DONE
Page stratégique SEO/conversion avec tracking clics/vues

## Mascotte Strate (Mar 2026) — DONE
Bulle pulsante, texte noir lisible, TTS français, CRUD Admin + Stats

## Chatbot IA Expert (Mar 2026) — DONE
Animation d'attente enrichie, prompt optimisé, entonnoir conversion

## Recherche IA (Mar 2026) — DONE
Barre → IA chatbot + suggestions Algolia

## Tracking Conversions (Mar 2026) — DONE
/api/tracking/event + /api/tracking/stats

## Taches a venir
- **P1:** Dashboard admin pour stats tracking/conversions
- **P1:** Activer les paiements en production (Stripe/PayPal)
- **P2:** Intégration HubSpot (en attente de credentials)
- **P2:** Audit logging complet
- **P3:** Finalisation du contenu légal
- **P3:** Refactoring EmailTemplateEditor.jsx

## Integrations 3rd party
- Stripe (test), PayPal (test), Claude Sonnet 4.5 (Emergent LLM Key), Resend (sandbox), Algolia Search, HubSpot (attente)
