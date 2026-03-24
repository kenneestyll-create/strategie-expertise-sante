# PRD — Strategie & Expertise Sante

## Enonce du probleme
Application web complete en francais pour fournir des conseils sur les maladies professionnelles, accidents du travail et litiges assurantiels.

## Architecture
- **Frontend:** React + Shadcn/UI + Tailwind CSS + Recharts
- **Backend:** FastAPI + MongoDB
- **Theme:** Warm neutral noir/or (Manrope + Playfair Display)

## Entonnoir de Conversion (Mar 2026) — DONE
- **Chatbot** : Reponses utiles mais volontairement incompletes, ouverture systematique vers StrategiIA/Dossier Express
- **Prompt Light** : Questions simples, sans tableaux MP, reponse rapide
- **Prompt Full** : Questions complexes/medicales, avec tableaux MP, toujours limitee
- **CTA Visuels** : Boutons "Analyse complete avec StrategiIA" + "Dossier Express 97EUR" apres chaque reponse IA
- Flow: Chatbot attire -> StrategiIA convertit -> Dossier Express monetise

## Page d'Accueil — Refonte (Mar 2026) — DONE
Hero premium sombre avec overlay, titre "accident du travail ou maladie professionnelle" en dore. Risques, Methode S.E.S, Solutions, Confiance, Chiffres, Fondateur, Medecin Conseil, Temoignages, CTA

## Header — Refonte Premium (Mar 2026) — DONE
Fond sombre #0a0a08, navigation epuree mais complete: A propos, Accompagnements (6 sous-pages), Outils (11 sous-pages dont Simulateur, Calculatrice IPP/AAH, Ressources, Forum, etc.), StrategiIA (ouvre le modal d'analyse), Tarifs, Dossier Express IA. CTA "Reserver un appel" dore a droite. Menu mobile avec sections depliables.

## StrategiIA — Entonnoir 3 paliers (Mar 2026) — DONE
Palier 1 (gratuit, sans email): 1/3 de l'analyse (resume + droits identifies) avec degrade + CTA email.
Palier 2 (apres email): ~50% (analyse approfondie + demarches) + elements premium verrouilles + CTA 29EUR.
Palier 3 (premium 29EUR): Analyse complete + jurisprudences + score + PDF + strategie detaillee.
Backend async polling (POST /analyze -> job_id, GET /status/{id} polling 3s). Prompt structure avec marqueurs ---SECTION_1/2/3---. ReactMarkdown pour le rendu. Retry 3x. Claude Sonnet 4.5.
- Barre de progression animee avec 4 etapes pendant le chargement (Mar 2026) — DONE
- Option "Regimes speciaux RATP/SNCF" dans le dropdown (Mar 2026) — DONE
- Correction bug syntaxe splitAnalysis duplique (Mar 2026) — DONE

## Page Medecin Conseil (Mar 2026) — DONE
Page strategique SEO/conversion avec tracking clics/vues

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
