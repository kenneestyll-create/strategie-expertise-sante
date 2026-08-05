# Préparation Phase C (SANS ACTIVATION) — Enrichissement du rapport
Date : 2026-08-05. Étude seulement — AUCUN code Phase C écrit, AUCUNE modification production.
Activation conditionnée à : validation Phase B par l'utilisateur.

## Périmètre Phase C (couche « enrichissement de rapport », fusion SF4+SF6 validée)

### C1 — Tableau documentaire en début de rapport
Emplacement : nouvelle section en page 1-2 du PDF, AVANT l'analyse (generate_dossier_pdf accepte déjà document_details ; quality_summary est désormais stocké sur le dossier → données disponibles sans nouveau calcul).
Contenu : nb documents, nb pages, pages exploitables / partielles / ignorées, niveau de confiance (qualitatif + score chiffré ici, contrairement à l'écran client), alertes pièces essentielles, choix du client (transparence : « le client a choisi de poursuivre en connaissance de cause »).

### C2 — Mentions d'impact (formulations graduées, prudence YMYL)
Règle déterministe sur quality_summary :
- Pages unusable dans pièce essentielle → « Les pages X-Y du document Z (pièce essentielle) n'ont pas pu être exploitées : elles peuvent contenir des informations susceptibles de modifier les conclusions. »
- Pages unusable uniquement dans pièces secondaires → « Les limitations constatées portent sur des pièces secondaires et n'ont probablement pas d'impact sur les conclusions principales. »
- Aucune page problématique → « Cette analyse repose sur N pages exploitables sur N fournies. »
Injection : phrase ajoutée au contexte du prompt d'analyse (le LLM en tient compte) + reprise verbatim dans le tableau C1. Risque faible : ajout de contexte, pas de modification des instructions du moteur.

### C3 — Validateur de citations (anti-hallucination programmatique)
1. Le prompt exige : toute citation entre guillemets d'une pièce doit être verbatim avec référence (Document, Page).
2. Post-traitement AVANT génération PDF : extraire les citations du rapport (regex guillemets + référence), les rechercher dans documents_text (normalisation espaces/accents, fuzzy ≥ 0,9) — le texte est déjà balisé [Page N].
3. Citation introuvable → dégradée en « (référence non vérifiée) » ou retirée + log [CITATION-CHECK].
4. Compteur « X citations vérifiées sur X » affiché dans le tableau C1 → preuve de fiabilité mesurable.
Point de vigilance : ne JAMAIS bloquer la livraison du rapport si le validateur échoue (dégradation gracieuse comme Phase A).

## Estimations
- Dev : C1 2 j · C2 1-2 j · C3 3-4 j → total 6-8 j.
- Coût exploitation : ~0 € (code pur + ~100 tokens de contexte prompt).
- Risque : modification du prompt d'analyse (C2/C3) = le seul point touchant le moteur → tests corpus + comparaison avant/après de rapports étalons OBLIGATOIRES avant toute validation.

## Ordre proposé à l'activation
C1 (zéro risque, données déjà stockées) → validation → C2 → C3 → validation finale Phase C sur corpus + rapports étalons.

## Rappels de l'ordre de mission
- Pas de métriques commerciales simulées ; indicateurs réels après premières ventes.
- Reportés : Mistral OCR, changement moteur OCR, détection fraude, comparatif dossiers, stats de réussite, jurisprudence automatique.
- Message produit cible : « Nous vérifions d'abord la qualité des pièces, nous identifions les limites et nous indiquons clairement le niveau de fiabilité de l'analyse. »
