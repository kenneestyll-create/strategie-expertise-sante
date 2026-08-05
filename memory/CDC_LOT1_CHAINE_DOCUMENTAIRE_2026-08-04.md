# Cahier des charges — Lot 1 « Chaîne documentaire transparente » (ÉTUDE, zéro code)
Date : 2026-08-04. Aucune modification effectuée. Décision GO/NO-GO attendue de l'utilisateur.

## 1. AUDIT DE L'EXISTANT (P7) — constats précis dans le code

### Flux actuel (décisif pour le chiffrage)
1. Client paie (Stripe checkout) AVANT tout upload.
2. Retour paiement → formulaire → upload chunké → **extraction = phase séparée** (endpoint /api/upload/extract-chunked + polling extract-status) orchestrée côté client (pdfExtractor.js).
3. Le client appelle ensuite /api/dossier-express/submit avec documents_text + document_details → analyse Claude → PDF → email.
→ CONSÉQUENCE MAJEURE : le « point de pause » entre extraction et analyse EXISTE DÉJÀ. L'écran de contrôle qualité s'insère sans refonte du moteur.

### Réutilisable tel quel
- Par fichier : pages, text_length, status (7 statuts), method, preview — déjà retournés au frontend (`details`).
- Texte extrait DÉJÀ balisé [Page N] (single, chunked, pdfplumber, Tesseract) → socle de la granularité par page ET de la matrice des preuves.
- Gemini marque déjà [illisible] dans le texte.
- pdfplumber : pages lisibles/total (ratio 60 %) ; Tesseract : labels lisible/partiellement/non lisible par page.
- Prompt analyse : sections 2 (pièces détectées), 10 (complétude), robustesse dossiers incomplets — réutilisables pour P4/P5.
- generate_dossier_pdf accepte déjà document_details → le tableau documentaire s'y greffe.
- quality_scoring.py (scoring interne 0-100), notifications admin, object storage.

### À développer (n'existe pas)
- Qualité PAR PAGE exposée (aujourd'hui agrégée par fichier).
- Drapeaux qualité (flou/coupé/vide/manuscrit) — dérivables des signaux existants + Gemini.
- Agrégation en score de confiance + niveaux.
- Écran client contrôle qualité + choix A/B + re-upload ciblé.
- Référentiel pièces attendues par type de dossier + détection pièces manquantes PRÉ-analyse.
- Tableau documentaire en tête de rapport + formulations d'impact (P4).
- Matrice des preuves + validateur programmatique de citations.

### Inutile à développer (déjà présent)
- Progression temps réel granulaire, heartbeats, reprise auto, alertes admin OCR, stockage originaux, découpage extraction/analyse.

## 2. SOUS-FONCTIONNALITÉS (découpage + estimation)

| SF | Contenu | Dev | Coût exploit. | Plus-value | Risques |
|---|---|---|---|---|---|
| SF1 | Qualité par page (backend) : signaux textuels (chars/page, densité [illisible], ratio caractères aberrants) + drapeaux Gemini par page (le prompt d'extraction retourne un mini-bilan JSON par page : lisible/partiel/illisible + cause flou/coupé/vide/manuscrit) | 3-4 j | ~0 € (mêmes appels) | Socle de tout le lot | Calibrage seuils ; +5-10 % tokens sortie Gemini |
| SF2 | Score de confiance : agrégation pondérée → 5 niveaux (Excellent≥97 %, Élevé 90-96, Bon 75-89, Moyen 50-74, Faible <50). Pondération : méthode (natif 1.0 / vision 0.9 / partiel 0.5 / échec 0) × poids type de pièce (expertise/certificat > courrier) × complétude pièces attendues | 1-2 j | 0 € | Transparence, confiance | Afficher niveaux qualitatifs, PAS un % pseudo-précis au lancement |
| SF3 | Écran client post-extraction : synthèse (docs, pages, exploitables/partielles/à remplacer, localisation « Document 3 — pages 7-8 »), Option A remplacer (re-upload ciblé) / Option B continuer (consentement explicite loggé) | 3-4 j | 0 € | Cœur de la demande ; réduit rapports dégradés | Friction post-paiement → ne JAMAIS bloquer, Option B en 1 clic |
| SF4 | Tableau documentaire en tête du rapport PDF + mention d'impact (P4) : formulations graduées automatiques selon nature des pages illisibles et données clés trouvées ailleurs | 2-3 j | 0 € | Rapport auto-documenté | P4 = fiabilité PARTIELLE par nature (voir §4) |
| SF5 | Pièces manquantes PRÉ-analyse : référentiel statique par type (MP/AT/expertise/assurance/MDPH/prévoyance) + classification des docs uploadés (1 appel Gemini Flash) → check-list ✓/⚠ sur l'écran SF3 | 3-4 j | +0,005 € | Évite un rapport sans pièce essentielle | Classification imparfaite → afficher « détecté/non détecté », pas « absent » affirmatif |
| SF6 | Matrice des preuves : le prompt exige pour chaque conclusion majeure (source : document, page, citation) ; VALIDATEUR programmatique post-génération : fuzzy-match de chaque citation contre le texte source balisé [Page N] ; citation non retrouvée → dégradée en « non vérifiée » ou retirée | 4-6 j | ~0 € (code pur) | Différenciant majeur ; anti-hallucination MESURABLE | Reformulations LLM → matching normalisé + règle « guillemets = verbatim » |
| SF7 (option) | Pilote Mistral OCR : benchmark 10 dossiers anonymisés vs Gemini (qualité, coût, confiance/page) | 2-3 j | test ponctuel | Donnée objective coût | RGPD : nouveau sous-traitant données médicales (DPA + politique de confidentialité) ; clé API séparée hors clé universelle |

**Total cœur (SF1→SF6) : 16-23 jours-homme. Coût d'exploitation additionnel : +0,01 à +0,04 €/dossier (négligeable vs 97 €).**

## 3. MÉTHODE DE CALCUL DU SCORE DE CONFIANCE (P3) — recommandée
score = Σ(poids_page × exploitabilité_page) / Σ(poids_page), où :
- exploitabilité_page ∈ {1.0 natif/vision propre ; 0.5 partiel ; 0 illisible/vide}
- poids_page selon la catégorie de la pièce (expertise, certificat, notification = 1.5 ; courriers/annexes = 1.0)
- malus complétude : −1 niveau si pièce essentielle attendue non détectée (lié SF5)
Affichage : « Analyse basée sur : 5 documents, 43 pages — 41 parfaitement exploitables, 2 partiellement lisibles. Niveau de confiance : Élevé. »
Calibrage : v1 = seuils fixes ; recalibrage après 50-100 dossiers via quality_scoring existant.

## 4. FAISABILITÉ P4 (impact des pages illisibles sur les conclusions) — réponse honnête
Fiabilité TOTALE impossible : on ne sait pas ce qu'on ne peut pas lire. Faisable de manière UTILE ET PRUDENTE via heuristique contextuelle :
- la page illisible appartient-elle à une pièce à fort poids (expertise/certificat) ? position (conclusions en fin de rapport d'expertise = pages critiques) ;
- les données clés (dates, taux, garanties) ont-elles été trouvées ailleurs dans le dossier ?
→ 2 formulations graduées automatiques : « Les pages X-Y du document Z appartiennent à [catégorie] : elles peuvent contenir des informations susceptibles de modifier les conclusions » / « Les limitations constatées portent sur des pièces secondaires et n'ont probablement pas d'impact sur les conclusions principales ». Jamais de certitude affirmée. Fiabilité estimée : bonne pour orienter, jamais garantie — à assumer dans la formulation.

## 5. IMPACTS ARCHITECTURE / PERFORMANCE / COÛT (P8)
- Architecture : AUCUNE refonte. Extension du schéma `details` (tableau par page), 1 écran frontend inséré dans le flux existant, extension du prompt d'extraction (bilan par page), post-processeur de rapport (validateur SF6), section PDF. Moteur d'analyse INCHANGÉ.
- Performance : +0 appel OCR (drapeaux dans les mêmes appels) ; SF5 = +1 appel Flash (~2-4 s) ; SF6 validateur = <1 s CPU. Pas de rendu image massif (contrainte pod 512 MB respectée — pas de module OpenCV dédié en v1).
- Coût : +0,01-0,04 €/dossier. Marge intacte.

## 6. PILOTE MISTRAL OCR (P9) — recommandation argumentée : REPORTER
Pour : coût OCR /2 à /5 à volume élevé ; confiance par page native ; benchmark objectif.
Contre (décisif aujourd'hui) : (1) SF1 fournit la confiance par page SANS nouveau fournisseur ; (2) RGPD — nouveau sous-traitant de données médicales = DPA + mise à jour politique de confidentialité ; (3) clé API et facturation séparées (hors clé universelle) ; (4) le goulot identifié est la qualité source, pas le moteur.
→ Déclencheurs de réévaluation : volume > ~200 dossiers/mois (économie devient matérielle) OU SF1 révèle des faiblesses OCR récurrentes de Gemini. D'ici là : NO-GO pilote.

## 7. ORDRE DE DÉVELOPPEMENT OPTIMISÉ
1. SF1 (socle données) → 2. SF2 (agrégation) → 3. SF3 (écran client A/B) → livrable intermédiaire testable de bout en bout → 4. SF4 (rapport + P4) → 5. SF5 (pièces manquantes) → 6. SF6 (matrice preuves).
Jalons de validation utilisateur : après SF3 (preview du parcours), après SF6 (rapport final enrichi).

## 8. RECOMMANDATION FINALE
- À DÉVELOPPER : SF1, SF2, SF3, SF4 (cœur transparence — 9-13 j) puis SF5, SF6 (7-10 j).
- À SIMPLIFIER : détection flou/contraste/rotation par vision classique (OpenCV) ABANDONNÉE en v1 — redondante (Gemini lit à travers rotation/manuscrit lisible), coûteuse en RAM sur pod 512 MB ; les signaux textuels + drapeaux Gemini couvrent ~90 % de la valeur.
- À ABANDONNER (dans ce lot) : pilote Mistral (reporté sur déclencheurs), % de confiance chiffré au lancement (niveaux qualitatifs d'abord).
- RISQUE PRINCIPAL À PILOTER : friction post-paiement de l'écran qualité → Option B « continuer » toujours disponible en 1 clic, jamais bloquant.
