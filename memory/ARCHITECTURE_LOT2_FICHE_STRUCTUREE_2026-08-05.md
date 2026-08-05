# LOT 2 — Architecture de la Fiche Structurée Dossier (ÉTUDE — aucun développement)
Date : 2026-08-05. Statut : préparation. Développement conditionné à validation utilisateur APRÈS premiers dossiers réels.

## Objectif
Extraire et normaliser les faits clés de chaque dossier pour alimenter : moteur de délais, détection
d'incohérences déterministe, recommandations enrichies. C'est le « Contrat B » posé au Lot 1.

## Schéma de données proposé (collection `dossier_fiche` ou champ `fiche` sur dossier_express)
```json
{
  "dossier_id": "...",
  "schema_version": "1.0",
  "extraction_method": "llm_structured",         // appel structuré dédié post-extraction
  "acteurs": {
    "employeur": {"nom": null, "source": {"doc": "...", "page": 3}},
    "organismes": [{"type": "CPAM|MDPH|CARSAT|tribunal", "nom": "...", "source": {...}}],
    "assureurs": [{"nom": "...", "contrat_ref": null, "source": {...}}],
    "experts": [{"nom": "...", "role": "expert assureur|médecin conseil|médecin de recours", "source": {...}}]
  },
  "dates": [
    {"type": "accident|consolidation|notification|expertise|reception_rapport|demande",
     "date": "2026-03-12", "source": {"doc": "...", "page": 2}, "confidence": "haute|moyenne"}
  ],
  "taux": [
    {"type": "IPP|AIPP|invalidité|incapacité", "valeur": 8.0, "bareme": "AIPP|Concours Médical|UCANSS",
     "origine": "CPAM|expert assureur|expert judiciaire", "source": {...}}
  ],
  "garanties": [
    {"type": "ITT|IPT|PTIA|invalidité", "seuil_declenchement": "33%|66%|null", "exclusions": [], "source": {...}}
  ],
  "decisions": [
    {"type": "notification_taux|refus_MP|refus_AAH|attribution", "organisme": "...", "date": "...",
     "voie_recours": "CRA|RAPO|pôle social", "source": {...}}
  ],
  "delais_calcules": [                             // rempli par le moteur de délais (Lot 2 phase 2)
    {"type": "prescription_biennale|recours_2_mois|RAPO", "date_depart": "...", "echeance": "...",
     "statut": "ouvert|proche|expiré", "regle": "L.114-1 C.assur."}
  ]
}
```

## Principes d'architecture (alignés Lot 1)
1. **Toujours sourcé** : chaque fait porte {doc, page} — réutilise le balisage [Page N] et le localisateur du
   validateur de citations (citation_check._locate).
2. **Additive et jamais bloquante** : échec de la fiche → pipeline inchangé (pattern quality_report).
3. **Extraction** : 1 appel LLM structuré (JSON schema strict) APRÈS l'extraction, AVANT l'analyse ;
   coût estimé +0,01-0,03 €/dossier ; Gemini Flash ou le modèle d'analyse en mode outil.
4. **Validation programmatique** : chaque valeur (date, taux) doit exister dans documents_text (même
   normalisation que citation_check) sinon marquée confidence=moyenne.
5. **Moteur de délais = code pur** (règles L.114-1, recours 2 mois CRA/RAPO, prescription MP) sur le champ
   dates[] — AUCUNE date calculée par le LLM.
6. **Incohérences = comparaison déterministe** : deux dates différentes pour le même type, deux taux
   différents pour le même préjudice → alertes structurées injectées dans le rapport.

## Découpage futur (à valider après données réelles)
- L2-1 Fiche structurée + validation programmatique (5-7 j)
- L2-2 Moteur de délais + affichage rapport (4-6 j)
- L2-3 Passe incohérences + section rapport (3-4 j)
Pré-requis : ≥10-20 dossiers réels pour valider le schéma sur la variété réelle des pièces.

## Reportés (inchangé)
Changement OCR, jurisprudence automatique, comparaison de dossiers, statistiques de réussite,
détection fraude, mode professionnel.
