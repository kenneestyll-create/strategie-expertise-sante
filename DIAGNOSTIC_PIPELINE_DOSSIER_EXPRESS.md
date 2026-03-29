# DIAGNOSTIC STRUCTUREL — Pipeline Dossier Express IA
## Date : 29 mars 2026

---

## 1. CE QUI BLOQUAIT EXACTEMENT

### Cause racine identifiee
Le proxy Emergent (`integrations.emergentagent.com`) impose un **timeout gateway strict de 60 secondes**.
Ce proxy **ne streame PAS reellement** — il bufferise l'integralite de la reponse LLM avant de la renvoyer au client,
meme quand `stream: True` est specifie dans la requete.

### Preuves du diagnostic
| Test | Prompt | max_tokens | Temps | Resultat |
|------|--------|-----------|-------|----------|
| Simple (10 tokens) | Minimal | 10 | 1.3s | OK |
| 1 section | Court | 1500 | 11.3s | OK |
| 3 sections | Moyen | 2500 | 26.8s | OK |
| **Prompt DE complet** | **Gros** | **3000** | **60.1s** | **503** |

Le LLM (Claude Sonnet 4.5) met >60s pour generer 3000 tokens sur un prompt riche,
ce qui depasse le timeout du proxy. Resultat : `upstream connect error or disconnect/reset before headers. reset reason: connection termination`.

### Etape exacte ou le pipeline mourait
Etape 4 "analyse_ia" → `llm_call()` → `_llm_async_call()` → `_llm_stream_call()` (httpx) → HTTP 503 apres 60.1s.
Le pipeline n'atteignait jamais les etapes PDF, email ou enregistrement admin.

---

## 2. POURQUOI LA CORRECTION PRECEDENTE N'ETAIT PAS SUFFISANTE

L'agent precedent avait remplace les appels paralleles (`asyncio.gather`) par des appels sequentiels avec `await asyncio.sleep(2)`.
Cela ne resolvait **rien** car le probleme n'etait pas la concurrence — c'etait que **chaque appel individuel** depassait 60s.

Avec 2 parties de 3000 max_tokens chacune et un prompt riche, chaque partie prenait >60s.
L'approche sequentielle ne faisait que doubler le temps total sans resoudre le timeout par appel.

---

## 3. CE QUI A ETE CHANGE DANS L'ARCHITECTURE

### Avant (broken)
```
_process_dossier_express
  → llm_call() → _llm_async_call()
    → Detecte "DOSSIER EXPRESS" dans le texte
    → Split en 2 parties (Part1 + sleep(2) + Part2)
    → Chaque partie : max_tokens=3000, httpx streaming
    → Chaque partie > 60s → 503 TIMEOUT
```

### Apres (structural fix)
```
_process_dossier_express
  → PATH A (native Anthropic, si cle disponible) : appel unique, pas de proxy
  → PATH B (Emergent) : _generate_dossier_report_multistage()
    → 7 sections focalisees
    → 3 batches paralleles (3+2+2)
    → Chaque appel : max_tokens=1500, via LlmChat SDK
    → Chaque appel : 10-35s (bien sous 60s)
    → Pause 2s entre batches
    → Assemblage du rapport complet
```

### Changements concrets
1. **Nouvelle fonction `_generate_section_llmchat()`** : Appel LLM granulaire avec retry par section via le SDK `LlmChat` (plus rapide et fiable que httpx brut).
2. **Nouvelle fonction `_generate_dossier_report_multistage()`** : Pipeline a 7 sections en 3 batches paralleles.
3. **`_process_dossier_express()` reecrit** : Chemin A (native Anthropic) preserve pour quand la cle live sera configuree. Chemin B (Emergent proxy) utilise le multi-stage.
4. **Stockage analyse** : Limite augmentee de 8000 a 30000 chars pour les nouveaux dossiers.
5. **Chaque section recoit le contexte COMPLET** (situation + documents + cas similaires) — zero perte d'information.

### Ce qui n'a PAS ete change
- Aucune modification du frontend
- Aucune modification des constantes, guards, workflows
- StrategiIA Premium non touche (son pipeline parallele existant fonctionne)
- Aucune degradation du prompt ou des instructions IA

---

## 4. LE PIPELINE TIENT-IL SUR DES CAS REALISTES ?

### Test 1 : Maladie Professionnelle (regime general, 8 documents)
| Metrique | Valeur |
|----------|--------|
| Sections generees | 7/7 |
| Taille rapport | 24,383 chars |
| PDF genere | 37,605 bytes |
| premium_analyses cree | Oui (3be74ebd) |
| Temps pipeline | ~180s |
| Erreurs 503 | 0 |
| Retries necessaires | 0 |

### Test 2 : Accident du Travail (regime agricole, 10 documents)
| Metrique | Valeur |
|----------|--------|
| Sections generees | 7/7 |
| Taille rapport | 25,776 chars |
| PDF genere | 38,548 bytes |
| premium_analyses cree | Oui (1d81902e) |
| Temps pipeline | ~178s |
| Erreurs 503 | 0 |
| Retries necessaires | 0 |

### Qualite du contenu verifie
- References juridiques (Tableau 98, Tableau 57, articles L.461-1 CSS) : **presentes**
- Jurisprudences citees (Cass. soc. 2019, Cass. 2e civ. 2020/2022) : **presentes**
- Analyse des pieces individuelles : **chaque document analyse separement**
- Chronologie reconstituee a partir des dates : **oui**
- Estimation des prejudices (IP, PGPF, DFT) : **avec fourchettes chiffrees**
- Plan d'action avec delais concrets : **5-7 actions numerotees**

---

## 5. LIMITES CONNUES RESTANTES

### Limite 1 : Temps de traitement (~3 minutes)
Le pipeline multi-stage prend environ 3 minutes. C'est incompressible avec le proxy actuel.
**Solution definitive** : Configurer `ANTHROPIC_API_KEY` native → appel unique direct, ~30-40s total.

### Limite 2 : S3 non configure
Les PDF sont generes mais ne peuvent pas etre telecharges car le stockage S3 n'est pas configure.
**Impact** : Le bouton "Telecharger" ne fonctionne pas. Le PDF existe en memoire mais n'est pas persistable.
**Solution** : Configurer S3_ACCESS_KEY et S3_SECRET_KEY.

### Limite 3 : Email Resend en sandbox
Les emails de livraison ne sont pas envoyes (domaine non verifie, mode sandbox).
**Impact** : Le client ne recoit pas d'email. Le dossier est marque "genere_sans_email".
**Solution** : Verifier un domaine dans Resend et configurer SENDER_EMAIL.

### Limite 4 : Dependance au proxy Emergent
Le proxy Emergent est une dependance structurelle avec un timeout de 60s.
**Recommandation** : Pour un service premium en production, utiliser la cle Anthropic native
(`ANTHROPIC_API_KEY`) qui elimine le proxy et permet des appels directs sans contrainte de timeout.

---

## 6. TABLEAU DE VALIDATION E2E

| Tunnel | Etape | Resultat | Preuve |
|--------|-------|----------|--------|
| Dossier Express IA | Lancement pipeline | OK | Logs: `[START]` visible |
| Dossier Express IA | Batch 1 (synthese, pieces, chrono) | OK | Logs: 3 sections OK |
| Dossier Express IA | Batch 2 (juridique, forces/vigilance) | OK | Logs: 2 sections OK |
| Dossier Express IA | Batch 3 (strategie, plan/conclusion) | OK | Logs: 2 sections OK |
| Dossier Express IA | Assemblage rapport | OK | Logs: `REPORT ASSEMBLED: 24383 chars, 7/7` |
| Dossier Express IA | Generation PDF | OK | Logs: `PDF genere (37605 bytes)` |
| Dossier Express IA | Stockage S3 | KO (attendu) | S3 non configure |
| Dossier Express IA | Email livraison | KO (attendu) | Resend sandbox |
| Dossier Express IA | premium_analyses DB | OK | MongoDB: `3be74ebd` cree |
| Admin Dashboard | Onglet Dossier Express | OK | Screenshot: monitoring visible |
| Suivi Client | Timeline 7 etapes | OK | Screenshot: toutes en vert |
| Suivi Client | Message "Rapport disponible" | OK | API: message correct |
| Backend | Zero erreur 503 | OK | Logs: aucune erreur proxy |
| Reproductibilite | 2e test (AT agricole) | OK | 25,776 chars, 7/7 sections |
