# AUDIT LONG CONTEXT — Dossier Express IA (Étape 1, AUCUNE modification de code)
Date : 06/09/2026 — Baseline préservée : claude-sonnet-5 + thinking disabled, prompts gelés, prod stable.

## 1. Où la limite de 120 000 caractères est appliquée (2 endroits)
| Fichier | Ligne | Mécanisme |
|---|---|---|
| `routes/dossier_express.py` | 612 | `documents_text[:120000]` — troncature silencieuse dans le user_msg de la VOIE NATIVE (PATH A) |
| `utils/llm.py` | 235-248 | `DOCS_LIMIT_CHARS = 120_000` — troncature + WARNING loggé, dans le pipeline multistage (PATH B fallback) |

## 2. Pourquoi cette limite existe
Héritée de l'époque Sonnet 4.5 (contexte 200k tokens, tarif long context majoré au-delà de 200k) + protection du fallback multistage qui renvoie les documents À CHAQUE section (7×) → 120k chars ≈ 34k tokens ×7 = 238k tokens de facturation fallback. La limite protégeait le coût et le contexte, pas la RAM.

## 3. Chronométrage du pipeline pour un gros dossier (mesures réelles)
| Étage | Mécanisme | Durée typique gros dossier | Goulot ? |
|---|---|---|---|
| Upload | chunked, MAX 10 fichiers / 50MB / 100MB total | secondes | non |
| Extraction PDF texte natif | pdfplumber, async background + polling | secondes | non |
| **Extraction PDF SCANNÉ** | Gemini 2.5 Pro, chunks de 4 pages, SÉQUENTIEL (Semaphore=1 imposé par RAM 512MB) | **~30-60 s par chunk → 108 pages scannées ≈ 27 chunks ≈ 15-30 MIN** | **OUI — goulot n°1 historique** |
| Préparation prompt | concat strings | ms | non |
| **Appel LLM natif** | streaming, `asyncio.wait_for(180 s)` + client timeout 120 s | mesuré : TTFT 1-4 s même à 600k chars ; la durée = génération sortie (~60-80 s pour 7k tokens) | non (mais cap 180 s à surveiller) |
| Fallback proxy multistage | 7 sections, docs renvoyés ×7, max_tokens 1500/section, timeout httpx 300 s | ~2-4 min, coût ×7 sur l'input | oui si gros dossier |
| Validation citations | déterministe | ms | non |
| Génération PDF/livraison | background | secondes | non |

**Architecture DÉJÀ asynchrone de bout en bout** : extraction ET analyse tournent en `asyncio.create_task` avec polling frontend (`/status/{id}`) → AUCUN timeout HTTP/gateway sur le flux. Les problèmes de latence passés venaient de l'OCR séquentiel des scans, pas du LLM.

## 4. Sondes de latence Sonnet 5 natif (mesures réelles du 06/09)
| Taille docs | Tokens réels | TTFT | Total (300 tok out) | Coût input |
|---|---|---|---|---|
| 120 000 chars | 52 427 | 1,1 s | 2,6 s | 0,105 $ |
| 300 000 chars | 130 985 | 2,0 s | 3,5 s | 0,262 $ |
| 600 000 chars | **261 910 (> 200k !)** | 3,5 s | 5,3 s | 0,524 $ |
→ L'ingestion d'entrée est quasi instantanée ; la latence LLM = génération de sortie (inchangée). Un dossier 108 pages (~300k chars) passera en ~80-90 s TOTAL sur la voie native, sous le cap 180 s.

## 5. Capacités réelles vérifiées
- **Voie native Anthropic** : contexte **1M tokens STANDARD sur claude-sonnet-5**, sans beta header, **sans surcoût long context** (doc officielle + sonde réelle à 262k tokens acceptée en tarif standard 2 $/M). Sortie max 128k tokens.
- **Fallback proxy Emergent** : param thinking OK (vérifié) ; capacité > 200k tokens d'entrée **À VÉRIFIER par sonde en Étape 3** (litellm transmet mais non testé au-delà de 131k tokens).
- **Mémoire** : les chaînes texte sont négligeables (600k chars = 0,6 MB). La contrainte 512MB concerne uniquement l'OCR Gemini (30-50 MB transitoires par chunk, d'où Semaphore=1 — NE PAS paralléliser sans upgrade RAM).

## 6. Verdict d'audit
Le problème n'est PAS la fenêtre de contexte (1M dispo, gratuite, rapide). Les vrais verrous :
1. Les 2 troncatures hardcodées à 120k chars (PATH A silencieuse !)
2. Le fallback multistage économiquement explosif sur gros dossiers (docs ×7)
3. L'OCR séquentiel des scans 100+ pages (15-30 min) — indépendant du LLM, contraint par la RAM
4. Le cap `wait_for(180 s)` PATH A — suffisant jusqu'à ~400k chars, à élever pour au-delà
5. Qualité d'attention sur 100+ pages : à valider objectivement (Étape 3)

## 7. Étape 2 — Comparaison architecturale
| Critère | A. Long context direct | B. Chunks + synthèse (map-reduce) | C. Hybride (seuil 120k) |
|---|---|---|---|
| Qualité d'analyse | Très bonne (Sonnet 5 long context), à valider sur 108 p | Bonne structure mais synthèse = perte de nuances transversales | = A sur gros dossiers, = prod actuelle sur dossiers normaux |
| Risque perte d'info | Faible (tout le texte vu en un appel) ; risque « needle » à valider | MOYEN-ÉLEVÉ (résumés intermédiaires, citations de 2e main) | Faible |
| Latence | +5-10 s vs actuel (ingestion) | +1 à 3 min (2 étages) | inchangée dossiers normaux ; ~90 s gros dossiers |
| Coût 108 pages | ~0,33 $ (0,26 in + 0,07 out) | ~0,60-0,90 $ (double lecture) | = A |
| Complexité | Minimale (2 constantes + 1 timeout) | Élevée (nouveaux prompts de chunk = TOUCHE au gelé) | Faible (aiguillage par taille) |
| Robustesse | Dépend du fallback >200k (à sonder) | Résiliente par construction | Maximale (petits dossiers isolés du changement) |
| Impact prod actuelle | Change AUSSI les dossiers normaux (même chemin) | Fort (nouveau pipeline pour tous ?) | **NUL sur les dossiers ≤ 120k chars** |

## RECOMMANDATION : Option C (hybride), avec long context direct comme pipeline « gros dossiers »
- Dossiers ≤ 120 000 chars → pipeline actuel STRICTEMENT inchangé (octet pour octet)
- Dossiers > 120 000 chars → même prompt métier, même appel natif, mais : limite portée à ~800 000 chars (~300k tokens), `wait_for` 300 s, `max_tokens` sortie 12 000 (rapports plus riches sur gros dossiers), fallback adapté (si natif échoue : retry natif, puis multistage sur version condensée AVEC AVERTISSEMENT explicite dans le rapport)
- Prompts métier : INCHANGÉS (seule la tranche de documents insérée change de taille)
- OCR scans 100+ pages : inchangé fonctionnellement (15-30 min, déjà asynchrone avec heartbeat) — optimisation = chantier ultérieur éventuel (RAM)

## Étape 3 prévue (après validation user)
Jeu de test : dossier 108 pages OCR fourni par l'utilisateur (ou synthétique réaliste à défaut). Mesures : chars, tokens réels, durées par étage, coût, troncature, exhaustivité, citations, chronologie, qualité médicale — comparé au pipeline actuel (tronqué à 120k). + Sonde fallback proxy > 200k tokens.
