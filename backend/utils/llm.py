"""
CONSOLIDATION_ARCHITECTURE — Fonctions LLM centralisees.
Fournit toutes les fonctions d'appel LLM (sync, async, stream, multi-stage).
Consomme : constants/prompts.py, config.py
Consommateurs : routes/strategiia.py, routes/dossier_express.py

# =========================================================================
# ZONE GELEE — MOTEUR IA V1 VALIDE
# Date de gel : 05/04/2026
# Perimetre : Pipeline LLM complet (sync, async, stream, multi-stage).
#   Inclut : llm_call, llm_sync_call, llm_async_call, llm_stream_call,
#   generate_section_llmchat, generate_dossier_report_multistage.
# Avertissement : AUCUNE modification sans ordre explicite du responsable.
#   Toute evolution future doit suivre le protocole IA_BASELINE_V1.md.
# =========================================================================
"""
import os
import asyncio
from config import db, logger

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
EMERGENT_LLM_KEY = os.environ.get("EMERGENT_LLM_KEY", "")


def has_llm_key() -> bool:
    """Check if any LLM key is available."""
    return bool(ANTHROPIC_API_KEY) or bool(EMERGENT_LLM_KEY)


async def check_llm_health() -> dict:
    """Health check for LLM services."""
    native = bool(ANTHROPIC_API_KEY)
    emergent = bool(EMERGENT_LLM_KEY)
    mode = "native" if native else ("emergent_fallback" if emergent else "none")
    return {"native_anthropic": native, "emergent_key": emergent, "mode": mode}


def llm_sync_call(api_key, session_id, system_message, user_text, provider, model, max_tokens=6000):
    """Run LLM call synchronously. Native Anthropic SDK if key available."""
    import anthropic
    if api_key:
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_message,
            messages=[{"role": "user", "content": user_text}],
        )
        return response.content[0].text
    raise Exception("Cle Anthropic native requise pour appel synchrone")


async def llm_stream_call(messages, model, max_tokens=4000):
    """Single streaming LLM call via httpx to Emergent proxy. Handles 60s gateway timeout."""
    import httpx
    import json as json_mod
    from emergentintegrations.llm.utils import get_integration_proxy_url
    proxy_url = get_integration_proxy_url()
    url = f"{proxy_url}/llm/chat/completions"
    headers = {"Authorization": f"Bearer {EMERGENT_LLM_KEY}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": messages, "max_tokens": max_tokens, "stream": True}
    async with httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=30.0)) as client:
        async with client.stream("POST", url, headers=headers, json=payload) as resp:
            if resp.status_code != 200:
                await resp.aread()
                raise Exception(f"LLM proxy error {resp.status_code}")
            full_text = ""
            async for line in resp.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data.strip() == "[DONE]":
                        break
                    try:
                        chunk = json_mod.loads(data)
                        content = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        if content:
                            full_text += content
                    except (json_mod.JSONDecodeError, IndexError, KeyError):
                        pass
    return full_text


async def llm_async_call(session_id, system_message, user_text, model):
    """Async LLM call via Emergent Universal Key. Service-aware split to handle 60s proxy timeout."""
    from constants.prompts import STRATEGIIA_SYSTEM_COMPACT

    is_strategiia_premium = "PILOTAGE STRATEGIQUE APPROFONDI" in user_text
    is_dossier_express = "DOSSIER EXPRESS IA" in user_text or "PRE-EXPERTISE DOCUMENTAIRE" in user_text

    if not is_strategiia_premium and not is_dossier_express:
        # StrategiIA basic — lightweight single call
        msgs = [{"role": "system", "content": system_message}, {"role": "user", "content": user_text}]
        result = await llm_stream_call(msgs, model, max_tokens=3000)
        if not result.strip():
            raise Exception("Reponse LLM vide")
        return result

    if is_dossier_express:
        # DOSSIER EXPRESS — split into 2 sequential calls (legacy path, multi-stage preferred)
        situation_block = user_text[:2500]

        de_part1 = f"""{situation_block}

Redige un rapport de PRE-EXPERTISE DOCUMENTAIRE pour Dossier Express IA.
INSTRUCTION : Genere UNIQUEMENT les sections suivantes.
## Synthese du dossier (8-10 lignes, resume la situation, les pieces, les enjeux)
## Analyse des pieces transmises (inventaire, pertinence, coherence documentaire)
## Cadre juridique applicable (articles de loi, tableaux MP, jurisprudences pertinentes)
## Points forts du dossier (elements favorables, preuve solide)
## Points de vigilance et pieces manquantes (lacunes, risques, documents a obtenir)
Commence directement par ## Synthese du dossier."""

        de_part2 = f"""{situation_block}

Suite du rapport de PRE-EXPERTISE DOCUMENTAIRE pour Dossier Express IA.
INSTRUCTION : Genere UNIQUEMENT les sections suivantes.
## Strategie recommandee (orientation, recours, demarches prioritaires)
## Estimation des prejudices (si applicable : IP, PGPF, DFT, souffrances endurees)
## Plan d action detaille (5-7 actions numerotees avec delais concrets)
## Conclusion et recommandation finale (4-5 lignes, ton professionnel et rassurant)
Commence directement par ## Strategie recommandee."""

        de_sys = "Tu es l'expert Dossier Express IA de Strategie & Expertise Sante. Specialise en analyse documentaire de dossiers de maladies professionnelles et accidents du travail. Reponds en francais. Cite textes de loi et jurisprudences. Sois precis et exhaustif."

        p1 = await llm_stream_call([{"role": "system", "content": de_sys}, {"role": "user", "content": de_part1}], model, max_tokens=3000)
        if not p1.strip():
            raise Exception("Reponse LLM vide (Dossier Express partie 1)")
        logger.info(f"[DOSSIER_EXPRESS][{session_id}] Part1 OK — {len(p1)} chars")
        await asyncio.sleep(2)
        p2 = await llm_stream_call([{"role": "system", "content": de_sys}, {"role": "user", "content": de_part2}], model, max_tokens=3000)
        if not p2.strip():
            raise Exception("Reponse LLM vide (Dossier Express partie 2)")
        logger.info(f"[DOSSIER_EXPRESS][{session_id}] Part2 OK — {len(p2)} chars, TOTAL={len(p1)+len(p2)} chars")
        return p1.strip() + "\n\n" + p2.strip()

    # STRATEGIIA PREMIUM — 2 PARALLEL calls
    situation_block = user_text[:2000]

    part1_prompt = f"""{situation_block}

Genere un rapport de pilotage strategique approfondi.
INSTRUCTION : Genere UNIQUEMENT les sections 1 a 5 ci-dessous.
## Votre situation analysee (5-6 lignes, ton empathique, montre que tu as compris)
## Lecture strategique du dossier (6-8 lignes, qualifie le dossier, identifie enjeu et frein)
## Cadre juridique applicable (4-5 lignes, cite articles et jurisprudences)
## Leviers prioritaires identifies (4-6 leviers concrets avec chiffres si possible)
## Points de vigilance (4-5 points, formules de maniere rassurante)
Commence directement par ## Votre situation analysee."""

    part2_prompt = f"""{situation_block}

Genere la SUITE d'un rapport de pilotage strategique approfondi.
INSTRUCTION : Genere UNIQUEMENT les sections 6 a 9 ci-dessous.
## Angles potentiellement sous-exploites (3-4 angles concrets que le client n'a pas envisages)
## Evaluation et perspectives (5-6 lignes avec estimation financiere si applicable)
## Plan d action recommande (5 actions numerotees avec delais concrets)
## Notre engagement a vos cotes (4-5 lignes, termine EXACTEMENT par :
**Vous n'etes plus seul(e) face a votre situation.**
**Desormais, Strategie & Expertise Sante devient votre bouclier.**)
Commence directement par ## Angles potentiellement sous-exploites."""

    msgs1 = [{"role": "system", "content": STRATEGIIA_SYSTEM_COMPACT}, {"role": "user", "content": part1_prompt}]
    msgs2 = [{"role": "system", "content": STRATEGIIA_SYSTEM_COMPACT}, {"role": "user", "content": part2_prompt}]

    part1, part2 = await asyncio.gather(
        llm_stream_call(msgs1, model, max_tokens=3000),
        llm_stream_call(msgs2, model, max_tokens=2500),
    )

    if not part1.strip():
        raise Exception("Reponse LLM vide (partie 1)")
    if not part2.strip():
        raise Exception("Reponse LLM vide (partie 2)")
    logger.info(f"[STRATEGIIA][{session_id}] Parallel OK — Part1={len(part1)} chars, Part2={len(part2)} chars")

    return part1.strip() + "\n\n" + part2.strip()


async def llm_call(api_key, session_id, system_message, user_text, provider, model, max_tokens=6000):
    """Unified LLM call — native Anthropic in thread if key, else Emergent async fallback."""
    if api_key:
        return await asyncio.to_thread(
            llm_sync_call, api_key, session_id, system_message, user_text, provider, model, max_tokens
        )
    if EMERGENT_LLM_KEY:
        return await llm_async_call(session_id, system_message, user_text, model)
    raise Exception("Aucune cle IA disponible")


async def generate_section_llmchat(section_id: str, system_msg: str, user_msg: str,
                                     dossier_id: str, max_tokens: int = 1500, retries: int = 2) -> str:
    """Generate a single report section via httpx streaming (truly async for parallel batches).
    Returns the generated text or raises Exception on total failure."""
    msgs = [{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}]
    for attempt in range(retries):
        try:
            text = await llm_stream_call(msgs, "claude-sonnet-4-5-20250929", max_tokens=max_tokens)
            if not text.strip():
                raise Exception(f"Section {section_id}: reponse vide")
            logger.info(f"[DOSSIER_EXPRESS][{dossier_id}][{section_id}] OK attempt={attempt+1} chars={len(text)}")
            return text.strip()
        except Exception as e:
            logger.warning(f"[DOSSIER_EXPRESS][{dossier_id}][{section_id}] attempt={attempt+1}/{retries} failed: {str(e)[:120]}")
            if attempt < retries - 1:
                await asyncio.sleep(3)
    raise Exception(f"Section {section_id}: toutes les tentatives echouees")


async def generate_dossier_report_multistage(dossier_id: str, name: str, type_dossier: str,
                                                regime: str, situation: str, documents_text: str,
                                                case_context: str) -> str:
    """Multi-stage pipeline: generates Dossier Express report in 7 focused sections.
    Each section stays under the 60s proxy timeout. Sections run in parallel batches.
    Returns the assembled full report or raises Exception on failure."""

    context = f"""Client : {name}
Type de dossier : {type_dossier}
Regime : {regime}

SITUATION :
{situation}

DOCUMENTS FOURNIS :
{documents_text[:8000] if documents_text else "(Aucun document textuel fourni)"}
{case_context}"""

    SYSTEM = (
        "Tu es l'expert Dossier Express IA de Strategie & Expertise Sante. "
        "Specialise en analyse documentaire de dossiers de maladies professionnelles et accidents du travail. "
        "Tu t'appuies sur les jurisprudences (Cass. soc. 2019 obligation securite, Cass. 2e civ. 2020 IPP incidence professionnelle, "
        "Cass. 2e civ. 2022 silence CPAM vaut acceptation), les statistiques CNAM, les baremes IPP, "
        "l'incidence professionnelle (IP) et la PGPF. "
        "REGLES : Reponds en francais. Verification croisee x3. Nuance intelligente. "
        "Cite textes de loi et jurisprudences. Ne genere aucune URL. "
        "Ce rapport est un outil d'aide a la decision, pas un avis juridique."
    )

    sections_def = [
        ("synthese", f"""{context}

Redige UNIQUEMENT la section suivante du rapport de PRE-EXPERTISE DOCUMENTAIRE :
## Synthese du dossier
Resume factuel de la situation : contexte professionnel du client, pathologie, type de procedure engagee, cadre juridique applicable, textes de loi pertinents, enjeux identifies. 8-10 lignes minimum. Montre que tu as compris la matiere documentaire.
Commence directement par ## Synthese du dossier"""),

        ("pieces", f"""{context}

Redige UNIQUEMENT la section suivante du rapport de PRE-EXPERTISE DOCUMENTAIRE :
## Pieces detectees
Liste structuree des categories documentaires reconnues dans les pieces fournies. Pour chaque categorie, indique le nombre de pieces et une description courte.
Categories possibles : Certificats medicaux, Comptes rendus specialises (IRM, scanner, EMG), Arrets de travail, Expertises medicales, Courriers administratifs, Decisions/notifications, Examens/imagerie, Attestations/correspondances.
Montre ce que tu as reconnu et exploite, pas seulement ce que tu as compte.
Commence directement par ## Pieces detectees"""),

        ("chrono", f"""{context}

Redige UNIQUEMENT la section suivante du rapport de PRE-EXPERTISE DOCUMENTAIRE :
## Chronologie synthetique du dossier
Reconstitue une frise chronologique a partir des dates detectees dans les documents. Structure en etapes :
- Debut des troubles / fait generateur
- Premiers soins / examens
- Arrets de travail (periodes)
- Expertises et evaluations
- Aggravations ou episodes significatifs
- Decisions administratives
Commence directement par ## Chronologie synthetique du dossier"""),

        ("juridique", f"""{context}

Redige UNIQUEMENT la section suivante du rapport de PRE-EXPERTISE DOCUMENTAIRE :
## Cadre juridique applicable
Articles de loi pertinents, tableaux de maladies professionnelles concernes, jurisprudences de reference (Cass. soc., Cass. 2e civ., CE), baremes IPP applicables. Cite au moins 3 textes ou jurisprudences precises avec dates. Analyse l'applicabilite au cas present.
Commence directement par ## Cadre juridique applicable"""),

        ("forces_vigilance", f"""{context}

Redige UNIQUEMENT les 2 sections suivantes du rapport de PRE-EXPERTISE DOCUMENTAIRE :
## Points forts du dossier
Elements favorables identifies dans les pieces : preuves solides, coherences entre documents, elements medico-administratifs robustes. Explique POURQUOI chaque point est un atout strategique.
## Points de vigilance et pieces manquantes
Lacunes documentaires, incoherences detectees, risques identifies, documents supplementaires a obtenir pour renforcer le dossier. Formulations nuancees.
Commence directement par ## Points forts du dossier"""),

        ("strategie_prejudices", f"""{context}

Redige UNIQUEMENT les 2 sections suivantes du rapport de PRE-EXPERTISE DOCUMENTAIRE :
## Strategie recommandee
Orientation strategique, voies de recours pertinentes, demarches prioritaires, instances competentes. Justifie tes recommandations.
## Estimation des prejudices
Si applicable : Incidence Professionnelle (IP), Perte de Gains Professionnels Futurs (PGPF), Deficit Fonctionnel Temporaire (DFT), souffrances endurees, prejudice d'agrement. Donne des fourchettes chiffrees quand les elements le permettent. Mentionne l'aide juridictionnelle si le profil le suggere.
Commence directement par ## Strategie recommandee"""),

        ("plan_conclusion", f"""{context}

Redige UNIQUEMENT les 2 sections suivantes du rapport de PRE-EXPERTISE DOCUMENTAIRE :
## Plan d'action detaille
5 a 7 actions numerotees avec delais concrets et interlocuteurs identifies. Chaque action doit etre actionnable immediatement.
## Conclusion et recommandation finale
4-5 lignes, ton professionnel et rassurant. Rappelle les points cles, la strategie recommandee et que ce rapport constitue une base fiable pour la suite de l'accompagnement.
Commence directement par ## Conclusion et recommandation finale"""),
    ]

    results = {}
    batch_plan = [
        (["synthese", "pieces", "chrono"], "Batch 1/3"),
        (["juridique", "forces_vigilance"], "Batch 2/3"),
        (["strategie_prejudices", "plan_conclusion"], "Batch 3/3"),
    ]

    sections_map = {s[0]: s[1] for s in sections_def}

    progress_labels = {
        "Batch 1/3": "analyzing_1",
        "Batch 2/3": "analyzing_2",
        "Batch 3/3": "analyzing_3",
    }

    for batch_keys, batch_label in batch_plan:
        logger.info(f"[DOSSIER_EXPRESS][{dossier_id}] {batch_label}: {batch_keys}")

        progress_key = progress_labels.get(batch_label, "analyzing")
        try:
            await db.dossier_express.update_one(
                {"id": dossier_id},
                {"$set": {"progress_step": progress_key, "analysis_batch": batch_label}}
            )
        except Exception:
            pass

        tasks = [
            generate_section_llmchat(key, SYSTEM, sections_map[key], dossier_id)
            for key in batch_keys
        ]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        for key, result in zip(batch_keys, batch_results):
            if isinstance(result, Exception):
                logger.error(f"[DOSSIER_EXPRESS][{dossier_id}] Section {key} FAILED: {result}")
                raise result
            results[key] = result

        if batch_label != "Batch 3/3":
            await asyncio.sleep(2)

    section_order = ["synthese", "pieces", "chrono", "juridique", "forces_vigilance", "strategie_prejudices", "plan_conclusion"]
    report_parts = [results[k] for k in section_order if k in results]
    full_report = "\n\n".join(report_parts)

    total_chars = len(full_report)
    logger.info(f"[DOSSIER_EXPRESS][{dossier_id}] REPORT ASSEMBLED: {total_chars} chars, {len(report_parts)}/7 sections")
    return full_report
