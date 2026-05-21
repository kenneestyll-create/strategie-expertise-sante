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
    If var_name contains ``|`` (e.g. "VAR_A | VAR_B"), concatenates the values
    of each named variable separated by a labelled divider — used by agents
    whose prompt is split across multiple constants (e.g. Video Factory).
    """
    try:
        spec_path = module_path.replace("/", ".").replace(".py", "")
        mod = importlib.import_module(spec_path)
        importlib.reload(mod)
        if "|" in var_name:
            parts = []
            for v in [x.strip() for x in var_name.split("|") if x.strip()]:
                val = getattr(mod, v, None)
                if isinstance(val, str) and val:
                    parts.append(f"=== {v} ===\n{val}")
            return "\n\n".join(parts)
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
        _agent_card(
            id="video_factory",
            name="Video Factory Engine",
            role="Production vidéo + SEO + Preview/Voix-off/Export/Tracking + Scene Engine V1 (V4.4)",
            mission="Produit en 1 appel LLM un pack vidéo court (TikTok/Shorts/Reels) : hook×3, script 70-150 mots, storyboard 6 plans, sous-titres .srt, pack SEO, CTA unique + UTM, conversion_score, disclaimer. Modes : forced/weighted/fallback/free. Boucle V2 : poids par format normalisés (views/CTR/conv), floor 10%, garde monoculture 65%/7j. V3 : page SEO d'atterrissage STRICTEMENT dérivée du pack vidéo (CTA verbatim, UTM différencié). V4.1 : couche rendering — lecteur 9:16 TikTok-style + voix-off OpenAI TTS HD via Emergent LLM Key (5 voix : Onyx/Sage/Alloy/Nova/Coral), MP3 base64 stocké par vidéo. V4.2 : export client-side .webm 9:16 720×1280 VP9 via MediaRecorder + AudioContext, sous-titres incrustés style TikTok (mode D1 phrase par scène, highlights or sur MAJUSCULES et chiffres), durée max 60s, ZÉRO endpoint backend. V4.3 : light tracking — mini-dialog 'Marquer publié' capture plateforme (tiktok/youtube/instagram/other) + URL publique optionnelle, stocke published/published_at/publish_platform/publish_public_url dans videos[idx]. V4.4 (Scene Engine V1) : moteur motion-design Canvas 2D pur (zéro WebGL/Three.js/Remotion). 5 scènes registered (stats_focus, alert_urgency, legal_balance, office_admin, testimony_quote) + 7 motion rules (F1=pédagogique calm 0.75x, F2=statistique punch, F3=témoignage amber, F4=juridique dramatic bordeaux, F5=admin indigo, F6=urgence high red 1.25x +shake3px, F7=mix orange 1.15x +shake2px). Mapping F1-F7→scene_type 100% backend déterministe. Source unique de vérité preview↔export (même classe Scene + update/draw). Fallback V4.2 automatique sur vidéos sans scene_type (rétro-compat totale).",
            model="Claude Haiku 4.5 (script) + OpenAI tts-1-hd (voix off) + Canvas 2D Scene Engine (render) + MediaRecorder VP9 (export)",
            file_path="/app/backend/utils/video_agent.py",
            prompt_var="SYSTEM_PROMPT | SEO_LANDING_SYSTEM_PROMPT",
            source_module="utils.video_agent",
            guardrails=[
                "7 formats verrouillés F1-F7 (aucune invention/fusion possible)",
                "CTA mapping urgence→service en règle dure (faible→0€, moyen→29€, critique→97€)",
                "Override Python du CTA après LLM (anti-divergence absolue, garantie 100%)",
                "Compliance regex backend : 'garanti / 100% / CPAM ment / promesse financière' → fail",
                "Page SEO V3 ne peut JAMAIS diverger du pack vidéo (CTA copié verbatim, UTM différencié)",
                "Floor exploration ε-greedy 10% par format + garde monoculture 65%/7j → reroll",
                "Log JSON structuré info-level par génération (audit-able : video_id, format, mode, weights_snapshot, conversion_score, ts)",
                "Schéma JSON strict (Pydantic) + retry unique sur JSON malformé (température 0.1)",
                "V4.1 — Voix-off : la couche TTS ne modifie JAMAIS le script généré V3 (texte lu = videos[idx].script intégral, garde-fou anti-régénération)",
                "V4.1 — Stockage base64 dans videos[idx].voice_over (additif, ne casse aucun consommateur V1/V2/V3 existant)",
                "V4.2 — Export client-side uniquement (MediaRecorder + AudioContext) : aucun endpoint backend, aucune dépendance serveur, aucune fuite de données",
                "V4.2 — Bouton Export DÉSACTIVÉ si voice_over absent (garde-fou UX : pas de vidéo muette accidentelle)",
                "V4.2 — Durée d'export bornée à 60s max avec warning UI explicite (anti-OOM navigateur sur scripts trop longs)",
                "V4.3 — Platform regex stricte ^(tiktok|youtube|instagram|other)$ (anti-injection, anti-typo)",
                "V4.3 — public_url borné à 500 caractères + validation http(s):// côté UI (anti-XSS, anti-spam)",
                "V4.3 — Rétro-compat totale du PATCH /status : si video_idx absent, comportement V1 inchangé (zero breaking change)",
                "V4.4 — Scene Engine déterministe : mapping F1-F7 → scene_type fixé côté backend (aucune hallucination LLM possible)",
                "V4.4 — SceneFactory.create renvoie null si scene_type inconnu/absent → fallback V4.2 systématique (rétro-compat 100%)",
                "V4.4 — Camera shake borné ±3px sur 150ms max (interdiction structurelle de dépasser, charte sobriété S.E.S)",
                "V4.4 — Auto-degrade FPS via probe 10 frames avant export : si > 33ms/frame moyenne → 24 FPS (jamais sous, jamais de drop audio)",
                "V4.4 — Preview et export utilisent EXACTEMENT le même renderer Canvas 2D (zéro divergence visuelle entre lecture et fichier final)",
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
