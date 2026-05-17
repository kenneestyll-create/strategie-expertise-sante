"""Agents Registry — exposes prompts and metadata for the admin org chart.

Reads prompts in real-time from source files so the admin always sees current state.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from utils.auth import get_current_admin
import os
import re
import io
import importlib
from datetime import datetime

router = APIRouter()


def _read_var_from_module(module_path: str, var_name: str) -> str:
    """Return the *current* value of a string variable from a Python module.

    Imports the module fresh to reflect any hot-reloaded changes.
    """
    try:
        spec_path = module_path.replace("/", ".").replace(".py", "")
        # Already-imported modules are returned from sys.modules; reload to be safe.
        mod = importlib.import_module(spec_path)
        importlib.reload(mod)
        val = getattr(mod, var_name, None)
        if isinstance(val, str):
            return val
        return ""
    except Exception:
        return ""


def _agent_card(*, id: str, name: str, role: str, mission: str, model: str,
                file_path: str, prompt_var: str, source_module: str | None = None,
                guardrails: list[str] | None = None, kpis: dict | None = None) -> dict:
    """Build one agent card with the live prompt loaded from its source file."""
    prompt_text = ""
    if source_module and prompt_var:
        prompt_text = _read_var_from_module(source_module, prompt_var)
    if not prompt_text and os.path.isfile(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            file_text = f.read()
        # Best-effort extract: triple-quoted block following `VAR_NAME = """`
        m = re.search(rf"{re.escape(prompt_var)}\s*=\s*['\"]{{3}}(.+?)['\"]{{3}}", file_text, re.DOTALL)
        if m:
            prompt_text = m.group(1).strip()
    return {
        "id": id,
        "name": name,
        "role": role,
        "mission": mission,
        "model": model,
        "file_path": file_path,
        "prompt_var": prompt_var,
        "prompt": prompt_text,
        "guardrails": guardrails or [],
        "kpis": kpis or {},
    }


@router.get("/admin/agents/registry")
async def get_agents_registry(admin: dict = Depends(get_current_admin)):
    """Return the org chart of all AI agents with their live prompts (admin only)."""
    agents = [
        _agent_card(
            id="strate",
            name="Straté",
            role="Réceptionniste IA",
            mission="Conciergerie : accueille le visiteur, qualifie son besoin via 12 routes déterministes, oriente vers le bon CTA (RDV, Dossier Express, StratégIA, guide).",
            model="Déterministe + Claude Haiku 4.5 (uniquement pour classification 'Autre situation')",
            file_path="/app/backend/utils/strate_prompts.py",
            prompt_var="FREE_TEXT_SYSTEM_PROMPT",
            source_module="utils.strate_prompts",
            guardrails=[
                "100% déterministe sur les 12 routes principales (pas d'hallucination possible)",
                "Filtre RGPD/NIR en amont (refus de traiter les données sensibles)",
                "Tracking de chaque interaction pour les KPI Admin",
            ],
        ),
        _agent_card(
            id="strategiia",
            name="StratégIA",
            role="Analyse stratégique premium",
            mission="Produit un rapport stratégique PDF (10-15 pages) à partir d'un dossier client : lecture juridique, axes de défense, plan d'action.",
            model="Claude Sonnet 4.5",
            file_path="/app/backend/constants/prompts.py",
            prompt_var="STRATEGIIA_SYSTEM_PROMPT",
            source_module="constants.prompts",
            guardrails=[
                "Aucune jurisprudence sans n° de pourvoi exact",
                "Aucun pourcentage / montant sans réserve 'selon les données publiques, à actualiser'",
                "Disclaimer obligatoire : 'outil d'aide à la décision, pas un avis juridique'",
                "Bloc anti-inversion : silence MDPH = rejet, RSDAE ≥ 1 an, IPP 10%, AT 48h",
            ],
        ),
        _agent_card(
            id="dossier_express",
            name="Dossier Express IA",
            role="Pré-expertise documentaire",
            mission="Analyse un lot de documents AT/MP/MDPH du client et produit une pré-expertise structurée (forces, faiblesses, alertes).",
            model="Claude Sonnet 4.5",
            file_path="/app/backend/constants/prompts.py",
            prompt_var="DOSSIER_EXPRESS_SYSTEM_PROMPT",
            source_module="constants.prompts",
            guardrails=[
                "Articles de loi vérifiés uniquement (L.411-1, L.461-1, L.821-2, etc.)",
                "Aucun nom propre, aucune donnée médicale sensible",
                "Réserve obligatoire sur les chiffres",
                "Bloc anti-inversion identique à StratégIA",
            ],
        ),
        _agent_card(
            id="editorial_planner",
            name="Planner Éditorial",
            role="Architecte d'article SEO",
            mission="À partir d'un sujet, produit un plan structuré : 3 H1 candidats, slug, méta-description, 5-7 sections H2/H3, 6-8 questions FAQ.",
            model="Claude Haiku 4.5",
            file_path="/app/backend/routes/editorial.py",
            prompt_var="SYSTEM_PROMPT_PLAN",
            source_module="routes.editorial",
            guardrails=[
                "Aucune jurisprudence inventée — base interne uniquement",
                "JSON structuré strict (5 sections max, 6-8 FAQ)",
                "Slug ASCII normalisé, méta ≤ 158 chars",
            ],
        ),
        _agent_card(
            id="editorial_writer",
            name="Writer Éditorial",
            role="Rédacteur de sections",
            mission="Rédige chaque section H2 du brouillon en parallèle, avec auto-retry des sections défaillantes (hooks fermés, fin de phrase complète).",
            model="Claude Haiku 4.5",
            file_path="/app/backend/routes/editorial.py",
            prompt_var="SYSTEM_PROMPT_DRAFT",
            source_module="routes.editorial",
            guardrails=[
                "Longueur stricte 250-380 mots/section",
                "TerrainHooks ASCII fermés correctement",
                "Bloc anti-inversion intégré",
                "Aucun % inventé (interdiction explicite type '95%')",
                "Post-check + auto-retry des sections défaillantes",
            ],
        ),
        _agent_card(
            id="editorial_critic",
            name="Critic Juridique",
            role="Auditeur qualité (NOUVEAU)",
            mission="Audite le brouillon : détecte chaque référence légale, jurisprudence, chiffre ou inversion potentielle. NE rédige PAS, AUDITE et propose des corrections ciblées.",
            model="Claude Haiku 4.5",
            file_path="/app/backend/routes/editorial.py",
            prompt_var="SYSTEM_PROMPT_CRITIC",
            source_module="routes.editorial",
            guardrails=[
                "Sortie JSON stricte avec verdict (clean/warnings/critical)",
                "Détection des 6 inversions juridiques critiques",
                "Préfère faux positif à faux négatif (exigence maximale)",
                "Propose une correction ciblée pour chaque violation",
                "N'accepte aucune jurisprudence sans n° de pourvoi exact",
            ],
        ),
        _agent_card(
            id="editorial_structurer",
            name="Structurer Éditorial",
            role="Mise en forme publishable",
            mission="Convertit le brouillon markdown en JSON structuré (réponse rapide, contexte, blocages, erreurs, stratégie, orientation, FAQ, maillage) aligné sur le schéma seo_pages.",
            model="Claude Haiku 4.5",
            file_path="/app/backend/routes/editorial.py",
            prompt_var="SYSTEM_PROMPT_STRUCTURE",
            source_module="routes.editorial",
            guardrails=[
                "Schéma JSON strict 11 clés obligatoires",
                "Parser tolérant via json_repair (récupère les JSON malformés IA)",
                "Préserve références légales du brouillon, n'en ajoute aucune",
                "5 blocages, 5 erreurs, 5 orientations, 6-8 FAQ exactement",
            ],
        ),
    ]

    # ============================================================
    # CATEGORIE : Outils internes admin (confidentiel admin-only)
    # ============================================================
    internal_agents = []
    try:
        # Lecture en temps réel du prompt versionné Kit Pro (MongoDB > fallback code)
        from services.kit_professionnel import (
            get_active_kit_prompts, KIT_MODEL_NAME, KIT_SECTIONS_ORDER
        )
        active = await get_active_kit_prompts()
        kit_system_prompt = active["system"]
        kit_version = active["version"]
        # Concaténer les sous-prompts dans une vue lisible
        sections_view = "\n\n".join(
            f"### Section : {sid}\n{active['sections'].get(sid, '')}"
            for sid in KIT_SECTIONS_ORDER
        )
        full_prompt = (
            f"=== SYSTEM PROMPT (rôle de l'agent) ===\n{kit_system_prompt}\n\n"
            f"=== SOUS-PROMPTS PAR SECTION (7 sections) ===\n{sections_view}"
        )
        internal_agents.append({
            "id": "kit_professionnel",
            "name": "Kit Professionnel IA",
            "role": "Assistant Métier Admin (CONFIDENTIEL)",
            "mission": (
                "Génère automatiquement après chaque dossier client un kit professionnel CONFIDENTIEL "
                "destiné strictement à l'usage interne. Transforme l'analyse Dossier Express en plan d'action "
                "opérationnel structuré : 7 sections (synthèse, diagnostic juridique, plan d'action, lettres-types, "
                "arguments, pièces à réclamer, calendrier). Versioning du prompt depuis MongoDB. JAMAIS transmis au client."
            ),
            "model": f"{KIT_MODEL_NAME} (Claude Sonnet 4.5)",
            "file_path": "/app/backend/services/kit_professionnel.py",
            "prompt_var": f"kit_pro_prompts (MongoDB) · version: {kit_version}",
            "prompt": full_prompt,
            "guardrails": [
                "⚠️ STRICTEMENT CONFIDENTIEL — Document jamais transmis au client",
                "Validation humaine obligatoire avant tout envoi à un tiers",
                "Déclenchement automatique en background après chaque dossier finalisé (non bloquant)",
                "Génération séquentielle (Sémaphore implicite) — préservation RAM 512MB",
                "Double fallback LLM : PATH B (proxy Emergent) → PATH A (Anthropic SDK direct)",
                "Versioning prompt depuis MongoDB avec fallback code si indisponible",
                "Authentification admin obligatoire sur les 4 endpoints",
                "Pas de double extraction OCR : réutilise documents_text + analysis du dossier",
            ],
            "kpis": {
                "categorie": "🔒 Outils internes admin",
                "sections_generees": 7,
                "version_prompt": kit_version,
                "endpoints_admin": 4,
            },
            "category": "internal",
        })
    except Exception as e:
        # Garde-fou : si le registry échoue à charger Kit Pro, on n'affiche rien plutôt que de crasher
        import logging
        logging.getLogger(__name__).warning(f"Kit Pro agent card load failed: {e}")

    return {
        "ceo": {"name": "PDG Fondateur", "role": "Vision, stratégie, validation finale"},
        "agents": agents,
        "internal_agents": internal_agents,
    }


@router.get("/admin/agents/registry/pdf")
async def get_agents_registry_pdf(admin: dict = Depends(get_current_admin)):
    """Generate a downloadable PDF of the AI org chart with full system prompts."""
    from utils.pdf_agents_org import generate_agents_org_pdf

    payload = await get_agents_registry(admin=admin)
    try:
        pdf_bytes = generate_agents_org_pdf(payload)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {e}")

    filename = f"organigramme-ia-ses-{datetime.now().strftime('%Y%m%d')}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
