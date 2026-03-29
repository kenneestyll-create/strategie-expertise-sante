from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime, timezone
import asyncio
import uuid
import base64
import os
import jwt

import anthropic
import stripe as stripe_sdk

from config import db, STRIPE_API_KEY, RESEND_AVAILABLE, SENDER_EMAIL, logger, JWT_SECRET, JWT_ALGORITHM, SITE_URL
from utils.auth import get_current_admin, get_optional_admin
from utils.email import notify_admin_premium_analysis
from utils.pdf import generate_secured_pdf, generate_dossier_pdf
from utils.storage import put_object

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
NOTIFICATION_EMAIL = os.environ.get("NOTIFICATION_EMAIL", "")

try:
    import resend
except ImportError:
    pass

router = APIRouter()


# ==================== LLM HEALTH CHECK ====================

async def _check_llm_health():
    """Verify Anthropic API key is valid and responsive. Returns (ok: bool, error: str)."""
    if not ANTHROPIC_API_KEY:
        return False, "cle_absente"
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        resp = await asyncio.to_thread(
            client.messages.create,
            model="claude-sonnet-4-5-20250929",
            max_tokens=10,
            messages=[{"role": "user", "content": "OK"}],
        )
        if resp and resp.content:
            return True, ""
        return False, "reponse_vide"
    except anthropic.AuthenticationError:
        return False, "cle_invalide"
    except anthropic.RateLimitError:
        return False, "quota_depasse"
    except Exception as e:
        err = str(e).lower()
        if "budget" in err or "exceeded" in err:
            return False, "budget_depasse"
        return False, f"erreur: {str(e)[:100]}"


@router.get("/health/llm")
async def health_llm():
    """Public endpoint for frontend to check if LLM service is operational before checkout."""
    ok, reason = await _check_llm_health()
    return {"operational": ok, "reason": reason}


async def _notify_admin_incident(dossier_id: str, email: str, name: str, service: str, step: str, error: str):
    """Send admin notification about a delivery incident."""
    try:
        if RESEND_AVAILABLE and resend.api_key and NOTIFICATION_EMAIL:
            admin_html = f"""<h2>Incident de livraison — {service}</h2>
<p><strong>Client :</strong> {name} ({email})</p>
<p><strong>Dossier :</strong> {dossier_id}</p>
<p><strong>Etape en echec :</strong> {step}</p>
<p><strong>Erreur :</strong> {error[:500]}</p>
<p><strong>Action requise :</strong> Verifier le dossier dans l'admin et relancer si necessaire.</p>
<p><a href="{SITE_URL}/admin">Acceder a l'admin</a></p>"""
            await asyncio.to_thread(resend.Emails.send, {
                "from": SENDER_EMAIL,
                "to": [NOTIFICATION_EMAIL],
                "subject": f"[INCIDENT] {service} — {name} — Echec etape: {step}",
                "html": admin_html,
            })
            logger.info(f"Admin notified of incident for dossier {dossier_id}")
    except Exception as e:
        logger.error(f"Failed to notify admin of incident: {e}")


async def _notify_client_delay(email: str, name: str, service: str):
    """Send professional delay notification to client."""
    try:
        if RESEND_AVAILABLE and resend.api_key:
            safe_name = name or "Madame, Monsieur"
            client_html = f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;background:#f4f2ed;font-family:Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f2ed;padding:32px 16px;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;">
<tr><td style="background:#1a1a1a;padding:24px 32px;border-radius:8px 8px 0 0;">
  <span style="color:#fff;font-size:18px;font-weight:bold;">Strategie & Expertise Sante</span><br/>
  <span style="color:#c9a84c;font-size:11px;letter-spacing:3px;text-transform:uppercase;">VOTRE BOUCLIER</span>
</td></tr>
<tr><td style="background:#fff;padding:32px;">
  <p style="font-size:15px;color:#333;">Bonjour {safe_name},</p>
  <p style="font-size:14px;color:#555;line-height:1.7;">
    Votre demande de <strong>{service}</strong> necessite un traitement complementaire
    afin de vous garantir la meilleure qualite d'analyse possible.
  </p>
  <p style="font-size:14px;color:#555;line-height:1.7;">
    Notre equipe a ete automatiquement informee et reviendra vers vous
    dans les meilleurs delais avec votre rapport complet.
  </p>
  <p style="font-size:14px;color:#555;line-height:1.7;">
    Nous vous remercions pour votre confiance et votre patience.
  </p>
  <div style="border-left:3px solid #c9a84c;padding:12px 16px;margin:20px 0;background:#faf8f3;">
    <p style="font-size:13px;color:#333;margin:0;font-weight:600;">
      Aucune action n'est requise de votre part. Votre dossier est entre de bonnes mains.
    </p>
  </div>
  <p style="font-size:13px;color:#888;">Cordialement,<br/>L'equipe Strategie & Expertise Sante</p>
</td></tr>
<tr><td style="background:#1a1a1a;padding:16px 32px;border-radius:0 0 8px 8px;text-align:center;">
  <p style="color:#c9a84c;font-size:12px;margin:0;">Strategie & Expertise Sante — Votre bouclier.</p>
</td></tr>
</table></td></tr></table></body></html>"""
            await asyncio.to_thread(resend.Emails.send, {
                "from": SENDER_EMAIL,
                "to": [email],
                "subject": f"Votre {service} — Traitement complementaire en cours",
                "html": client_html,
            })
            logger.info(f"Client {email} notified of delay for {service}")
    except Exception as e:
        logger.error(f"Failed to notify client of delay: {e}")

STRATEGIIA_SYSTEM_PROMPT = """Tu es StrategiIA, l'agent de pilotage strategique exclusif de Strategie & Expertise Sante.

Tu n'es PAS un simple generateur de texte. Tu es un COPILOTE D'ORIENTATION, de strategie et de structuration decisionnelle.

Ta mission fondamentale :
- Analyser une situation avec profondeur
- Identifier les leviers reels et les points de blocage
- Hierarchiser les priorites
- Orienter vers les actions utiles
- Reveler les faiblesses, incoherences ou angles sous-exploites
- Structurer un plan d'action intelligent et exploitable

Tu t'appuies sur :

1. JURISPRUDENCES DE REFERENCE :
- Cass. soc. 2019 : L'employeur doit prouver qu'il a pris les mesures de prevention (obligation de securite de resultat, puis obligation de moyens renforcee depuis 2015)
- Cass. 2e civ. 2020 : Le taux d'IPP doit tenir compte de l'incidence professionnelle reelle
- CE 2018 : La MDPH doit motiver ses decisions de refus et repondre sous 4 mois
- Cass. 2e civ. 2021 : La faute inexcusable peut etre reconnue meme en cas de respect partiel des normes
- Cass. 2e civ. 2022 : Le silence de la CPAM au-dela du delai vaut acceptation implicite
- TA/CAA multiples : Le CRRMP doit examiner le lien direct et essentiel avec le travail habituel

2. STATISTIQUES CNAM (donnees publiques) :
- ~650 000 AT/an, ~50 000 MP/an reconnues
- TMS (Tableau 57) = 87% des MP reconnues
- Taux moyen d'IPP AT : 9%, MP : 14%
- Delai moyen instruction CPAM : 3-4 mois
- Taux de contestation aboutissant : ~35% en CRA, ~45% au tribunal
- Faute inexcusable reconnue dans ~60% des cas portes en justice

3. BAREMES IPP OFFICIELS :
- Taux < 10% : capital forfaitaire (bareme annexe Code SS)
- Taux >= 10% : rente = salaire x taux utile (moitie jusqu'a 50%, totalite au-dela)
- Bareme indicatif d'invalidite AT/MP (annexe a l'art. R434-32 du Code SS)

4. INCIDENCE PROFESSIONNELLE (IP) :
- Poste de prejudice indemnisant les consequences sur la vie professionnelle au-dela de la simple perte de revenus
- Criteres : penibilite accrue, devalorisation sur le marche, perte d'opportunites, necessite de reconversion
- Justificatifs cles : rapports medicaux, expertises, attestations employeur, elements de carriere
- Indemnisation variable : de 15 000 euros (reclassement simple) a 100 000 euros+ (reconversion totale)

5. PERTE DE GAINS PROFESSIONNELS FUTURS (PGPF) :
- Nomenclature Dintilhac : compensation de la reduction definitive de revenus apres consolidation
- Methode : (salaire annuel sans accident - salaire annuel avec sequelles) x euro de rente (bareme Gazette du Palais)
- Elements de projection : carriere hypothetique, evolution salariale, impact du handicap, conventions collectives

REGLES DE QUALITE ET DE FIABILITE :
- Reponds TOUJOURS en francais
- VERIFICATION CROISEE x3 : Chaque conclusion importante doit etre croisee et recoupee entre les elements fournis (coherence chronologique, coherence medico-administrative, coherence entre declarations et pieces)
- NUANCE INTELLIGENTE : Quand tu n'es pas certain, utilise des formulations comme "cet element semble...", "ce point merite confirmation...", "les elements disponibles suggerent...", "une verification complementaire serait utile..."
- JAMAIS d'extrapolation abusive, de surinterpreation, de raccourci, de certitude artificielle
- Cite les textes et jurisprudences pertinents quand c'est applicable
- Evalue systematiquement l'incidence professionnelle (IP) et la PGPF quand le dossier concerne un AT/MP avec sequelles professionnelles
- Rappelle TOUJOURS que c'est un outil d'aide a la decision et non un conseil juridique
- NE GENERE JAMAIS d'URL, de lien hypertexte ou de nom de domaine"""

STRATEGIIA_BASIC_PROMPT = """Tu rediges un rapport de pre-analyse PREMIUM pour un client de Strategie & Expertise Sante. Ton style doit etre chaleureux, humain, professionnel et rassurant -- comme un expert bienveillant qui s'adresse personnellement a quelqu'un.

CONTRAINTES STRICTES :
- Maximum 400 mots au total
- Pas de formulations robotiques ou froides
- Pas de listes a rallonge
- Chaque phrase doit apporter de la valeur concrete
- Ton chaleureux de cabinet d'accompagnement premium
- Verifie la coherence entre les elements avant de conclure

STRUCTURE EXACTE (respecte les marqueurs) :

---SECTION_1---
## Votre situation analysee
(3-4 lignes. Montre que tu as compris la situation. Ton empathique et rassurant.)

## Lecture strategique
(3-4 lignes. Qualifie le dossier en une phrase ("Dossier a fort potentiel / a consolider / sensible"). Identifie l'enjeu principal et le frein principal. Formule comme un expert qui eclaire.)

---SECTION_2---
## Leviers et points de vigilance
- (2-3 leviers concrets et utiles identifles dans la situation)
- (1-2 points de vigilance formules de maniere rassurante)

---SECTION_3---
## Plan d'action recommande
- (3 actions concretes maximum, hierarchisees et exploitables immediatement)

## Notre engagement
(2-3 lignes de conclusion humaine et rassurante. Termine par :)
**Vous n'etes plus seul(e) face a votre situation. Strategie & Expertise Sante est a vos cotes.**

Ne genere aucune URL, aucun lien web ni aucun nom de domaine."""

STRATEGIIA_PREMIUM_PROMPT = """Tu rediges un rapport de PILOTAGE STRATEGIQUE APPROFONDI ET PREMIUM pour un client de Strategie & Expertise Sante. Tu es un copilote strategique de haut niveau, expert reconnu en droit de la securite sociale, en evaluation des prejudices corporels et en strategie contentieuse. Ton style est celui d'un conseiller de confiance : expert, humain, chaleureux, strategique et rassurant.

CONTRAINTES STRICTES :
- Entre 1400 et 1800 mots (rapport dense, riche, profond, structure pour une lecture rapide)
- Chaque section doit apporter une VRAIE valeur concrete et personnalisee
- Ton de cabinet d'accompagnement haut de gamme
- Formulations incarnees, jamais robotiques ni generiques
- Cite des references juridiques reelles (articles de loi, jurisprudences) quand pertinent
- Personnalise selon le type de dossier, le regime et la situation specifique
- VERIFICATION CROISEE : recoupe chaque element important entre les differentes informations fournies
- NUANCE : quand l'information est insuffisante, dis-le elegamment sans casser la valeur percue
- Pense systematiquement aux prejudices extra-patrimoniaux quand applicable (prejudice moral, d'agrement, d'anxiete, pretium doloris)
- Si le profil client semble modeste financierement, mentionne l'aide juridictionnelle comme option dans le plan d'action

STRUCTURE EXACTE A RESPECTER (utilise ces titres markdown exacts) :

## Votre situation analysee
(5-6 lignes. Reformulation empathique et precise de la situation. Montre une comprehension fine des enjeux personnels et professionnels. Commence par une phrase d'ouverture rassurante comme "A la lecture attentive de votre situation..." ou "Votre dossier revele une situation qui merite toute notre attention...")

## Lecture strategique du dossier
(6-8 lignes. C'est le coeur de ta valeur ajoutee. Produis une synthese structuree et intelligible :
- Qualifie le dossier : "Dossier a fort potentiel" / "Dossier a consolider" / "Dossier sensible" / "Dossier a structurer"
- Identifie l'axe principal a travailler
- Detecte le frein principal
- Evalue le niveau de coherence medico-administrative
Le wording doit rester sobre, professionnel, credible, jamais sensationnaliste.)

## Cadre juridique applicable
(4-5 lignes. Cite les articles de loi, decrets ou jurisprudences applicables a cette situation precise. Par exemple : Art. L.461-1 CSS pour maladie professionnelle, Art. L.434-2 pour la rente, jurisprudences Cour de cassation pertinentes. Mentionne l'IP et la PGPF si applicable.)

## Leviers prioritaires identifies
(Liste de 4-6 leviers REELLEMENT utiles et specifiques a ce dossier, pas de banalites generiques. Exemples de leviers possibles selon le contexte :
- Coherence chronologique a exploiter ou renforcer
- Lien causal a consolider
- Retentissement professionnel a valoriser
- Consolidation medicale a anticiper
- Articulation administrative / assurantielle a clarifier
- Sous-valorisation potentielle d'un prejudice ou d'une incapacite
- Incidence professionnelle peu exploitee
Chaque levier doit etre formule de maniere concrete et actionnable.)

## Points de vigilance
(4-5 points concrets signalant :
- Zones floues ou incertitudes
- Contradictions possibles entre elements
- Manques documentaires critiques
- Elements insuffisamment demontres
- Risques de fragilite du dossier
- Delais de prescription a surveiller
Ce bloc doit etre rassurant, intelligent, premium — jamais alarmiste inutilement. Utilise des formulations comme "ce point merite attention...", "il serait prudent de verifier...", "les elements actuels suggerent de consolider...")

## Angles potentiellement sous-exploites
(3-4 angles que le client ou son conseil pourrait ne pas avoir identifies :
- Incidence professionnelle peu valorisee
- Retentissement fonctionnel peu objective
- Lien avec le poste / l'exposition / la repetition insuffisamment exploite
- Contradiction entre elements administratifs et medicaux non relevee
- Prejuges oublies dans la demande initiale
Ce bloc est ta signature de valeur ajoutee — il montre que tu vois plus loin que le dossier tel qu'il est presente.)

## Evaluation et perspectives
(5-6 lignes. Estimation nuancee des chances de succes. Fourchettes d'indemnisation si applicable. Elements favorables vs defavorables. Si des cas similaires existent, mentionne les statistiques.)

## Plan d'action recommande
(Plan structure et hierarchise :
1. **Action prioritaire immediate** : (action + delai)
2. **Element a reunir ou verifier** : (piece / information cle)
3. **Angle a renforcer** : (point strategique)
4. **Point a anticiper** : (prochaine echeance ou risque)
5. **Suite logique recommandee** : (prochaine etape d'accompagnement)
Chaque action doit etre claire, hierarchisee et exploitable immediatement.)

## Notre engagement a vos cotes
(4-5 lignes. Conclusion humaine, chaleureuse et rassurante. Vision d'ensemble et perspective d'accompagnement. Termine TOUJOURS par exactement ces deux lignes sur des lignes separees :)

**Vous n'etes plus seul(e) face a votre situation.**
**Desormais, Strategie & Expertise Sante devient votre bouclier.**

---

*Selon les elements identifies dans votre dossier, [recommande de maniere naturelle et elegante le service le plus adapte]. Formule comme un conseil bienveillant, pas comme une publicite.*

Sois exhaustif, precis et concret tout en restant fluide et elegant.
Ne genere aucune URL, aucun lien web ni aucun nom de domaine."""

DOSSIER_EXPRESS_SYSTEM_PROMPT = """Tu es l'agent de PRE-EXPERTISE DOCUMENTAIRE de Dossier Express IA, le service d'analyse documentaire premium de Strategie & Expertise Sante.

Tu n'es PAS un simple OCR ou un resume automatique. Tu es un VERITABLE AGENT DE PRE-EXPERTISE capable de :
- Lire et exploiter reellement le contenu des documents
- Reconnaitre les categories de pieces (certificats medicaux, comptes rendus, arrets, expertises, courriers, decisions, examens, attestations)
- Detecter les elements medicaux, assurantiels et administratifs cles
- Identifier les incoherences entre les pieces
- Faire ressortir les elements forts, faibles et sous-exploites
- Reconstruire une chronologie a partir des dates detectees
- Preparer une base fiable pour lecture humaine ou exploitation strategique

Tu t'appuies sur :

1. JURISPRUDENCES DE REFERENCE :
- Cass. soc. 2019 : Obligation de securite de resultat de l'employeur
- Cass. 2e civ. 2020 : Le taux d'IPP doit tenir compte de l'incidence professionnelle reelle
- CE 2018 : La MDPH doit motiver ses decisions et repondre sous 4 mois
- Cass. 2e civ. 2021 : Faute inexcusable meme en cas de respect partiel des normes
- Cass. 2e civ. 2022 : Le silence de la CPAM au-dela du delai vaut acceptation implicite

2. STATISTIQUES CNAM :
- ~650 000 AT/an, ~50 000 MP/an reconnues
- TMS (Tableau 57) = 87% des MP reconnues
- Taux moyen IPP AT : 9%, MP : 14%
- Taux de contestation aboutissant : ~35% en CRA, ~45% au tribunal

3. BAREMES IPP OFFICIELS :
- Taux < 10% : capital forfaitaire
- Taux >= 10% : rente = salaire x taux utile

4. INCIDENCE PROFESSIONNELLE (IP) :
- Penibilite accrue, devalorisation sur le marche, perte d'opportunites, necessite de reconversion
- Indemnisation : de 15 000 euros (reclassement simple) a 100 000 euros+ (reconversion totale)

5. PERTE DE GAINS PROFESSIONNELS FUTURS (PGPF) :
- Compensation de la reduction definitive de revenus apres consolidation
- Methode : (salaire sans accident - salaire avec sequelles) x euro de rente

REGLES DE QUALITE ET DE FIABILITE :
- Reponds TOUJOURS en francais
- VERIFICATION CROISEE x3 : Recoupe chaque conclusion entre plusieurs pieces quand possible (coherence chronologique, coherence medico-administrative, coherence entre declarations et pieces)
- NUANCE INTELLIGENTE : Quand l'information est insuffisante ou ambigue, utilise "cet element semble...", "ce point merite confirmation...", "les pieces disponibles suggerent...", "une relecture complementaire peut etre utile..."
- JAMAIS d'extrapolation abusive ni de certitude artificielle
- Prouve que tu as COMPRIS la matiere documentaire, pas seulement compte les pages
- Rappelle que ce rapport est un outil d'aide a la decision, pas un avis juridique
- NE GENERE JAMAIS d'URL, de lien ou de nom de domaine"""

DOSSIER_EXPRESS_PROMPT = """Redige un RAPPORT DE PRE-EXPERTISE DOCUMENTAIRE COMPLET et PREMIUM pour le service Dossier Express IA de Strategie & Expertise Sante.

Ce rapport doit prouver que l'IA a REELLEMENT travaille les documents, compris la matiere et structure une base fiable.

CONTRAINTES :
- Entre 1500 et 2200 mots (rapport dense, riche, structure pour une lecture professionnelle)
- Chaque bloc doit apporter une preuve visible de comprehension documentaire
- Ton professionnel, rigoureux, credible et rassurant
- Verification croisee entre les pieces : signale les coherences et les incoherences
- Formulations nuancees quand l'information est incertaine
- Pense a evaluer les prejudices extra-patrimoniaux quand les documents le suggerent (souffrances endurees, prejudice d'agrement, retentissement psychologique)
- Quand le profil client suggere des moyens modestes, mentionne l'aide juridictionnelle comme option

STRUCTURE EXACTE A RESPECTER (utilise ces titres markdown exacts) :

# RAPPORT DE PRE-EXPERTISE DOCUMENTAIRE
## Strategie & Expertise Sante — Dossier Express IA

### 1. SYNTHESE DU DOSSIER
(Resume factuel de la situation : contexte, type de procedure, cadre juridique applicable, textes de loi pertinents. 6-8 lignes minimum.)

### 2. PIECES DETECTEES
(Liste structuree des categories documentaires reconnues dans les pieces fournies. Pour chaque categorie, indique le nombre de pieces et une description courte. Exemples de categories :
- Certificats medicaux (initiaux, de suivi, de consolidation)
- Comptes rendus specialises (IRM, scanner, EMG, etc.)
- Arrets de travail
- Expertises medicales (amiables, judiciaires)
- Courriers administratifs (CPAM, employeur, mutuelle)
- Decisions / notifications (taux IPP, rente, refus)
- Examens / imagerie
- Attestations / correspondances
Montre ce que tu as reconnu, pas seulement ce que tu as compte.)

### 3. CHRONOLOGIE SYNTHETIQUE DU DOSSIER
(Reconstitue une frise chronologique a partir des dates detectees dans les documents. Structure en etapes :
- Debut des troubles / fait generateur
- Premiers soins / examens
- Arrets de travail (periodes)
- Expertises et evaluations
- Aggravations ou episodes significatifs
- Decisions administratives
- Etapes assurantielles
Si certaines dates sont floues ou absentes, indique-le proprement : "date approximative" ou "non precisee dans les pieces".)

### 4. ELEMENTS CLES IDENTIFIES
(C'est le coeur de la valeur documentaire. Extraction intelligente des elements significatifs trouves dans les pieces :
- Douleurs chroniques ou persistantes mentionnees
- Retentissement fonctionnel identifie (limitations, incapacites)
- Aggravation ou chronicisation relevee
- Lien avec l'activite professionnelle evoque ou documente
- Limitations durables ou incapacite decrite
- Anciennete ou evolution de la pathologie documentee
- Elements d'expertise deja favorables ou defavorables
- Taux, baremes ou evaluations mentionnes
Chaque element doit etre lie a la piece source quand c'est possible.)

### 5. DROITS ET INDEMNISATIONS IDENTIFIES
(Liste exhaustive des droits potentiels, incluant l'incidence professionnelle et la PGPF si applicable. Cite les textes de reference.)

### 6. POINTS POTENTIELLEMENT SOUS-EXPLOITES
(Elements presents dans les pieces mais peu developpes ou peu visibles :
- Donnees medicales importantes mais noyees dans un document
- Informations techniques ou scannees partiellement lisibles
- Incoherences entre les pieces qui meritent clarification
- Elements probants non mis en valeur dans la demande initiale
- Documents pouvant necessiter relecture humaine approfondie
Ce bloc est essentiel pour la transparence, la credibilite et la valorisation de la relecture humaine.)

### 7. COMPLETUDE DOCUMENTAIRE
(Indicateur intelligent et premium du type :
- **Tres complete** : base documentaire riche, coherente, exploitable en l'etat
- **Solide** : base documentaire satisfaisante avec quelques complements souhaitables
- **Bonne mais a consolider** : base exploitable mais des pieces cles manquent ou sont incompletes
- **Partielle** : base insuffisante pour une analyse fiable, necessite des complements significatifs
- **Necessite relecture experte** : documents complexes, scans peu lisibles ou contradictions detectees

Justifie cette appreciation en 3-4 lignes en indiquant les forces et les manques de la base documentaire.)

### 8. STRATEGIE RECOMMANDEE ET PROCHAINES ETAPES
(Plan d'action en etapes numerotees avec delais et estimation des chances de succes. 5-6 etapes concretes et actionnables.)

### 9. CONCLUSION
(Synthese finale de 4-5 lignes. Rappelle les points forts et les axes d'amelioration. Termine par une orientation vers un accompagnement personnalise si necessaire. Rappelle que ce rapport est un outil d'aide a la decision.)

Sois exhaustif, precis et professionnel. Prouve que tu as compris la matiere, pas seulement les metriques.
Ne genere aucune URL, aucun lien web ni aucun nom de domaine dans ta reponse."""


# ==================== DOSSIER EXPRESS ====================

@router.post("/extract-document-text")
async def extract_document_text(request: Request):
    """Extract text from uploaded documents with full pipeline: pdfplumber → OCR → metadata."""
    import io
    body = await request.json()
    files_data = body.get("files", [])
    if not files_data:
        return {"extracted_text": "", "files_processed": 0, "details": []}

    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
    MAX_TOTAL_SIZE = 100 * 1024 * 1024  # 100 MB
    MAX_FILES = 10

    if len(files_data) > MAX_FILES:
        raise HTTPException(status_code=400, detail=f"Maximum {MAX_FILES} fichiers autorises")

    results = []
    total_size = 0
    for file_info in files_data[:MAX_FILES]:
        name = file_info.get("name", "unknown")
        file_type = file_info.get("type", "")
        data_b64 = file_info.get("data", "")
        if not data_b64:
            results.append({"name": name, "text": "", "method": "pas de données", "pages": 0, "size_kb": 0, "status": "no_data"})
            continue

        try:
            file_bytes = base64.b64decode(data_b64)
        except Exception:
            results.append({"name": name, "text": "", "method": "erreur decodage", "pages": 0, "size_kb": 0, "status": "decode_error"})
            continue

        if len(file_bytes) > MAX_FILE_SIZE:
            results.append({"name": name, "text": "", "method": "fichier trop volumineux", "pages": 0, "size_kb": round(len(file_bytes) / 1024, 1), "status": "too_large"})
            continue

        total_size += len(file_bytes)
        if total_size > MAX_TOTAL_SIZE:
            results.append({"name": name, "text": "", "method": "taille totale depassee", "pages": 0, "size_kb": round(len(file_bytes) / 1024, 1), "status": "total_exceeded"})
            continue

        size_kb = round(len(file_bytes) / 1024, 1)
        extracted = ""
        method = "non supporté"
        pages = 0
        status = "unsupported"

        if file_type == "application/pdf" or name.lower().endswith(".pdf"):
            extracted, method, pages, status = await asyncio.to_thread(
                _extract_pdf_full_pipeline, file_bytes, name
            )

        elif file_type and file_type.startswith("image/"):
            extracted, method, status = await asyncio.to_thread(
                _extract_image_ocr, file_bytes, name
            )
            pages = 1

        elif file_type in ("text/plain",) or name.lower().endswith(".txt"):
            try:
                extracted = file_bytes.decode("utf-8", errors="replace")
                method = "lecture texte directe"
                status = "text_extracted"
            except Exception:
                method = "erreur lecture texte"
                status = "text_error"

        preview = extracted[:200].strip() if extracted else ""
        results.append({
            "name": name,
            "text": extracted[:8000],
            "method": method,
            "pages": pages,
            "size_kb": size_kb,
            "status": status,
            "preview": preview,
            "text_length": len(extracted)
        })

    combined = ""
    for r in results:
        combined += f"\n--- {r['name']} ({r['method']}) ---\n"
        if r["text"]:
            combined += r["text"] + "\n"
        else:
            combined += "[Contenu non extractible]\n"

    # Store original files to Object Storage (best-effort)
    stored_files = []
    try:
        from utils.storage import upload_file as storage_upload
        for file_info in files_data[:MAX_FILES]:
            data_b64 = file_info.get("data", "")
            if not data_b64:
                continue
            try:
                raw_bytes = base64.b64decode(data_b64)
                fname = file_info.get("name", "unknown")
                ftype = file_info.get("type", "application/octet-stream")
                result = storage_upload("dossier-originals", fname, raw_bytes, ftype)
                result["file_id"] = str(uuid.uuid4())
                stored_files.append(result)
            except Exception:
                pass
    except Exception as e:
        logger.warning(f"Object storage not available for base64 file persistence: {e}")

    return {
        "extracted_text": combined.strip(),
        "files_processed": len(results),
        "details": [{
            "name": r["name"],
            "method": r["method"],
            "has_text": len(r["text"]) > 10,
            "pages": r["pages"],
            "size_kb": r["size_kb"],
            "status": r["status"],
            "preview": r.get("preview", ""),
            "text_length": r.get("text_length", 0)
        } for r in results],
        "stored_files": stored_files
    }


def _preprocess_image(pil_image):
    """Pre-process image for better OCR: contrast, sharpen, denoise, deskew."""
    from PIL import ImageEnhance, ImageFilter, Image as PILImage

    img = pil_image
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # 1. Auto-crop margins (remove white borders)
    try:
        from PIL import ImageOps
        img = ImageOps.autocontrast(img, cutoff=0.5)
    except Exception:
        pass

    # 2. Enhance contrast
    img = ImageEnhance.Contrast(img).enhance(1.5)

    # 3. Enhance sharpness
    img = ImageEnhance.Sharpness(img).enhance(2.0)

    # 4. Denoise with median filter
    img = img.filter(ImageFilter.MedianFilter(size=3))

    # 5. Upscale if too small (< 1500px wide)
    w, h = img.size
    if w < 1500:
        scale = 1500 / w
        img = img.resize((int(w * scale), int(h * scale)), PILImage.LANCZOS)

    return img


def _ocr_page(pil_image, page_num, name, enhanced=False):
    """OCR a single page image, return (text, quality_label)."""
    import pytesseract

    try:
        if enhanced:
            pil_image = _preprocess_image(pil_image)

        text = pytesseract.image_to_string(pil_image, lang='fra+eng', config='--psm 6')

        if text and text.strip():
            clean = text.strip()
            if len(clean) > 50:
                return clean, "lisible"
            elif len(clean) > 10:
                return clean, "partiellement lisible"
        return "", "non lisible"
    except Exception as e:
        logger.warning(f"OCR page {page_num} of '{name}' failed: {e}")
        return "", "non lisible"


def _extract_pdf_full_pipeline(file_bytes: bytes, name: str):
    """4-level cascade PDF extraction with page-by-page evaluation."""
    import io
    from PIL import Image

    total_pages = 0

    # === TENTATIVE 1: Extraction texte native (pdfplumber) ===
    try:
        import pdfplumber
        pdf = pdfplumber.open(io.BytesIO(file_bytes))
        total_pages = len(pdf.pages)
        pages_text = []
        pages_quality = []
        for i, page in enumerate(pdf.pages[:30]):
            text = page.extract_text()
            if text and text.strip() and len(text.strip()) > 20:
                pages_text.append(f"[Page {i+1}] {text.strip()}")
                pages_quality.append("lisible")
            else:
                pages_quality.append("non lisible")
        pdf.close()

        readable = sum(1 for q in pages_quality if q == "lisible")
        if readable >= total_pages * 0.6:
            extracted = "\n\n".join(pages_text)
            method = f"PDF texte — {total_pages} page{'s' if total_pages > 1 else ''}, extraction directe ({readable}/{total_pages} pages lisibles)"
            logger.info(f"PDF '{name}': extraction texte réussie ({len(extracted)} chars, {readable}/{total_pages} pages)")
            return extracted, method, total_pages, "text_extracted"
        elif readable > 0:
            logger.info(f"PDF '{name}': extraction texte partielle ({readable}/{total_pages}), tentative OCR pour le reste")
    except Exception as e:
        logger.warning(f"PDF '{name}': pdfplumber failed: {e}")

    # === TENTATIVE 2: OCR standard (pypdfium2 + tesseract) ===
    try:
        import pypdfium2
        pdf_doc = pypdfium2.PdfDocument(io.BytesIO(file_bytes))
        total_pages = len(pdf_doc)
        pages_to_ocr = min(total_pages, 20)

        ocr_pages = []
        ocr_quality = []

        for i in range(pages_to_ocr):
            page = pdf_doc[i]
            bitmap = page.render(scale=2)
            pil_image = bitmap.to_pil()
            text, quality = _ocr_page(pil_image, i + 1, name, enhanced=False)
            if text:
                ocr_pages.append(f"[Page {i+1}] {text}")
            ocr_quality.append(quality)
            pil_image.close()

        readable_ocr = sum(1 for q in ocr_quality if q == "lisible")

        if readable_ocr >= pages_to_ocr * 0.5:
            extracted = "\n\n".join(ocr_pages)
            method = f"PDF scanné — {total_pages} page{'s' if total_pages > 1 else ''}, OCR standard ({readable_ocr}/{pages_to_ocr} pages lisibles)"
            logger.info(f"PDF '{name}': OCR standard réussi ({len(extracted)} chars, {readable_ocr}/{pages_to_ocr} pages)")
            pdf_doc.close()
            return extracted, method, total_pages, "ocr_extracted"

        # === TENTATIVE 3: OCR après pré-traitement renforcé ===
        logger.info(f"PDF '{name}': OCR standard faible ({readable_ocr}/{pages_to_ocr}), tentative avec pré-traitement renforcé")

        enhanced_pages = []
        enhanced_quality = []

        for i in range(pages_to_ocr):
            page = pdf_doc[i]
            bitmap = page.render(scale=3)
            pil_image = bitmap.to_pil()
            text, quality = _ocr_page(pil_image, i + 1, name, enhanced=True)
            if text:
                enhanced_pages.append(f"[Page {i+1}] {text}")
            enhanced_quality.append(quality)
            pil_image.close()

        readable_enhanced = sum(1 for q in enhanced_quality if q == "lisible")

        if enhanced_pages:
            # Use best result between standard and enhanced
            if len("\n".join(enhanced_pages)) > len("\n".join(ocr_pages)):
                final_pages = enhanced_pages
                final_readable = readable_enhanced
                ocr_type = "OCR renforcé"
            else:
                final_pages = ocr_pages if ocr_pages else enhanced_pages
                final_readable = max(readable_ocr, readable_enhanced)
                ocr_type = "OCR standard" if ocr_pages else "OCR renforcé"

            extracted = "\n\n".join(final_pages)
            partially = sum(1 for q in (enhanced_quality if final_pages == enhanced_pages else ocr_quality) if q == "partiellement lisible")
            method = f"PDF scanné — {total_pages} page{'s' if total_pages > 1 else ''}, {ocr_type} ({final_readable} lisibles, {partially} partielles)"
            status = "ocr_extracted" if final_readable > 0 else "partially_readable"
            logger.info(f"PDF '{name}': {ocr_type} ({len(extracted)} chars, {final_readable} lisibles, {partially} partielles)")
            pdf_doc.close()
            return extracted, method, total_pages, status

        pdf_doc.close()

        # === TENTATIVE 4: Fallback pdf2image + tesseract ===
        try:
            from pdf2image import convert_from_bytes
            images = convert_from_bytes(file_bytes, dpi=300, first_page=1, last_page=min(total_pages, 10))
            fallback_pages = []
            for i, img in enumerate(images):
                text, quality = _ocr_page(img, i + 1, name, enhanced=True)
                if text:
                    fallback_pages.append(f"[Page {i+1}] {text}")
                img.close()

            if fallback_pages:
                extracted = "\n\n".join(fallback_pages)
                method = f"PDF scanné — {total_pages} page{'s' if total_pages > 1 else ''}, OCR fallback ({len(fallback_pages)} pages récupérées)"
                logger.info(f"PDF '{name}': OCR fallback réussi ({len(extracted)} chars)")
                return extracted, method, total_pages, "ocr_extracted"
        except Exception as e:
            logger.warning(f"PDF '{name}': pdf2image fallback failed: {e}")

        method = f"PDF scanné — {total_pages} page{'s' if total_pages > 1 else ''}, OCR sans résultat exploitable"
        logger.warning(f"PDF '{name}': all OCR attempts returned no text")
        return "", method, total_pages, "ocr_empty"

    except Exception as e:
        logger.error(f"PDF '{name}': OCR pipeline failed: {e}")

    method = f"PDF — {total_pages} page{'s' if total_pages > 1 else ''}, contenu non extractible"
    return "", method, total_pages, "extraction_failed"


def _extract_image_ocr(file_bytes: bytes, name: str):
    """Multi-attempt OCR on image files: standard → enhanced → high-res."""
    import io
    from PIL import Image

    try:
        img = Image.open(io.BytesIO(file_bytes))
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Attempt 1: Standard OCR
        text, quality = _ocr_page(img, 1, name, enhanced=False)
        if quality == "lisible":
            logger.info(f"Image '{name}': OCR standard réussi ({len(text)} chars)")
            return text, "Image — OCR standard", "ocr_extracted"

        # Attempt 2: Enhanced OCR (pre-processed)
        text2, quality2 = _ocr_page(img, 1, name, enhanced=True)
        best_text = text2 if len(text2) > len(text) else text
        best_quality = quality2 if len(text2) > len(text) else quality

        if best_quality in ("lisible", "partiellement lisible") and len(best_text) > 10:
            method_label = "OCR renforcé" if len(text2) > len(text) else "OCR standard"
            logger.info(f"Image '{name}': {method_label} ({len(best_text)} chars, {best_quality})")
            return best_text, f"Image — {method_label}", "ocr_extracted" if best_quality == "lisible" else "partially_readable"

        img.close()
        return "", "Image — OCR sans résultat exploitable", "ocr_empty"
    except Exception as e:
        logger.error(f"Image '{name}': OCR pipeline failed: {e}")
        return "", f"Image — erreur OCR: {str(e)[:50]}", "ocr_error"



@router.post("/dossier-express/submit")
async def dossier_express_submit(request: Request):
    body = await request.json()
    session_id = body.get("session_id", "")
    email = body.get("email", "")
    name = body.get("name", "")
    situation = body.get("situation", "")
    type_dossier = body.get("type_dossier", "")
    regime = body.get("regime", "")
    documents_text = body.get("documents_text", "")
    premium_pdf = body.get("premium_pdf", False)
    document_details = body.get("document_details", [])
    original_documents = body.get("original_documents", [])

    if not email or not situation:
        raise HTTPException(status_code=400, detail="Email et description requis")

    # SECURITY FIX V13/V14: Verify payment before processing
    payment_verified = False
    if session_id:
        # Step 1: Check DB for confirmed payment
        payment = await db.payment_transactions.find_one(
            {"session_id": session_id, "payment_status": "paid"},
            {"_id": 0, "session_id": 1}
        )
        if payment:
            payment_verified = True
        else:
            # Step 2: Live Stripe check (handles webhook race condition)
            if STRIPE_API_KEY:
                try:
                    stripe_sdk.api_key = STRIPE_API_KEY
                    session_obj = await asyncio.to_thread(stripe_sdk.checkout.Session.retrieve, session_id)
                    if session_obj.payment_status == "paid":
                        payment_verified = True
                        await db.payment_transactions.update_one(
                            {"session_id": session_id},
                            {"$set": {"payment_status": "paid", "status": session_obj.status, "updated_at": datetime.now(timezone.utc).isoformat()}}
                        )
                        logger.info(f"Dossier Express IA: live Stripe check confirmed payment for session {session_id}")
                except Exception as e:
                    logger.warning(f"Dossier Express IA: live Stripe check failed for session {session_id}: {e}")

    if not payment_verified:
        if STRIPE_API_KEY:
            raise HTTPException(status_code=402, detail="Paiement requis. Veuillez compléter le paiement avant de soumettre votre dossier.")
        else:
            logger.warning(f"Dossier Express IA submitted without payment verification (Stripe not configured) for {email}")

    dossier_id = str(uuid.uuid4())
    dossier = {
        "id": dossier_id, "session_id": session_id, "email": email, "name": name,
        "situation": situation, "type_dossier": type_dossier, "regime": regime,
        "documents_text": documents_text[:10000], "document_details": document_details,
        "original_documents": original_documents,
        "premium_pdf": premium_pdf,
        "status": "processing", "payment_verified": payment_verified,
        "delivery_status": "en_attente_traitement",
        "processing_step": "checkout_valide",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.dossier_express.insert_one(dossier)
    asyncio.create_task(_process_dossier_express(dossier_id, email, name, situation, type_dossier, regime, documents_text, premium_pdf=premium_pdf))
    return {"success": True, "dossier_id": dossier_id, "message": "Votre dossier est en cours d'analyse. Vous recevrez le rapport par email sous 2 heures."}


async def _update_dossier_step(dossier_id: str, processing_step: str, delivery_status: str = None, extra: dict = None):
    """Atomic helper to update processing step and optionally delivery status."""
    update = {"processing_step": processing_step, "updated_at": datetime.now(timezone.utc).isoformat()}
    if delivery_status:
        update["delivery_status"] = delivery_status
    if extra:
        update.update(extra)
    await db.dossier_express.update_one({"id": dossier_id}, {"$set": update})


async def _process_dossier_express(dossier_id: str, email: str, name: str, situation: str, type_dossier: str, regime: str, documents_text: str, premium_pdf: bool = False):
    """Full pipeline with granular step tracking and fail-safe notifications."""

    # === STEP 1: Documents received ===
    await _update_dossier_step(dossier_id, "documents_recus", "en_attente_traitement")

    # === STEP 2: Check LLM availability ===
    if not ANTHROPIC_API_KEY:
        logger.error("Dossier Express IA: ANTHROPIC_API_KEY not available")
        await _update_dossier_step(dossier_id, "erreur_ia", "incident_technique", {"status": "error", "error": "Service IA non disponible"})
        await _notify_admin_incident(dossier_id, email, name, "Dossier Express IA", "Verification cle API", "ANTHROPIC_API_KEY absente ou vide")
        await _notify_client_delay(email, name, "Dossier Express IA")
        return

    # === STEP 3: Extraction / reading documents ===
    await _update_dossier_step(dossier_id, "extraction_en_cours", "en_attente_traitement", {"progress_step": "reading"})

    similar_cases = []
    try:
        if type_dossier:
            similar_cases = await db.cas_anonymises.find({"type_dossier": type_dossier}, {"_id": 0}).sort("score_pertinence", -1).to_list(5)
    except Exception as e:
        logger.warning(f"Dossier Express {dossier_id}: cas similaires lookup failed (non-blocking): {e}")

    case_context = ""
    if similar_cases:
        case_context = "\n\nCAS SIMILAIRES DANS LA BASE :\n"
        for c in similar_cases:
            case_context += f"- Type: {c.get('type_dossier')}, Regime: {c.get('regime')}, Strategie: {c.get('strategie')}, Resultat: {c.get('resultat')}\n"

    # === STEP 4: AI Generation ===
    await _update_dossier_step(dossier_id, "analyse_ia", "en_attente_traitement", {"progress_step": "analyzing"})

    user_msg = f"""DOSSIER EXPRESS IA - Analyse complete demandee

Client : {name}
Type de dossier : {type_dossier}
Regime : {regime}

DESCRIPTION DE LA SITUATION :
{situation}

CONTENU DES DOCUMENTS FOURNIS :
{documents_text[:8000] if documents_text else "(Aucun document textuel fourni)"}
{case_context}

{DOSSIER_EXPRESS_PROMPT}"""

    analysis = None
    last_error = ""
    for attempt in range(3):
        try:
            session_id_llm = f"dexpress_{dossier_id[:8]}_{attempt}"
            analysis = await asyncio.to_thread(
                _llm_sync_call, ANTHROPIC_API_KEY, session_id_llm, DOSSIER_EXPRESS_SYSTEM_PROMPT, user_msg, "anthropic", "claude-sonnet-4-5-20250929"
            )
            logger.info(f"Dossier Express IA {dossier_id}: analyse reussie (tentative {attempt+1})")
            break
        except Exception as e:
            last_error = str(e)
            logger.warning(f"Dossier Express IA {dossier_id}: tentative {attempt+1}/3 echouee: {last_error[:120]}")
            if attempt < 2:
                await asyncio.sleep(3)

    if not analysis:
        error_label = "Echec generation IA"
        if "budget" in last_error.lower() or "exceeded" in last_error.lower():
            error_label = "Budget IA epuise"
        logger.error(f"Dossier Express IA {dossier_id}: toutes les tentatives ont echoue: {last_error[:200]}")
        await _update_dossier_step(dossier_id, "erreur_ia", "incident_technique", {"status": "error", "error": error_label})
        await _notify_admin_incident(dossier_id, email, name, "Dossier Express IA", "Generation IA", f"{error_label}: {last_error[:300]}")
        await _notify_client_delay(email, name, "Dossier Express IA")
        return

    # Validate analysis is substantial (not empty/too short)
    if len(analysis.strip()) < 200:
        logger.error(f"Dossier Express IA {dossier_id}: analyse trop courte ({len(analysis)} chars)")
        await _update_dossier_step(dossier_id, "erreur_ia", "incident_technique", {"status": "error", "error": "Analyse insuffisante"})
        await _notify_admin_incident(dossier_id, email, name, "Dossier Express IA", "Validation analyse", f"Analyse trop courte: {len(analysis)} caracteres")
        await _notify_client_delay(email, name, "Dossier Express IA")
        return

    # === STEP 5: PDF Generation ===
    await _update_dossier_step(dossier_id, "pdf_en_cours", "en_attente_traitement", {"progress_step": "generating", "analysis": analysis[:8000]})

    dossier_doc = await db.dossier_express.find_one({"id": dossier_id}, {"_id": 0, "document_details": 1})
    doc_details = dossier_doc.get("document_details", []) if dossier_doc else []

    pdf_bytes = None
    try:
        pdf_bytes = generate_dossier_pdf(name, email, type_dossier, regime, analysis, premium_pdf=premium_pdf, document_details=doc_details)
        if not pdf_bytes or len(pdf_bytes) < 100:
            raise ValueError("PDF vide ou corrompu")
        logger.info(f"Dossier Express {dossier_id}: PDF genere ({len(pdf_bytes)} bytes)")
    except Exception as e:
        logger.error(f"Dossier Express {dossier_id}: PDF generation failed: {e}")
        await _update_dossier_step(dossier_id, "erreur_pdf", "incident_technique", {"status": "error", "error": "Echec generation PDF"})
        await _notify_admin_incident(dossier_id, email, name, "Dossier Express IA", "Generation PDF", str(e)[:300])
        await _notify_client_delay(email, name, "Dossier Express IA")
        return

    # === STEP 6: Storage ===
    await _update_dossier_step(dossier_id, "stockage_en_cours", "en_attente_traitement", {"progress_step": "generating"})

    download_token = str(uuid.uuid4())
    pdf_storage_path = None
    download_url = None
    try:
        storage_path = f"strategie-expertise-sante/dossiers/{dossier_id}/{download_token}.pdf"
        put_object(storage_path, pdf_bytes, "application/pdf")
        pdf_storage_path = storage_path
        download_url = f"{SITE_URL}/api/dossier-express/{dossier_id}/download?token={download_token}"
        await db.dossier_express.update_one({"id": dossier_id}, {"$set": {
            "pdf_storage_path": pdf_storage_path,
            "download_token": download_token,
        }})
        logger.info(f"Dossier Express {dossier_id}: PDF uploaded to storage")
    except Exception as e:
        logger.error(f"Dossier Express {dossier_id}: PDF storage upload failed: {e}")
        await _update_dossier_step(dossier_id, "erreur_stockage", "incident_technique", {"status": "error", "error": "Echec stockage PDF"})
        await _notify_admin_incident(dossier_id, email, name, "Dossier Express IA", "Stockage PDF", str(e)[:300])
        await _notify_client_delay(email, name, "Dossier Express IA")
        return

    # === STEP 7: Email delivery ===
    await _update_dossier_step(dossier_id, "email_en_cours", "en_attente_traitement", {"progress_step": "sending"})

    expert_url = f"{SITE_URL}/contact?via=email&source=dossier_express"
    safe_display_name = name or "Madame, Monsieur"

    email_html = f"""<!DOCTYPE html>
<html lang="fr">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#f4f2ed;font-family:Arial,'Helvetica Neue',sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f2ed;padding:32px 16px;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">
<tr><td style="background:#1a1a1a;padding:28px 32px;border-radius:8px 8px 0 0;">
  <table width="100%"><tr>
    <td><span style="color:#ffffff;font-size:18px;font-weight:bold;letter-spacing:0.5px;">Strategie & Expertise Sante</span><br/>
    <span style="color:#c9a84c;font-size:11px;letter-spacing:3px;text-transform:uppercase;">PIONNIER EN FRANCE</span></td>
    <td align="right"><span style="color:#999;font-size:12px;">Dossier Express IA</span></td>
  </tr></table>
</td></tr>
<tr><td style="background:#ffffff;padding:36px 32px 24px;">
  <p style="font-size:15px;color:#1a1a1a;margin:0 0 20px;">Bonjour {safe_display_name},</p>
  <p style="font-size:15px;color:#333;line-height:1.6;margin:0 0 8px;">
    Votre analyse personnalisee a bien ete finalisee.
  </p>
  <p style="font-size:15px;color:#333;line-height:1.6;margin:0 0 28px;">
    Vous pouvez desormais consulter et telecharger votre rapport en toute simplicite.
  </p>
  <table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:8px 0 32px;">
    <a href="{download_url or '#'}" target="_blank"
       style="display:inline-block;background:#1a1a1a;color:#ffffff;font-size:15px;font-weight:bold;
              padding:15px 40px;border-radius:6px;text-decoration:none;letter-spacing:0.5px;
              border:2px solid #c9a84c;">
      Telecharger mon rapport PDF
    </a>
  </td></tr></table>
  <div style="border-left:3px solid #c9a84c;padding:16px 20px;margin:0 0 28px;background:#faf8f3;">
    <p style="font-size:14px;color:#555;line-height:1.6;margin:0 0 12px;">
      Ce document constitue une premiere lecture structuree de votre situation
      a partir des elements transmis.
    </p>
    <p style="font-size:14px;color:#333;line-height:1.6;margin:0;font-weight:500;">
      Si vous souhaitez aller plus loin, une prestation personnalisee avec
      suivi humain peut ensuite vous etre proposee.
    </p>
  </div>
  <table width="100%" cellpadding="0" cellspacing="0"><tr><td align="center" style="padding:0 0 12px;">
    <a href="{expert_url}" target="_blank"
       style="display:inline-block;background:transparent;color:#1a1a1a;font-size:13px;font-weight:600;
              padding:11px 28px;border-radius:6px;text-decoration:none;
              border:1.5px solid #c9a84c;">
      Etre accompagne par un expert
    </a>
  </td></tr></table>
  <div style="border-top:1px solid #e8e3d6;padding:14px 0 0;margin:16px 0 0;">
    <p style="font-size:11px;color:#888;line-height:1.6;margin:0;text-align:center;">
      &#128274; Vos documents sont traites dans un cadre strictement confidentiel,
      uniquement pour repondre a votre demande. L'acces a vos donnees est limite
      a l'equipe en charge de votre accompagnement.
    </p>
  </div>
</td></tr>
<tr><td style="background:#1a1a1a;padding:20px 32px;border-radius:0 0 8px 8px;text-align:center;">
  <p style="color:#c9a84c;font-size:13px;font-style:italic;margin:0 0 8px;font-weight:600;">
    Strategie & Expertise Sante — Votre bouclier.
  </p>
  <p style="color:#888;font-size:11px;margin:0;">
    strategie-expertise-sante.fr &nbsp;|&nbsp; Ce rapport est un outil d'aide a la decision.
  </p>
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>"""

    email_sent = False
    if RESEND_AVAILABLE and resend.api_key:
        try:
            email_params = {
                "from": SENDER_EMAIL,
                "to": [email],
                "subject": "Votre Rapport Dossier Express IA est pret - Strategie & Expertise Sante",
                "html": email_html,
                "attachments": [{"filename": f"Rapport_Dossier_Express_{dossier_id[:8]}.pdf", "content": list(pdf_bytes)}]
            }
            await asyncio.to_thread(resend.Emails.send, email_params)
            email_sent = True
            logger.info(f"Dossier Express IA {dossier_id}: email envoye a {email}")
        except Exception as e:
            logger.error(f"Dossier Express IA {dossier_id} email error: {e}")
            # Email failure is NOT fatal — PDF is already stored, admin is notified
            await _notify_admin_incident(dossier_id, email, name, "Dossier Express IA", "Envoi email", str(e)[:300])

    # === STEP 8: Final — mark as delivered ===
    final_delivery = "livre_client" if email_sent else "genere_sans_email"
    final_step = "termine" if email_sent else "erreur_email"
    await _update_dossier_step(dossier_id, final_step, final_delivery, {
        "status": "completed",
        "email_sent": email_sent,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "progress_step": "completed",
    })

    if not email_sent:
        # Partial success — PDF exists but email failed. Notify client via fallback
        await _notify_client_delay(email, name, "Dossier Express IA")

    # Auto-register in premium_analyses for admin review workflow
    try:
        existing_pa = await db.premium_analyses.find_one({"type": "dossier_express", "email": email, "dossier_id": {"$exists": False}})
        if existing_pa:
            await db.premium_analyses.update_one({"id": existing_pa["id"]}, {"$set": {"dossier_id": dossier_id}})
            logger.info(f"Dossier Express {dossier_id}: linked to existing premium_analyses {existing_pa['id']}")
        else:
            pa_id = str(uuid.uuid4())
            await db.premium_analyses.insert_one({
                "id": pa_id, "type": "dossier_express", "email": email, "name": name,
                "dossier_id": dossier_id, "status": "en_attente", "premium_pdf": premium_pdf,
                "amount": 0, "admin_test": True,
                "created_at": datetime.now(timezone.utc).isoformat()
            })
            logger.info(f"Dossier Express {dossier_id}: created premium_analyses entry {pa_id}")
    except Exception as e:
        logger.warning(f"Dossier Express {dossier_id}: premium_analyses registration failed (non-blocking): {e}")


@router.get("/dossier-express/{dossier_id}/download")
async def download_dossier_pdf(dossier_id: str, token: str = ""):
    """Public endpoint to download the Dossier Express PDF via a secure token."""
    if not token:
        raise HTTPException(status_code=400, detail="Token requis")
    dossier = await db.dossier_express.find_one(
        {"id": dossier_id, "download_token": token},
        {"_id": 0, "pdf_storage_path": 1, "status": 1, "name": 1}
    )
    if not dossier:
        raise HTTPException(status_code=404, detail="Lien de téléchargement invalide ou expiré")
    if dossier.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Le rapport n'est pas encore prêt")
    storage_path = dossier.get("pdf_storage_path")
    if not storage_path:
        raise HTTPException(status_code=404, detail="PDF non disponible")
    try:
        from utils.storage import download_file
        pdf_data, content_type = download_file(storage_path)
        from fastapi.responses import Response
        safe_name = (dossier.get("name") or "rapport").replace(" ", "-")
        filename = f"Rapport-Dossier-Express-{safe_name}.pdf"
        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"',
                "Cache-Control": "private, max-age=3600",
            },
        )
    except Exception as e:
        logger.error(f"PDF download error for {dossier_id}: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors du téléchargement")


@router.post("/dossier-express/checkout")
async def dossier_express_checkout(request: Request):
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Stripe non configure")
    body = await request.json()
    origin_url = body.get("origin_url", "").rstrip('/')
    email = body.get("email", "")
    name = body.get("name", "")
    premium_pdf = body.get("premium_pdf", False)
    analyse_premium = body.get("analyse_premium", False)

    # ====== LAUNCH MODE CHECK — SOFT LAUNCH GATING ======
    launch_config = await db.system_config.find_one({"key": "launch_mode"}, {"_id": 0})
    launch_mode = launch_config.get("value", "ouvert") if launch_config else "ouvert"
    if launch_mode == "indisponible":
        custom_msg = launch_config.get("message", "") if launch_config else ""
        raise HTTPException(
            status_code=503,
            detail=custom_msg or "Le service est temporairement suspendu pour maintenance programmee. Nous serons de retour tres prochainement."
        )

    # ====== PRE-PAYMENT LLM HEALTH CHECK — STRICTLY BLOCKING ======
    llm_ok, llm_reason = await _check_llm_health()
    if not llm_ok:
        logger.warning(f"Dossier Express checkout BLOCKED: LLM unavailable ({llm_reason}) for {email}")
        raise HTTPException(
            status_code=503,
            detail="Le service est momentanement indisponible pour finalisation technique. Merci de reessayer dans quelques instants."
        )

    amount = 97.00
    if premium_pdf:
        amount += 19.00
    if analyse_premium:
        amount += 49.00
    params = f"premium_pdf={'1' if premium_pdf else '0'}&analyse_premium={'1' if analyse_premium else '0'}"
    success_url = f"{origin_url}/dossier-express?payment=success&session_id={{CHECKOUT_SESSION_ID}}&{params}"
    cancel_url = f"{origin_url}/dossier-express?payment=cancelled"
    stripe_sdk.api_key = STRIPE_API_KEY
    tag = "dossier_express"
    if premium_pdf and analyse_premium:
        tag = "dossier_express_full"
    elif premium_pdf:
        tag = "dossier_express_pdf_pro"
    elif analyse_premium:
        tag = "dossier_express_analyse_premium"
    metadata = {"package_id": tag, "package_name": f"Dossier Express IA ({amount:.0f}€)", "customer_email": email, "customer_name": name, "premium_pdf": "1" if premium_pdf else "0", "analyse_premium": "1" if analyse_premium else "0"}
    if analyse_premium:
        await db.premium_analyses.insert_one({"id": str(uuid.uuid4()), "type": "dossier_express", "email": email, "name": name, "status": "en_attente", "relecture_expert_required": True, "premium_pdf": premium_pdf, "amount": amount, "created_at": datetime.now(timezone.utc).isoformat()})
        asyncio.create_task(notify_admin_premium_analysis("dossier_express", email, name, amount, options={"analyse_premium": True, "premium_pdf": premium_pdf}))
    try:
        session = await asyncio.to_thread(
            stripe_sdk.checkout.Session.create,
            payment_method_types=["card"],
            line_items=[{"price_data": {"currency": "eur", "product_data": {"name": metadata["package_name"]}, "unit_amount": int(amount * 100)}, "quantity": 1}],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata,
        )
        return {"success": True, "url": session.url, "session_id": session.id}
    except Exception as e:
        logger.error(f"Dossier Express IA checkout error: {e}")
        raise HTTPException(status_code=500, detail="Erreur de paiement")

@router.get("/dossier-express/suivi/{dossier_id}")
async def dossier_express_suivi(dossier_id: str, token: str = ""):
    """Public client-facing tracker — returns only premium, human-readable status."""
    dossier = await db.dossier_express.find_one({"id": dossier_id}, {"_id": 0})
    if not dossier:
        raise HTTPException(status_code=404, detail="Dossier non trouve")
    # Security: require download_token match
    if token and dossier.get("download_token") and token != dossier.get("download_token"):
        raise HTTPException(status_code=403, detail="Acces non autorise")

    # Map internal steps to premium client-facing labels
    STEP_MAP = {
        "checkout_valide":     {"order": 1, "label": "Dossier bien recu",                "done": True},
        "relance_admin":       {"order": 1, "label": "Dossier bien recu",                "done": True},
        "documents_recus":     {"order": 2, "label": "Documents en cours de preparation", "done": True},
        "extraction_en_cours": {"order": 3, "label": "Lecture documentaire en cours",     "done": True},
        "analyse_ia":          {"order": 4, "label": "Analyse en cours de finalisation",  "done": True},
        "pdf_en_cours":        {"order": 5, "label": "Rapport en cours de preparation",   "done": True},
        "stockage_en_cours":   {"order": 6, "label": "Rapport en cours de preparation",   "done": True},
        "email_en_cours":      {"order": 7, "label": "Envoi en cours",                    "done": True},
        "termine":             {"order": 8, "label": "Rapport disponible",                 "done": True},
        "erreur_ia":           {"order": 4, "label": "Verification complementaire en cours", "done": True},
        "erreur_pdf":          {"order": 5, "label": "Verification complementaire en cours", "done": True},
        "erreur_stockage":     {"order": 6, "label": "Verification complementaire en cours", "done": True},
        "erreur_email":        {"order": 7, "label": "Verification complementaire en cours", "done": True},
    }

    CLIENT_STEPS = [
        {"key": "received",    "label": "Dossier bien recu"},
        {"key": "preparation", "label": "Documents en cours de preparation"},
        {"key": "reading",     "label": "Lecture documentaire en cours"},
        {"key": "analysis",    "label": "Analyse en cours de finalisation"},
        {"key": "report",      "label": "Rapport en cours de preparation"},
        {"key": "delivery",    "label": "Envoi en cours"},
        {"key": "available",   "label": "Rapport disponible"},
    ]

    current_step = dossier.get("processing_step", "checkout_valide")
    status = dossier.get("status", "processing")
    delivery_status = dossier.get("delivery_status", "en_attente_traitement")
    step_info = STEP_MAP.get(current_step, {"order": 1, "label": "Dossier en cours de traitement", "done": True})

    is_incident = delivery_status == "incident_technique"
    is_completed = status == "completed"

    # Build steps with progress
    step_order = step_info["order"]
    if is_completed:
        step_order = 8

    steps_with_status = []
    order_map = [1, 2, 3, 4, 5, 7, 8]
    for i, s in enumerate(CLIENT_STEPS):
        s_order = order_map[i]
        if is_incident and s_order > step_order:
            steps_with_status.append({**s, "status": "waiting"})
        elif s_order < step_order:
            steps_with_status.append({**s, "status": "completed"})
        elif s_order == step_order:
            steps_with_status.append({**s, "status": "active" if not is_completed else "completed"})
        else:
            steps_with_status.append({**s, "status": "waiting"})

    # Client-facing message
    if is_completed:
        client_message = "Votre rapport est disponible. Vous pouvez le telecharger ci-dessous."
    elif is_incident:
        client_message = "Votre dossier est bien pris en charge. Un traitement complementaire est en cours pour vous garantir la meilleure qualite d'analyse."
    else:
        client_message = step_info["label"]

    result = {
        "dossier_id": dossier_id,
        "name": dossier.get("name", ""),
        "status": "completed" if is_completed else ("incident" if is_incident else "processing"),
        "message": client_message,
        "current_label": step_info["label"] if not is_completed else "Rapport disponible",
        "steps": steps_with_status,
        "created_at": dossier.get("created_at"),
        "completed_at": dossier.get("completed_at"),
    }

    if is_completed and dossier.get("download_token"):
        result["download_url"] = f"{SITE_URL}/api/dossier-express/{dossier_id}/download?token={dossier.get('download_token')}"

    return result


@router.get("/dossier-express/status/{dossier_id}")
async def dossier_express_status(dossier_id: str):
    dossier = await db.dossier_express.find_one({"id": dossier_id}, {"_id": 0, "documents_text": 0})
    if not dossier:
        raise HTTPException(status_code=404, detail="Dossier non trouve")
    return dossier

@router.get("/admin/dossier-express")
async def admin_dossier_express(admin: dict = Depends(get_current_admin)):
    dossiers = await db.dossier_express.find({}, {"_id": 0, "documents_text": 0, "analysis": 0}).sort("created_at", -1).to_list(100)
    stats = {
        "total": len(dossiers),
        "completed": sum(1 for d in dossiers if d.get("status") == "completed"),
        "processing": sum(1 for d in dossiers if d.get("status") == "processing"),
        "errors": sum(1 for d in dossiers if d.get("status") == "error"),
        "incidents": sum(1 for d in dossiers if d.get("delivery_status") == "incident_technique"),
        "delivered": sum(1 for d in dossiers if d.get("delivery_status") == "livre_client" or (d.get("status") == "completed" and not d.get("delivery_status"))),
        "pending": sum(1 for d in dossiers if d.get("delivery_status") == "en_attente_traitement" or (d.get("status") == "processing" and not d.get("delivery_status"))),
    }
    return {"items": dossiers, "stats": stats}


@router.post("/admin/dossier-express/{dossier_id}/retry")
async def admin_retry_dossier(dossier_id: str, admin: dict = Depends(get_current_admin)):
    """Admin endpoint to retry a failed dossier processing from scratch."""
    dossier = await db.dossier_express.find_one({"id": dossier_id}, {"_id": 0})
    if not dossier:
        raise HTTPException(status_code=404, detail="Dossier non trouve")
    if dossier.get("status") not in ("error",):
        raise HTTPException(status_code=400, detail="Seuls les dossiers en erreur peuvent etre relances")

    # Reset status
    await db.dossier_express.update_one({"id": dossier_id}, {"$set": {
        "status": "processing",
        "delivery_status": "en_attente_traitement",
        "processing_step": "relance_admin",
        "error": None,
        "retry_count": (dossier.get("retry_count", 0) + 1),
        "last_retry_at": datetime.now(timezone.utc).isoformat(),
        "retried_by": admin.get("email", "admin"),
    }})

    # Re-launch processing
    asyncio.create_task(_process_dossier_express(
        dossier_id,
        dossier.get("email", ""),
        dossier.get("name", ""),
        dossier.get("situation", ""),
        dossier.get("type_dossier", ""),
        dossier.get("regime", ""),
        dossier.get("documents_text", ""),
        premium_pdf=dossier.get("premium_pdf", False),
    ))

    logger.info(f"Admin retry launched for dossier {dossier_id} by {admin.get('email')}")
    return {"success": True, "message": "Relance en cours"}

@router.get("/dossier-express/weekly-count")
async def dossier_express_weekly_count():
    from datetime import timedelta
    now = datetime.now(timezone.utc)
    week_start = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    real_count = await db.dossier_express.count_documents({"created_at": {"$gte": week_start}})
    display_count = 12 + real_count
    return {"count": display_count, "period": "week"}


# ==================== STRATEGIIA ====================

# In-memory job store for async polling
_jobs = {}

def _llm_sync_call(api_key, session_id, system_message, user_text, provider, model):
    """Run Anthropic Claude LLM call synchronously (called via asyncio.to_thread)."""
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=6000,
        system=system_message,
        messages=[{"role": "user", "content": user_text}],
    )
    return response.content[0].text


async def _run_analysis(job_id, type_dossier, regime, situation, is_premium, email, similar_cases, case_context, is_admin_test=False):
    """Background task for LLM analysis with retry."""
    last_error = ""

    # ARTICULATION: If Dossier Express analysis exists for this email, inject as enriched context
    dossier_express_context = ""
    if email and is_premium:
        try:
            de_doc = await db.dossier_express.find_one(
                {"email": email.lower(), "status": "completed"},
                {"_id": 0, "analysis": 1, "document_details": 1}
            )
            if de_doc and de_doc.get("analysis"):
                dossier_express_context = f"""

CONTEXTE DOCUMENTAIRE ENRICHI (issu d'un Dossier Express IA precedemment realise pour ce client) :
{de_doc['analysis'][:4000]}

INSTRUCTION : Utilise cette matiere documentaire structuree pour affiner ta lecture strategique. Les pieces ont deja ete analysees par Dossier Express IA — tu peux t'appuyer sur ses conclusions pour produire une orientation plus precise et plus profonde. Ne repete pas l'analyse documentaire, concentre-toi sur la strategie et le pilotage."""
                logger.info(f"StrategiIA {job_id}: Enriched with Dossier Express context for {email}")
        except Exception as e:
            logger.warning(f"StrategiIA {job_id}: Failed to fetch Dossier Express context: {e}")

    for attempt in range(3):
        try:
            analysis_prompt = STRATEGIIA_PREMIUM_PROMPT if is_premium else STRATEGIIA_BASIC_PROMPT
            user_msg = f"""Type de dossier : {type_dossier}\nRegime : {regime}\nDescription de la situation : {situation}\n{case_context}{dossier_express_context}\n\n{analysis_prompt}"""
            session_id = f"strategiia_{str(uuid.uuid4())[:8]}"
            response = await asyncio.to_thread(
                _llm_sync_call, ANTHROPIC_API_KEY, session_id, STRATEGIIA_SYSTEM_PROMPT, user_msg, "anthropic", "claude-sonnet-4-5-20250929"
            )
            analysis_doc = {"id": str(uuid.uuid4()), "type_dossier": type_dossier, "regime": regime, "situation": situation[:500], "is_premium": is_premium, "email": email if email else "", "admin_test": is_admin_test, "created_at": datetime.now(timezone.utc).isoformat()}
            await db.strategiia_analyses.insert_one(analysis_doc)
            remaining = 3
            if not is_premium and email:
                now = datetime.now(timezone.utc)
                month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
                usage_count = await db.strategiia_analyses.count_documents({"email": email, "is_premium": False, "created_at": {"$gte": month_start}})
                remaining = max(0, 3 - usage_count)
            _jobs[job_id] = {"status": "done", "result": {"success": True, "analysis": response, "cases_found": len(similar_cases), "remaining": remaining}}
            return
        except Exception as e:
            last_error = str(e)
            logger.warning(f"StratégiIA attempt {attempt+1}/3 failed: {last_error}")
            if attempt < 2:
                await asyncio.sleep(3)
    logger.error(f"StratégiIA all 3 attempts failed: {last_error}")
    if "budget" in last_error.lower() or "exceeded" in last_error.lower():
        _jobs[job_id] = {"status": "error", "error": "Le service d'analyse IA est temporairement indisponible."}
    else:
        _jobs[job_id] = {"status": "error", "error": "L'analyse a échoué après plusieurs tentatives. Veuillez réessayer."}


@router.post("/strategiia/analyze")
async def strategiia_analyze(request: Request):
    body = await request.json()
    situation = body.get("situation", "")
    type_dossier = body.get("type_dossier", "")
    regime = body.get("regime", "")
    is_premium = body.get("premium", False)
    email = body.get("email", "").strip().lower()
    is_admin_test = body.get("admin_test", False)
    # Check admin token manually if admin_test requested
    if is_admin_test:
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                payload = jwt.decode(auth_header.split(" ", 1)[1], JWT_SECRET, algorithms=[JWT_ALGORITHM])
                is_admin_test = payload.get("is_admin", False)
            except Exception:
                is_admin_test = False
        else:
            is_admin_test = False
    if not situation.strip():
        raise HTTPException(status_code=400, detail="Description de la situation requise")
    if not ANTHROPIC_API_KEY:
        raise HTTPException(status_code=503, detail="Service IA non disponible")
    # Admin bypass: skip quota check
    if not is_admin_test and not is_premium and email:
        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
        usage_count = await db.strategiia_analyses.count_documents({"email": email, "is_premium": False, "created_at": {"$gte": month_start}})
        if usage_count >= 3:
            return {"success": False, "quota_exceeded": True, "remaining": 0, "message": "Vous avez utilisé vos 3 analyses gratuites ce mois-ci."}

    similar_cases = []
    if type_dossier:
        similar_cases = await db.cas_anonymises.find({"type_dossier": type_dossier}, {"_id": 0}).sort("score_pertinence", -1).to_list(5)
    case_context = ""
    if similar_cases:
        case_context = "\n\nCAS SIMILAIRES ANONYMISÉS DANS LA BASE :\n"
        for c in similar_cases:
            case_context += f"- Type: {c.get('type_dossier')}, Régime: {c.get('regime')}, Durée: {c.get('duree')}, Stratégie: {c.get('strategie')}, Résultat: {c.get('resultat')}, Score: {c.get('score_pertinence', 'N/A')}/100\n"

    job_id = str(uuid.uuid4())[:12]
    _jobs[job_id] = {"status": "pending"}
    asyncio.create_task(_run_analysis(job_id, type_dossier, regime, situation, is_premium, email, similar_cases, case_context, is_admin_test=is_admin_test))
    return {"job_id": job_id, "status": "pending", "admin_test": is_admin_test}


@router.get("/strategiia/status/{job_id}")
async def strategiia_status(job_id: str):
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Analyse non trouvée")
    if job["status"] == "done":
        result = job["result"]
        del _jobs[job_id]
        return {"status": "done", **result}
    elif job["status"] == "error":
        error = job["error"]
        del _jobs[job_id]
        return {"status": "error", "error": error}
    return {"status": "pending"}

@router.get("/strategiia/score")
async def get_relevance_score(type_dossier: str, regime: str = ""):
    query = {"type_dossier": type_dossier}
    if regime:
        query["regime"] = regime
    cases = await db.cas_anonymises.find(query, {"_id": 0, "resultat": 1, "score_pertinence": 1, "strategie": 1, "duree": 1}).to_list(500)
    total = len(cases)
    if total == 0 and regime:
        cases = await db.cas_anonymises.find({"type_dossier": type_dossier}, {"_id": 0, "resultat": 1, "score_pertinence": 1, "strategie": 1, "duree": 1}).to_list(500)
        total = len(cases)
    if total == 0:
        return {"score": None, "confidence": "insufficient_data", "total_cases": 0, "message": "Pas assez de cas similaires pour estimer un score de pertinence.", "distribution": {}}
    favorable = sum(1 for c in cases if c.get("resultat", "").lower() in ("favorable", "très favorable", "accepté", "accord"))
    defavorable = sum(1 for c in cases if c.get("resultat", "").lower() in ("défavorable", "refusé", "rejet", "refus"))
    en_cours = sum(1 for c in cases if c.get("resultat", "").lower() in ("en cours", "en attente", "partiel"))
    other = total - favorable - defavorable - en_cours
    scored_cases = [c for c in cases if c.get("score_pertinence") and c["score_pertinence"] > 0]
    avg_admin_score = round(sum(c["score_pertinence"] for c in scored_cases) / len(scored_cases)) if scored_cases else None
    decided = favorable + defavorable
    success_rate = round(favorable / decided * 100) if decided > 0 else None
    if success_rate is not None and avg_admin_score is not None:
        composite = round(success_rate * 0.6 + avg_admin_score * 0.4)
    elif success_rate is not None:
        composite = success_rate
    elif avg_admin_score is not None:
        composite = avg_admin_score
    else:
        composite = None
    confidence = "high" if total >= 20 else ("medium" if total >= 5 else "low")
    favorable_cases = [c for c in cases if c.get("resultat", "").lower() in ("favorable", "très favorable", "accepté", "accord")]
    strategies = {}
    for c in favorable_cases:
        s = c.get("strategie", "").strip()
        if s:
            strategies[s] = strategies.get(s, 0) + 1
    top_strategies = sorted(strategies.items(), key=lambda x: -x[1])[:3]
    return {"score": composite, "success_rate": success_rate, "avg_admin_score": avg_admin_score, "confidence": confidence, "total_cases": total, "distribution": {"favorable": favorable, "defavorable": defavorable, "en_cours": en_cours, "autre": other}, "top_strategies": [{"strategie": s, "count": c} for s, c in top_strategies], "message": f"Score basé sur {total} cas similaires ({confidence} confiance)."}


# ==================== DOSSIER QUALITY SCORE ====================

ESSENTIAL_DOCS_BY_TYPE = {
    "at": ["Certificat médical initial", "Déclaration d'accident", "Arrêt de travail", "Notification CPAM", "Bulletins de salaire"],
    "mp": ["Certificat médical initial", "Déclaration de maladie professionnelle", "Attestation d'exposition", "Notification CPAM", "Examens médicaux", "Fiche de poste"],
    "mdph": ["Formulaire Cerfa", "Certificat médical récent", "Justificatif d'identité", "Justificatif de domicile", "Bilans médicaux"],
    "assurance": ["Contrat d'assurance", "Déclaration de sinistre", "Courriers assureur", "Certificat médical", "Rapport d'expertise"],
    "expertise": ["Convocation expertise", "Certificats médicaux", "Historique médical", "Notification taux IPP"],
    "faute_inex": ["Certificat médical initial", "Déclaration d'accident", "Arrêt de travail", "Notification CPAM", "Preuves faute employeur"],
    "recours": ["Décision contestée", "Courrier de recours", "Certificat médical", "Pièces justificatives"],
}

@router.post("/strategiia/dossier-score")
async def get_dossier_score(request: Request):
    body = await request.json()
    type_dossier = body.get("type_dossier", "")
    regime = body.get("regime", "")
    situation = body.get("situation", "")
    doc_count = body.get("doc_count", 0)
    doc_names = body.get("doc_names", [])

    essential = ESSENTIAL_DOCS_BY_TYPE.get(type_dossier, ESSENTIAL_DOCS_BY_TYPE.get("at", []))

    # 1. Completeness score: documents provided vs essential
    matched = 0
    matched_docs = []
    missing_docs = []
    for ed in essential:
        ed_lower = ed.lower()
        found = False
        for dn in doc_names:
            if any(keyword in dn.lower() for keyword in ed_lower.split()):
                found = True
                break
        if found or doc_count >= len(essential):
            matched += 1
            matched_docs.append(ed)
        else:
            missing_docs.append(ed)

    completeness = round((matched / len(essential)) * 100) if essential else 100

    # 2. Coherence score: situation detail + type match
    coherence = 50
    if situation:
        word_count = len(situation.split())
        if word_count >= 80:
            coherence = 100
        elif word_count >= 40:
            coherence = 80
        elif word_count >= 20:
            coherence = 60
    if type_dossier and regime:
        coherence = min(100, coherence + 10)

    # 3. Key documents presence score
    key_doc_score = 100 if doc_count >= 3 else round((doc_count / 3) * 100)

    # Composite score
    composite = round(completeness * 0.45 + coherence * 0.30 + key_doc_score * 0.25)

    # Pedagogical tips
    tips = []
    if completeness < 80:
        tips.append(f"Ajoutez les documents manquants : {', '.join(missing_docs[:3])}")
    if coherence < 70:
        tips.append("Détaillez davantage votre situation (dates, faits, conséquences) pour une analyse plus précise")
    if key_doc_score < 100:
        tips.append(f"Fournissez au moins 3 pièces justificatives ({doc_count}/3 actuellement)")
    if not tips:
        tips.append("Votre dossier est bien constitué. L'analyse sera optimale.")

    # Score level
    if composite >= 80:
        level = "excellent"
        level_label = "Excellent"
        level_color = "green"
    elif composite >= 60:
        level = "bon"
        level_label = "Bon"
        level_color = "blue"
    elif composite >= 40:
        level = "moyen"
        level_label = "A compléter"
        level_color = "orange"
    else:
        level = "faible"
        level_label = "Insuffisant"
        level_color = "red"

    return {
        "score": composite,
        "level": level,
        "level_label": level_label,
        "level_color": level_color,
        "details": {
            "completeness": {"score": completeness, "label": "Complétude des documents", "matched": len(matched_docs), "total": len(essential)},
            "coherence": {"score": coherence, "label": "Richesse de la description"},
            "key_documents": {"score": key_doc_score, "label": "Pièces justificatives", "count": doc_count},
        },
        "missing_documents": missing_docs,
        "tips": tips,
    }

@router.get("/strategiia/quota/{email}")
async def strategiia_quota(email: str):
    email = email.strip().lower()
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    usage_count = await db.strategiia_analyses.count_documents({"email": email, "is_premium": False, "created_at": {"$gte": month_start}})
    remaining = max(0, 3 - usage_count)
    return {"remaining": remaining, "limit": 3, "used": min(usage_count, 3)}

@router.post("/strategiia/register-email")
async def strategiia_register_email(request: Request):
    body = await request.json()
    email = body.get("email", "").strip().lower()
    is_admin_test = body.get("admin_test", False)
    # Check admin token manually if admin_test requested
    if is_admin_test:
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            try:
                payload = jwt.decode(auth_header.split(" ", 1)[1], JWT_SECRET, algorithms=[JWT_ALGORITHM])
                is_admin_test = payload.get("is_admin", False)
            except Exception:
                is_admin_test = False
        else:
            is_admin_test = False
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Email invalide")
    # Admin test: don't create leads, return unlimited quota
    if is_admin_test:
        return {"success": True, "email": email, "remaining": 999, "admin_test": True}
    await db.leads.update_one({"email": email}, {"$set": {"email": email, "source": "strategiia_readwall", "updated_at": datetime.now(timezone.utc).isoformat()}, "$setOnInsert": {"created_at": datetime.now(timezone.utc).isoformat()}}, upsert=True)
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    usage_count = await db.strategiia_analyses.count_documents({"email": email, "is_premium": False, "created_at": {"$gte": month_start}})
    remaining = max(0, 3 - usage_count)
    return {"success": True, "email": email, "remaining": remaining}

@router.post("/strategiia/checkout")
async def strategiia_checkout(request: Request):
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Stripe non configuré")
    body = await request.json()
    origin_url = body.get("origin_url", "").rstrip('/')
    email = body.get("email", "")
    analysis_context = body.get("context", "")
    premium_pdf = body.get("premium_pdf", False)
    analyse_premium = body.get("analyse_premium", False)
    amount = 29.00
    if premium_pdf:
        amount += 19.00
    if analyse_premium:
        amount += 29.00
    params = f"premium_pdf={'1' if premium_pdf else '0'}&analyse_premium={'1' if analyse_premium else '0'}"
    success_url = f"{origin_url}/simulateur?strategiia=success&session_id={{CHECKOUT_SESSION_ID}}&{params}"
    cancel_url = f"{origin_url}/simulateur?strategiia=cancelled"
    stripe_sdk.api_key = STRIPE_API_KEY
    product_tag = "strategiia_premium"
    if premium_pdf and analyse_premium:
        product_tag = "strategiia_premium_full"
    elif premium_pdf:
        product_tag = "strategiia_premium_pdf"
    elif analyse_premium:
        product_tag = "strategiia_analyse_premium"
    metadata = {"product": product_tag, "customer_email": email, "context": analysis_context[:200], "premium_pdf": "1" if premium_pdf else "0", "analyse_premium": "1" if analyse_premium else "0"}
    if analyse_premium:
        await db.premium_analyses.insert_one({"id": str(uuid.uuid4()), "type": "strategiia", "email": email, "context": analysis_context[:500], "status": "en_attente", "premium_pdf": premium_pdf, "analyse_premium": True, "relecture_expert_required": True, "amount": amount, "created_at": datetime.now(timezone.utc).isoformat()})
        asyncio.create_task(notify_admin_premium_analysis("strategiia", email, "", amount, options={"analyse_premium": True, "premium_pdf": premium_pdf, "context": analysis_context[:300]}))
    try:
        session = await asyncio.to_thread(
            stripe_sdk.checkout.Session.create,
            payment_method_types=["card"],
            line_items=[{"price_data": {"currency": "eur", "product_data": {"name": f"StratégiIA Premium ({amount:.0f}€)"}, "unit_amount": int(amount * 100)}, "quantity": 1}],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata,
        )
        return {"url": session.url, "session_id": session.id}
    except Exception as e:
        logger.error(f"StratégiIA checkout error: {e}")
        raise HTTPException(status_code=500, detail="Erreur de paiement")


@router.post("/strategiia/admin-bypass-premium")
async def strategiia_admin_bypass(request: Request):
    """Admin bypass: skips Stripe checkout and runs premium analysis directly."""
    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token manquant")
    token = auth_header.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if not payload.get("is_admin"):
            raise HTTPException(status_code=403, detail="Non autorisé")
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalide")
    body = await request.json()
    situation = body.get("situation", "")
    type_dossier = body.get("type_dossier", "")
    regime = body.get("regime", "")
    premium_pdf = body.get("premium_pdf", False)
    analyse_premium = body.get("analyse_premium", False)
    email = payload.get("email", "admin@test")
    if not situation.strip() or not ANTHROPIC_API_KEY:
        raise HTTPException(status_code=400, detail="Situation requise et service IA actif")
    similar_cases = []
    if type_dossier:
        similar_cases = await db.cas_anonymises.find({"type_dossier": type_dossier}, {"_id": 0}).sort("score_pertinence", -1).to_list(5)
    case_context = ""
    if similar_cases:
        case_context = "\n\nCAS SIMILAIRES ANONYMISÉS DANS LA BASE :\n"
        for c in similar_cases:
            case_context += f"- Type: {c.get('type_dossier')}, Régime: {c.get('regime')}, Durée: {c.get('duree')}, Stratégie: {c.get('strategie')}, Résultat: {c.get('resultat')}, Score: {c.get('score_pertinence', 'N/A')}/100\n"
    job_id = str(uuid.uuid4())[:12]
    _jobs[job_id] = {"status": "pending"}
    asyncio.create_task(_run_analysis(job_id, type_dossier, regime, situation, True, email, similar_cases, case_context, is_admin_test=True))
    return {"job_id": job_id, "status": "pending", "admin_test": True, "premium_pdf": premium_pdf, "analyse_premium": analyse_premium}


@router.post("/dossier-express/admin-bypass")
async def dossier_express_admin_bypass(request: Request):
    """Admin bypass: process Dossier Express without Stripe payment."""
    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token manquant")
    token = auth_header.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if not payload.get("is_admin"):
            raise HTTPException(status_code=403, detail="Non autorisé")
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalide")
    body = await request.json()
    email = payload.get("email", "admin@test")
    name = body.get("name", "Admin Test")
    situation = body.get("situation", "")
    type_dossier = body.get("type_dossier", "")
    regime = body.get("regime", "")
    documents_text = body.get("documents_text", "")
    premium_pdf = body.get("premium_pdf", False)
    document_details = body.get("document_details", [])
    original_documents = body.get("original_documents", [])
    if not situation.strip():
        raise HTTPException(status_code=400, detail="Description requise")
    dossier_id = str(uuid.uuid4())
    dossier_doc = {
        "id": dossier_id, "email": email, "name": name, "situation": situation[:5000],
        "type_dossier": type_dossier, "regime": regime,
        "documents_text": documents_text[:10000], "document_details": document_details,
        "original_documents": original_documents,
        "premium_pdf": premium_pdf,
        "status": "processing", "payment_verified": True, "admin_test": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.dossier_express.insert_one(dossier_doc)
    asyncio.create_task(_process_dossier_express(dossier_id, email, name, situation, type_dossier, regime, documents_text, premium_pdf=premium_pdf))
    return {"success": True, "dossier_id": dossier_id, "admin_test": True}

@router.post("/strategiia/generate-pdf")
async def strategiia_generate_pdf(request: Request):
    body = await request.json()
    analysis = body.get("analysis", "")
    type_dossier = body.get("type_dossier", "")
    regime = body.get("regime", "")
    name = body.get("name", "")
    premium_pdf = body.get("premium_pdf", False)
    if not analysis:
        raise HTTPException(status_code=400, detail="Analyse requise")
    pdf_bytes = generate_secured_pdf(analysis=analysis, report_type="StrategiIA", name=name, type_dossier=type_dossier, regime=regime, with_watermark=not premium_pdf)
    encoded = base64.b64encode(pdf_bytes).decode("utf-8")
    return {"pdf_base64": encoded, "filename": "strategiia-rapport.pdf"}


# ==================== CAS ANONYMISES ====================

@router.get("/admin/cas-anonymises")
async def get_cas_anonymises(admin: dict = Depends(get_current_admin)):
    cases = await db.cas_anonymises.find({}, {"_id": 0}).sort("created_at", -1).to_list(500)
    return {"items": cases, "total": len(cases)}

@router.post("/admin/cas-anonymises")
async def create_cas_anonymise(request: Request, admin: dict = Depends(get_current_admin)):
    body = await request.json()
    cas = {"id": str(uuid.uuid4()), "type_dossier": body.get("type_dossier", ""), "regime": body.get("regime", ""), "duree": body.get("duree", ""), "strategie": body.get("strategie", ""), "resultat": body.get("resultat", ""), "score_pertinence": body.get("score_pertinence", 0), "notes": body.get("notes", ""), "created_at": datetime.now(timezone.utc).isoformat()}
    await db.cas_anonymises.insert_one(cas)
    return {"success": True, "id": cas["id"]}

@router.delete("/admin/cas-anonymises/{case_id}")
async def delete_cas_anonymise(case_id: str, admin: dict = Depends(get_current_admin)):
    await db.cas_anonymises.delete_one({"id": case_id})
    return {"success": True}

@router.patch("/admin/cas-anonymises/{case_id}")
async def update_cas_anonymise(case_id: str, request: Request, admin: dict = Depends(get_current_admin)):
    body = await request.json()
    update = {}
    for field in ["type_dossier", "regime", "duree", "strategie", "resultat", "score_pertinence", "notes"]:
        if field in body:
            update[field] = body[field]
    update["updated_at"] = datetime.now(timezone.utc).isoformat()
    result = await db.cas_anonymises.update_one({"id": case_id}, {"$set": update})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Cas non trouvé")
    return {"success": True}

@router.post("/admin/cas-anonymises/import")
async def import_cas_anonymises(request: Request, admin: dict = Depends(get_current_admin)):
    body = await request.json()
    cases_data = body.get("cases", [])
    if not cases_data or not isinstance(cases_data, list):
        raise HTTPException(status_code=400, detail="Format invalide: 'cases' doit être une liste")
    imported = 0
    for item in cases_data[:100]:
        cas = {"id": str(uuid.uuid4()), "type_dossier": item.get("type_dossier", ""), "regime": item.get("regime", ""), "duree": item.get("duree", ""), "strategie": item.get("strategie", ""), "resultat": item.get("resultat", ""), "score_pertinence": item.get("score_pertinence", 0), "notes": item.get("notes", ""), "created_at": datetime.now(timezone.utc).isoformat()}
        await db.cas_anonymises.insert_one(cas)
        imported += 1
    return {"success": True, "imported": imported}

@router.get("/admin/cas-anonymises/stats")
async def get_cas_stats(admin: dict = Depends(get_current_admin)):
    total = await db.cas_anonymises.count_documents({})
    pipeline = [{"$group": {"_id": "$type_dossier", "count": {"$sum": 1}}}]
    by_type = await db.cas_anonymises.aggregate(pipeline).to_list(50)
    pipeline_regime = [{"$group": {"_id": "$regime", "count": {"$sum": 1}}}]
    by_regime = await db.cas_anonymises.aggregate(pipeline_regime).to_list(50)
    return {"total": total, "by_type": [{k: v for k, v in d.items() if k != "_id"} | {"label": d["_id"] or "Non précisé"} for d in by_type], "by_regime": [{k: v for k, v in d.items() if k != "_id"} | {"label": d["_id"] or "Non précisé"} for d in by_regime]}

@router.get("/admin/strategiia/stats")
async def get_strategiia_stats(admin: dict = Depends(get_current_admin)):
    total_analyses = await db.strategiia_analyses.count_documents({})
    premium = await db.strategiia_analyses.count_documents({"is_premium": True})
    total_cases = await db.cas_anonymises.count_documents({})
    recent = await db.strategiia_analyses.find({}, {"_id": 0}).sort("created_at", -1).to_list(20)
    return {"total_analyses": total_analyses, "premium": premium, "total_cases": total_cases, "recent": recent}
