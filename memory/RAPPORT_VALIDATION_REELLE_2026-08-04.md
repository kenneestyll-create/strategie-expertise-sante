# RAPPORT UNIQUE — VALIDATION RÉELLE EN PRODUCTION AVEC LE PDF DE RÉFÉRENCE
Date : 04/08/2026 — Ordre exécutif « Arrêt des tests théoriques »
Document de référence : « Rapport Dr Etchepare.pdf » (3 309 077 octets, 9 pages scannées, md5 3ca9ae8b185f04a4011b1f236d092100)
Environnement : PRODUCTION uniquement (https://strategie-expertise-sante.fr)

════════════════════════════════════════════════════════════════
## 1. RECHERCHE MÉMOIRE — LE CORRECTIF PRÉCÉDENT (git, preuves)
════════════════════════════════════════════════════════════════
- **Commit 5cc827a — 08/05/2026 16:19** : introduction du mode asynchrone pour les extractions
  lourdes (fichiers : routes/dossier_express.py +205 lignes, routes/upload.py, pdfExtractor.js).
- **Commit 15cff93 — 08/05/2026 18:16** : finalisation (routes/upload.py), commentaire du code :
  « avoids ingress proxy timeouts (~120s) ».
- **Cause traitée à l'époque** : les extractions Gemini > 120 s tuées par le proxy de l'ANCIENNE infra.
- **Calibration choisie alors** : async seulement si > 2 PDFs OU > 5 Mo. UN SEUL PDF ≤ 5 Mo restait
  SYNCHRONE — acceptable car il tenait sous les ~120 s de l'ancienne infra.

### Ce correctif a-t-il été perdu ? NON.
`git log -S` prouve qu'il est resté intact dans le code du 08/05 jusqu'à aujourd'hui, aucun commit
ne l'a retiré. **Ce n'est pas une régression de code : ce sont les HYPOTHÈSES du correctif qui sont
mortes le 03/08 vers 22h30 UTC**, au moment du redéploiement sur la nouvelle infrastructure :
1. Le timeout de passerelle est passé de ~120 s à **~30 s** → le chemin synchrone (60-150 s pour
   votre scan) est tué en vol. PREUVE MESURÉE : rejeu de l'appel exact le 03/08 23:5x UTC →
   **HTTP 504 « emergent.cloud Gateway time-out » à 30,852 s chrono**.
2. La production est passée en **multi-réplicas** → les chunks d'upload, stockés sur le disque LOCAL
   d'un pod, devenaient invisibles des autres pods. PREUVE MESURÉE : deux chunks envoyés
   successivement rapportaient chacun `received: 1` (pods différents), extract → « pas de données ».
- **Qui a introduit la différence** : le changement d'infrastructure du déploiement (plateforme),
  pas une modification du code applicatif.
- **Correctif définitif (commit dbe66c6, 03/08 23:41)** : extraction TOUJOURS asynchrone dès qu'un
  PDF est présent (plus aucune requête longue exposée à la passerelle, quel que soit son timeout)
  + chunks stockés dans MongoDB (partagés par tous les pods). Déployé par vous ce jour.

════════════════════════════════════════════════════════════════
## 2. TEST RÉEL EN PRODUCTION — VOTRE PDF, CHAQUE ÉTAPE HORODATÉE (04/08/2026 UTC)
════════════════════════════════════════════════════════════════
| Horodatage | Étape | Mesure |
|---|---|---|
| 00:26:52.238 | Envoi chunk 0 (2 097 152 o) | HTTP 200 en 1,567 s — `received: 1` |
| 00:26:53.820 | Envoi chunk 1 (1 211 925 o) | HTTP 200 en 0,890 s — `received: 2, complete: true` ✅ multi-réplicas OK |
| 00:26:54.724 | Reconstruction + stockage + dispatch | HTTP 200 en **2,467 s** (async — plus jamais 504) |
| — | Stockage S3 du fichier original | `size: 3 309 077` = **taille source exacte** → reconstruction intègre ✅ |
| 00:27:17→00:28:40 | Extraction Gemini Vision (asynchrone) | `done` en **≤ 83 s** — 9 pages, 3/3 chunks OK |
| — | Caractères OCR extraits | **21 176** (21 256 avec en-têtes de pagination) |
| 00:30:02.179 | Soumission dossier (21 256 car. transmis à l'analyse) | HTTP 200 en 0,193 s |
| 00:30:25→00:32:50 | Analyse IA (native_anthropic) | chrono serveur : **158,59 s** — **23 307 caractères** produits |
| 00:32:50 | Génération PDF final | chrono serveur : **9,81 s** — **111 961 octets** |
| 00:32:51 | Stockage PDF final (S3) | chrono serveur : **0,86 s** — OK |
| 00:32:52 | Envoi email | chrono serveur : 0,35 s — **ÉCHEC (voir §4)** |
| 00:33:24 | Téléchargement du PDF final | **HTTP 200, 111 961 octets en 0,803 s** |
| Total pipeline dossier | | **169,73 s** (chronos serveur stockés en base, champ `timings`) |

### Où le texte disparaît-il ? NULLE PART.
3 309 077 o (source, md5 vérifié) → 3 309 077 o (stocké S3) → reconstruit à l'identique →
21 176 car. OCR → 21 256 car. envoyés à l'analyse → 23 307 car. d'analyse → PDF final de
111 961 o contenant 27 870 car. de texte. **Le PDF final cite 6 fois le Dr Etchepare avec des
détails que seul votre document contient** : « missionné par MULTI IMPACT ASS pour le compte de
GENERALI », « rapport daté du 24 juillet 2026 (examen du 25 juin 2026), 9 pages, mission
d'arbitrage ». Le contenu a traversé toute la chaîne, en production, sans perte.
Dossier de preuve : `a386ad8d-fb0` (consultable dans votre onglet admin Dossier Express).

════════════════════════════════════════════════════════════════
## 3. VÉRIFICATION INFRASTRUCTURE — CHRONOMÈTRES EXACTS
════════════════════════════════════════════════════════════════
- Timeout passerelle nouvelle infra : **~30 s**, prouvé par la mesure 30,852 s → 504 (03/08).
- Durée Gemini (extraction 9 pages scannées) : ≤ 83 s → INCOMPATIBLE avec 30 s en synchrone,
  d'où l'asynchrone obligatoire (réponse en 2,467 s, travail en arrière-plan).
- Reconstruction chunks : < 2,5 s (incluse dans le dispatch).
- Analyse IA : 158,59 s (asynchrone depuis toujours — jamais affectée par la passerelle).
- PDF : 9,81 s | Stockage : 0,86 s | Téléchargement : 0,80 s.

════════════════════════════════════════════════════════════════
## 4. LE SEUL MAILLON EN ÉCHEC : L'EMAIL — CAUSE EXACTE IDENTIFIÉE
════════════════════════════════════════════════════════════════
Erreur exacte renvoyée par Resend en production à 00:32:52 UTC (capturée par la supervision) :
> **« You can only send testing emails to your own email address (kenneestyll@gmail.co…) »**

Signification : la clé API Resend utilisée en production appartient à un compte en **mode test** —
le domaine d'envoi n'est pas (ou plus) vérifié sur CE compte. Resend n'autorise alors l'envoi
qu'à l'adresse du titulaire du compte (kenneestyll@gmail.com). Ce n'est ni le code, ni le quota
d'hier (l'erreur a changé au reset quotidien) : c'est la **configuration du compte Resend**.

### Action requise — DE VOTRE CÔTÉ (impossible à corriger par le code) :
1. Connectez-vous sur resend.com avec le compte propriétaire de la clé API utilisée en production.
2. Domaines → vérifier que `strategie-expertise-sante.fr` figure avec le statut **Verified**
   (sinon : l'ajouter et poser les 3 enregistrements DNS DKIM/SPF fournis par Resend).
3. Alternative : si le domaine est vérifié sur un AUTRE compte Resend, remplacez la clé API de
   production par celle de CE compte (variables d'environnement du déploiement).
4. Dites-le moi : je relance l'email du dossier a386ad8d-fb0 et je fournis la preuve finale.

════════════════════════════════════════════════════════════════
## 5. ÉTAT DU CRITÈRE DE RÉUSSITE
════════════════════════════════════════════════════════════════
VOTRE PDF → envoyé ✅ → stocké ✅ (3 309 077 o) → reconstitué ✅ → extrait ✅ (21 176 car.) →
envoyé à Gemini ✅ → texte complet ✅ → analysé ✅ (23 307 car.) → rapport ✅ → PDF final ✅
(111 961 o) → téléchargement ✅ → **email ❌ (compte Resend en mode test — action vous incombant)**.

**CHANTIER NON CLÔTURÉ** conformément à votre critère. Il ne reste AUCUN problème de code :
le dernier maillon dépend exclusivement de la vérification du domaine sur votre compte Resend.
