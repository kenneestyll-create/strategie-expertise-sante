# Sentry — Setup Frontend Monitoring d'erreurs

**Date** : 2026-05-19
**Périmètre** : Erreurs runtime React en production uniquement
**État actuel** : 📦 **Code installé, INACTIF** (DSN vide)
**Activation** : à votre charge (étapes ci-dessous)

---

## 🎯 Pourquoi Sentry sur ce projet

Le bug `adminToken is not defined` (19/05/2026) a survécu plusieurs semaines en preview + prod sans détection automatique. Vous l'avez découvert par hasard via une session Samsung Internet. Sentry capture ce type de `ReferenceError` côté navigateur **en 1 minute**, vous notifie par email, et vous fournit la stack trace complète.

## 📐 Configuration installée (résumé)

| Paramètre | Valeur |
|---|---|
| SDK | `@sentry/react@10.x` (50 KB gzipped) |
| Périmètre | **Erreurs runtime uniquement** |
| Replay / Performance / Profiling | ❌ DÉSACTIVÉS |
| Environnements actifs | `production` UNIQUEMENT |
| Preview / dev | Triple exclusion (env check + denyUrls + beforeSend) |
| Release tag | `production-YYYY-MM-DD` (auto-généré au build) |
| Filtres `ignoreErrors` | 11 patterns (voir ci-dessous) |
| Filtres `denyUrls` | 6 patterns |

---

## 🚀 Activation (3 étapes, 5 minutes)

### Étape 1 — Créer le compte Sentry (gratuit)

1. Aller sur https://sentry.io/signup/
2. Sign up avec votre email
3. Choisir le plan **Developer (free)** : 5 000 erreurs/mois, 1 utilisateur, 30j de rétention
4. Créer un projet :
   - **Platform** : React
   - **Project name** : `strategie-expertise-sante-frontend`
   - **Alert frequency** : "Alert me on every new issue" (recommandé)

### Étape 2 — Récupérer le DSN

Après création du projet, Sentry vous montre une page de setup avec un bloc code contenant :
```javascript
Sentry.init({
  dsn: "https://xxxxxxxxxxxxxxxxxxxxxxxx@o123456.ingest.sentry.io/7654321",
  ...
});
```

→ Copier la valeur de `dsn:` (la longue URL https). C'est votre **DSN**.

### Étape 3 — Coller le DSN dans Emergent prod

#### Option A : via l'interface Emergent (recommandé)

1. Aller sur le dashboard Emergent du projet
2. Sélectionner l'environnement **Production**
3. Variables d'environnement frontend → ajouter :
   - `REACT_APP_SENTRY_DSN` = `<votre DSN copié>`
   - `REACT_APP_ENVIRONMENT` = `production`
   - `REACT_APP_BUILD_DATE` = (optionnel, sinon date auto à l'init)
4. Sauvegarder
5. **Redéployer** (Save to GitHub → Deploy)

#### Option B : via le fichier .env (dev local seulement, à éviter en prod)

Modifier `/app/frontend/.env` :
```
REACT_APP_SENTRY_DSN=https://xxxxxxxxxxxxxxxxxxxxxxxx@o123456.ingest.sentry.io/7654321
REACT_APP_ENVIRONMENT=production
```

⚠️ Ne **JAMAIS commit le DSN dans Git** (même s'il est techniquement public). Utiliser Emergent env vars.

---

## ✅ Vérifier que Sentry est actif (test contrôlé)

**Après activation + redéploiement** :

1. Ouvrir https://strategie-expertise-sante.fr en navigateur (pas preview !)
2. F12 → Console
3. Coller dans la console :
   ```javascript
   throw new Error("Test Sentry — ignorer cette erreur");
   ```
4. Attendre 30 secondes
5. Aller sur https://sentry.io → votre projet → "Issues"
6. Une nouvelle issue `Test Sentry — ignorer cette erreur` doit apparaître

Si rien n'apparaît :
- Vérifier que `REACT_APP_SENTRY_DSN` est bien dans les env vars Emergent **prod**
- Vérifier que le redéploiement est terminé
- Inspecter Network tab → chercher une requête vers `*.ingest.sentry.io` (devrait être 200)

---

## 🛡 Erreurs IGNORÉES par défaut

Ces patterns ne remontent **pas** dans Sentry (false-positives connus) :

| Pattern | Raison |
|---|---|
| `ResizeObserver loop limit exceeded` | Bug benign Chrome, sans impact |
| `ResizeObserver loop completed with undelivered notifications` | Idem |
| `ChunkLoadError` / `Loading chunk` | Utilisateurs avec cache obsolète après Deploy |
| `Loading CSS chunk` | Idem CSS |
| `NetworkError` / `Failed to fetch` | Utilisateur perd sa 4G |
| `Network request failed` | Idem |
| `Non-Error promise rejection captured` | Promesses rejetées sans Error object |
| `TypeError: cancelled` | Annulations volontaires (navigation) |
| `AbortError` | Idem (Fetch API) |

**Pour ajouter une nouvelle erreur à ignorer plus tard** : modifier `frontend/src/index.js`, tableau `ignoreErrors`, puis redéployer.

## 🛡 URLs IGNORÉES par défaut

Aucune erreur n'est envoyée si elle provient de :
- Extensions navigateur (`chrome-extension://`, `moz-extension://`, `safari-extension://`)
- `localhost` (dev local)
- `*.preview.emergentagent.com` (votre environnement preview Emergent)
- `*.preview.emergent.sh` (environnement legacy Emergent)

---

## 🔌 Désactivation rapide (en cas de souci)

**Pour stopper Sentry immédiatement, sans redéployer le code** :
1. Aller dans Emergent → env vars prod
2. Vider `REACT_APP_SENTRY_DSN` (mettre `""`)
3. Sauvegarder
4. Le prochain chargement de la page n'initialisera plus Sentry

**Pour le supprimer complètement du code** :
```bash
yarn remove @sentry/react
```
Puis retirer les blocs `Sentry.*` dans `frontend/src/index.js`.

---

## 💰 Quotas et limites Sentry Free

- **5 000 erreurs/mois** — grouping intelligent (erreurs identiques = 1 issue)
- **1 utilisateur** dans la console Sentry
- **30 jours** de rétention des données
- **Free forever** (pas un trial)

Estimation pour votre site (353 sessions/mois × ~2% erreur) ≈ **7-50 erreurs/mois**. Largement dans le quota.

**Si vous explosez le quota** : Sentry ne plante pas votre site, il arrête simplement d'enregistrer les erreurs jusqu'au mois suivant.

---

## 🧭 Ce que Sentry FAIT (et ne fait pas dans cette config)

| Fonctionnalité | Activé ? |
|---|---|
| Capture des erreurs JavaScript runtime | ✅ |
| Stack trace symboliquée (lignes du code source) | ✅ |
| Email d'alerte sur chaque nouvelle issue | ✅ |
| Tag environnement (`production`) | ✅ |
| Tag release (date du build) | ✅ |
| Session Replay vidéo | ❌ |
| Performance monitoring (Web Vitals) | ❌ |
| User feedback widget | ❌ |
| Profiling | ❌ |
| Tracking analytics / events | ❌ |
| Cookies / tracking utilisateur | ❌ |

→ **Aucune dimension RGPD problématique** dans cette config (pas de PII, pas de cookies, pas de tracking).

---

## 🚨 Bonnes pratiques

1. **Configurer "Allowed Domains"** côté Sentry dashboard → Settings → Security & Privacy → Allowed Domains : ajouter `strategie-expertise-sante.fr` (empêche le DSN d'être utilisé depuis un autre domaine si quelqu'un le trouve dans votre bundle JS public).

2. **Ne pas notifier sur chaque erreur dès le début**. Sentry peut être bavard les premiers jours. Si vous êtes submergé d'emails, désactiver "Alert me on every new issue" et activer "Alert me when the issue affects X users".

3. **Marquer les issues comme "Resolved" rapidement** dans Sentry quand vous corrigez. Si l'erreur revient = régression détectée automatiquement.

4. **Ne JAMAIS logger** d'infos sensibles (mots de passe, tokens, PII client) dans une `Error()`. Sentry recevra le texte de l'erreur tel quel.

---

## 📅 Calendrier suggéré

| Date | Action | Statut |
|---|---|---|
| 2026-05-19 | Code Sentry installé (preview, DSN vide, INACTIF) | ✅ FAIT |
| À votre rythme (idéalement < 7j) | Créer compte Sentry + récupérer DSN | ⏳ |
| Même jour | Coller DSN dans Emergent env vars prod + Deploy | ⏳ |
| Même jour | Test manuel (console F12 → throw) | ⏳ |
| Semaine 1 | Observer la console Sentry, calibrer `ignoreErrors` si besoin | ⏳ |

---

## 🔍 Fichiers modifiés / créés

| Fichier | Action |
|---|---|
| `frontend/package.json` | +1 dépendance `@sentry/react` |
| `frontend/src/index.js` | Init Sentry conditionnelle (lignes 3-60) |
| `frontend/.env` | +2 variables (`REACT_APP_SENTRY_DSN` vide, `REACT_APP_ENVIRONMENT=preview`) |
| `/app/memory/SENTRY_SETUP.md` | Ce document |

## 🚫 Ce qui N'A PAS été modifié

- ❌ Aucun fichier backend
- ❌ Aucune page publique (`frontend/src/pages/*`)
- ❌ Aucun composant UI
- ❌ Aucun fichier SEO (`index.html`, `robots.txt`, `sitemap.xml`)
- ❌ Aucun changement comportement Admin
- ❌ Aucun ErrorBoundary ajouté
