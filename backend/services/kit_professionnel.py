"""
Kit Professionnel — Pipeline IA Admin
Generation confidentielle reservee a l'admin S.E.S.
Reutilise le texte OCR deja extrait (zero double extraction).

Prompts versionnes : lus depuis MongoDB collection 'kit_pro_prompts' avec fallback codé.
"""
import asyncio
import os
from datetime import datetime, timezone
from config import db, logger
from utils.llm import generate_section_llmchat, llm_call

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
KIT_MODEL_NAME = "claude-sonnet-4-5-20250929"
KIT_PROMPT_VERSION_DEFAULT = "v1.0"

# ============================================================
# PROMPTS PAR DEFAUT (code-defined) — utilises comme fallback
# si MongoDB est vide ou indisponible.
# Editables depuis l'admin via la collection 'kit_pro_prompts'.
# ============================================================

KIT_SYSTEM_PROMPT_DEFAULT = (
    "Tu es l'Assistant Metier Senior interne de Strategie & Expertise Sante. "
    "Tu rediges un KIT PROFESSIONNEL CONFIDENTIEL destine STRICTEMENT a l'usage interne du fondateur. "
    "Ton public : un expert metier qui va utiliser ce kit comme support operationnel pour piloter le suivi client. "
    "Ton requis : technique, juridiquement precis, operationnel, sans complaisance. "
    "INTERDICTION : ce document ne sera JAMAIS lu par le client. Tu peux donc etre direct, citer des montants, "
    "des delais juridiques, des risques, des angles d'attaque sans precaution oratoire. "
    "Tu cites systematiquement les articles de loi (CSS, CASF), tableaux MP, jurisprudences avec references exactes "
    "(juridiction + date + n) quand tu en as la certitude. Si pas de reference exacte, tu ecris 'jurisprudence constante'. "
    "Tu n'inventes JAMAIS de donnees. "
    "Tu cites NOMINATIVEMENT chaque expert medical (Dr Nom complet + date) presents dans le dossier. "
    "Ton francais : professionnel, sobre, sans emojis."
)

KIT_SECTION_PROMPTS_DEFAULT = {
    "synthese_strategique": """Redige UNIQUEMENT la section :
## 1. SYNTHESE STRATEGIQUE
3 a 5 lignes maximum. Le coeur du dossier : probleme central, voie de resolution recommandee, niveau d'urgence (forclusion, prescription), levier business principal.
Commence directement par ## 1. SYNTHESE STRATEGIQUE""",

    "diagnostic_juridique": """Redige UNIQUEMENT la section :
## 2. DIAGNOSTIC JURIDIQUE STRUCTURE
- Regime applicable (AT/MP/AAH/Faute inexcusable/autre) avec article precis
- Points de droit cles (3-5 points numerotes)
- Jurisprudences mobilisables (avec references)
- Risques juridiques identifies (3-5 risques avec consequence chiffree si possible)
Commence directement par ## 2. DIAGNOSTIC JURIDIQUE STRUCTURE""",

    "plan_action_chronologique": """Redige UNIQUEMENT la section :
## 3. PLAN D'ACTION CHRONOLOGIQUE
Tableau d'actions priorisees. Pour chaque action :
- Echeance (J+X jours) ou date butoir absolue (forclusion)
- Action precise
- Destinataire (CPAM, CMRA, tribunal judiciaire pole social, employeur, MDPH...)
- Piece a produire ou demande a formuler
5 a 8 actions numerotees du plus urgent au moins urgent.
Commence directement par ## 3. PLAN D'ACTION CHRONOLOGIQUE""",

    "lettres_types": """Redige UNIQUEMENT la section :
## 4. LETTRES-TYPES PRETES A PERSONNALISER
Genere 2 a 3 lettres TYPES adaptees au dossier (ex: contestation taux IPP a la CMRA, saisine pole social du tribunal judiciaire, demande de pieces medicales a la CPAM, mise en demeure employeur faute inexcusable).
Pour CHAQUE lettre :
- Titre clair (ex: LETTRE 1 - Contestation taux IPP / CMRA)
- Destinataire (institution + adresse type)
- Objet juridique precis avec references CSS
- Corps de lettre redige : 8-15 lignes avec articles de loi cites
- Formule de politesse adaptee
Commence directement par ## 4. LETTRES-TYPES PRETES A PERSONNALISER""",

    "arguments_contestation": """Redige UNIQUEMENT la section :
## 5. ARGUMENTS DE CONTESTATION & NEGOCIATION
- Arguments offensifs (3-5) en faveur du client avec base legale
- Contre-arguments anticipes (3-4) que l'adversaire/CPAM va probablement opposer
- Reponses preparees a ces contre-arguments
- Points de vigilance dans la phase contradictoire
Commence directement par ## 5. ARGUMENTS DE CONTESTATION & NEGOCIATION""",

    "pieces_a_reclamer": """Redige UNIQUEMENT la section :
## 6. PIECES A RECLAMER AU CLIENT
Liste exhaustive et hierarchisee des pieces manquantes ou a obtenir pour completer le dossier :
- Pieces medicales (preciser : comptes rendus, examens specifiques, expertises a demander)
- Pieces administratives (bulletins de salaire, attestations employeur, notifications CPAM/MDPH)
- Pieces de procedure (LRAR, accuses, decisions anterieures)
Pour chaque piece : indique l'organisme detenteur et le delai d'obtention estime.
Commence directement par ## 6. PIECES A RECLAMER AU CLIENT""",

    "calendrier_suivi": """Redige UNIQUEMENT la section :
## 7. CALENDRIER DE SUIVI
Plan de relance et points de controle :
- J+15 : objet du suivi + action interne
- J+30 : point intermediaire (que verifier, qui contacter)
- J+60 : bilan operationnel
- J+90 : reorientation strategique si necessaire
Si forclusion imminente, signale-la en tete de section.
Commence directement par ## 7. CALENDRIER DE SUIVI""",
}

KIT_SECTIONS_ORDER = [
    "synthese_strategique",
    "diagnostic_juridique",
    "plan_action_chronologique",
    "lettres_types",
    "arguments_contestation",
    "pieces_a_reclamer",
    "calendrier_suivi",
]


async def ensure_kit_prompts_seeded():
    """Pre-remplit MongoDB avec les prompts par defaut si la collection est vide.
    Garde-fou : appele au demarrage du backend pour garantir qu'on ne crash jamais."""
    try:
        existing = await db.kit_pro_prompts.find_one({"_id": "current"})
        if existing:
            return
        doc = {
            "_id": "current",
            "version": KIT_PROMPT_VERSION_DEFAULT,
            "model": KIT_MODEL_NAME,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "system_prompt": KIT_SYSTEM_PROMPT_DEFAULT,
            "section_prompts": KIT_SECTION_PROMPTS_DEFAULT,
        }
        await db.kit_pro_prompts.insert_one(doc)
        logger.info(f"[KIT_PRO][SEED] Initial prompts seeded version={KIT_PROMPT_VERSION_DEFAULT}")
    except Exception as e:
        logger.warning(f"[KIT_PRO][SEED] Failed (non-blocking, fallback to code defaults): {e}")


async def get_active_kit_prompts():
    """Lit les prompts versionnes depuis MongoDB avec fallback systematique vers les valeurs codees."""
    try:
        doc = await db.kit_pro_prompts.find_one({"_id": "current"})
        if doc and doc.get("system_prompt") and doc.get("section_prompts"):
            return {
                "system": doc["system_prompt"],
                "sections": doc["section_prompts"],
                "version": doc.get("version", KIT_PROMPT_VERSION_DEFAULT),
            }
    except Exception as e:
        logger.warning(f"[KIT_PRO] MongoDB read failed, using code fallback: {e}")
    # Fallback codé garanti
    return {
        "system": KIT_SYSTEM_PROMPT_DEFAULT,
        "sections": KIT_SECTION_PROMPTS_DEFAULT,
        "version": f"{KIT_PROMPT_VERSION_DEFAULT}-fallback",
    }


async def generate_kit_professionnel(dossier_id: str) -> dict:
    """
    Genere un kit professionnel admin pour un dossier donne.
    Reutilise le texte OCR deja stocke. Generation sequentielle (Semaphore 1).
    """
    logger.info(f"[KIT_PRO][{dossier_id}] Start generation")

    # Charger le dossier + texte OCR existant (zero double extraction)
    dossier = await db.dossier_express.find_one({"id": dossier_id}, {"_id": 0})
    if not dossier:
        raise Exception(f"Dossier {dossier_id} introuvable")

    # Reutiliser le texte OCR + le rapport client deja genere (schema MongoDB existant)
    documents_text = dossier.get("documents_text", "") or dossier.get("extracted_documents_text", "") or ""
    client_report = dossier.get("analysis", "") or dossier.get("ai_report", "") or ""
    name = dossier.get("name", "")
    type_dossier = dossier.get("type_dossier", "")
    regime = dossier.get("regime", "")
    situation = dossier.get("situation", "")

    if not documents_text and not client_report:
        raise Exception(f"Aucune donnee analysable pour dossier {dossier_id}")

    # Limiter le texte pour respecter le contexte LLM (120k chars = ~30-40k tokens)
    DOCS_LIMIT = 100_000
    docs_truncated = documents_text[:DOCS_LIMIT] if documents_text else ""

    context = f"""DOSSIER ADMIN — Reference interne : {dossier_id}
Client : {name}
Type : {type_dossier} | Regime : {regime}

SITUATION CLIENT (declarative) :
{situation}

RAPPORT CLIENT DEJA GENERE (Dossier Express IA) :
{client_report[:30_000] if client_report else "(non disponible)"}

DOCUMENTS OCR EXTRAITS :
{docs_truncated if docs_truncated else "(aucun document texte exploitable)"}
"""

    # Lecture des prompts versionnes (MongoDB) avec fallback codé
    active_prompts = await get_active_kit_prompts()
    system_prompt = active_prompts["system"]
    section_prompts = active_prompts["sections"]
    prompt_version = active_prompts["version"]
    logger.info(f"[KIT_PRO][{dossier_id}] Using prompts version={prompt_version}")

    # Generation sequentielle (Semaphore implicite : appels en serie)
    # Strategie : essai PATH B (Emergent stream) puis fallback PATH A (Anthropic SDK direct)
    results = {}
    for section_id in KIT_SECTIONS_ORDER:
        prompt = section_prompts.get(section_id) or KIT_SECTION_PROMPTS_DEFAULT.get(section_id, "")
        user_msg = f"{context}\n\n{prompt}"
        text = None
        # PATH B — Emergent proxy stream
        try:
            text = await generate_section_llmchat(
                section_id, system_prompt, user_msg, f"kit_{dossier_id}",
                max_tokens=2500, retries=2
            )
        except Exception as e_proxy:
            logger.warning(f"[KIT_PRO][{dossier_id}] section {section_id} PATH B (proxy) FAILED: {str(e_proxy)[:120]} — fallback PATH A native")
            # PATH A — Anthropic SDK direct (resilience)
            if ANTHROPIC_API_KEY:
                try:
                    text = await asyncio.wait_for(
                        llm_call(
                            ANTHROPIC_API_KEY, f"kit_{dossier_id}_{section_id}",
                            system_prompt, user_msg,
                            "anthropic", KIT_MODEL_NAME, max_tokens=2500
                        ),
                        timeout=120.0
                    )
                    logger.info(f"[KIT_PRO][{dossier_id}] section {section_id} PATH A native SUCCESS")
                except Exception as e_native:
                    logger.error(f"[KIT_PRO][{dossier_id}] section {section_id} PATH A also FAILED: {str(e_native)[:120]}")
                    text = None

        if text and text.strip():
            results[section_id] = text.strip()
            logger.info(f"[KIT_PRO][{dossier_id}] section {section_id} OK ({len(text)} chars)")
        else:
            logger.error(f"[KIT_PRO][{dossier_id}] section {section_id} TOTAL FAILURE")
            results[section_id] = "## Erreur generation\n\nLa generation de cette section a echoue (LLM indisponible). Cliquez sur 'Re-generer' pour reessayer."
        await asyncio.sleep(1)  # leger souffle pour RAM

    # Persist
    kit_doc = {
        "dossier_id": dossier_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "regenerated_count": 0,
        "admin_notes": "",
        **results,
    }

    # Si deja un kit existe, incrementer le compteur regen
    existing = await db.kit_professionnel.find_one({"dossier_id": dossier_id}, {"_id": 0})
    if existing:
        kit_doc["regenerated_count"] = (existing.get("regenerated_count", 0) or 0) + 1
        kit_doc["admin_notes"] = existing.get("admin_notes", "")  # preserve notes
        await db.kit_professionnel.update_one({"dossier_id": dossier_id}, {"$set": kit_doc})
    else:
        await db.kit_professionnel.insert_one(kit_doc)

    logger.info(f"[KIT_PRO][{dossier_id}] Stored OK ({len([k for k in results if results[k]])} sections)")
    return kit_doc


async def trigger_kit_generation_background(dossier_id: str):
    """Background task non-bloquant declenche apres envoi PDF client."""
    try:
        await asyncio.sleep(3)  # laisser le pipeline client finir proprement
        await generate_kit_professionnel(dossier_id)
    except Exception as e:
        logger.exception(f"[KIT_PRO][BACKGROUND][{dossier_id}] FAILED: {e}")
