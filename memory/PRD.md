# PRD — Strategie & Expertise Sante

## Enonce du probleme
Application web complete en francais pour fournir des conseils sur les maladies professionnelles, accidents du travail et litiges assurantiels.

## Architecture
- **Frontend:** React + Shadcn/UI + Tailwind CSS + Recharts
- **Backend:** FastAPI + MongoDB
- **Theme:** Warm neutral (Manrope + Playfair Display)
- **Integrations:** Stripe (test), PayPal (test), Claude Sonnet 4.5 (Emergent LLM Key), Resend (sandbox)

## Contenu strategique IP & PGPF (Mar 2026)

### Section IP — Incidence Professionnelle
- Definition claire et pedagogique
- 4 criteres : penibilite accrue, devalorisation marche du travail, perte d'opportunites, reconversion
- Justificatifs : rapports medicaux, expertises, attestations employeur, elements de carriere
- 4 exemples concrets d'indemnisation (ouvrier, infirmiere, cadre, technicien agricole)
- Disclaimer obligatoire

### Section PGPF — Perte de Gains Professionnels Futurs
- Definition + nomenclature Dintilhac
- Distinction PGPA vs PGPF
- Methode de calcul en 4 etapes (projection, evolution salariale, impact handicap, capitalisation)
- Justificatifs : bulletins salaire, contrats, evolution previsible, expertises
- 3 cas concrets (salarie, fonctionnaire, independant)
- Disclaimer obligatoire

### Integration globale
- **Ressources** : 2 nouveaux onglets encyclopedie (IP + PGPF)
- **Calculatrice IPP** : encarts explicatifs IP et PGPF avec liens
- **Moteur de recherche** : mots-cles indexes (incidence professionnelle, IP, PGPF, perte de gains futurs, PGPA, Dintilhac)
- **StrategiIA** : prompts IA mis a jour (basic + premium + dossier express) avec evaluation IP/PGPF
- **Page Accident du Travail** : encarts liens vers IP et PGPF
- **Glossaire** : 4 termes ajoutes (IP, PGPF, PGPA, Dintilhac)
- **Tests** : 12/12 passes (iteration 88)

## Scanner Documents (Mar 2026)
- Appareil photo natif (`<input capture="environment">`)
- Worker OffscreenCanvas (filtres, rotation, multi-pages, PDF)
- Auto-crop supprime

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
