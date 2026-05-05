"""Agents Snapshot — capture the live state of the AI agents ecosystem.

Used by the versioning/audit system. Reads prompts, red-flag patterns, model config
and legal base count, then computes a stable hash for deduplication.
"""
import hashlib
import importlib
import json
import re
from datetime import datetime, timezone


def _import_fresh(module_path: str):
    mod = importlib.import_module(module_path)
    importlib.reload(mod)
    return mod


def _get_var(module_path: str, var: str, default=""):
    try:
        m = _import_fresh(module_path)
        return getattr(m, var, default)
    except Exception:
        return default


def _extract_red_flag_patterns() -> list:
    """Read the patterns list from routes/editorial.py::_scan_red_flags source."""
    try:
        with open("/app/backend/routes/editorial.py", "r", encoding="utf-8") as f:
            src = f.read()
        m = re.search(r"patterns\s*=\s*\[(.*?)\]\s*\n\s*for pat,", src, re.DOTALL)
        if not m:
            return []
        block = m.group(1)
        # Each pattern line: (r"...", "kind", "severity"),
        items = []
        for line in block.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            tm = re.match(r"\(\s*r?\"(.*?)\"\s*,\s*\"(\w+)\"\s*,\s*\"(\w+)\"\s*\)", line)
            if tm:
                items.append({
                    "pattern": tm.group(1),
                    "kind": tm.group(2),
                    "severity": tm.group(3),
                })
        return items
    except Exception:
        return []


async def capture_state(db) -> dict:
    """Capture the current state of all agents, prompts, red flags, models, legal base.

    Returns a serialisable dict ready to be stored as a snapshot document.
    """
    # Agents (live registry — reuses agents_registry logic for prompts)
    from routes.agents_registry import _agent_card

    agents = [
        _agent_card(
            id="strate", name="Straté", role="Réceptionniste IA",
            mission="Conciergerie",
            model="Déterministe + Claude Haiku 4.5",
            file_path="/app/backend/utils/strate_prompts.py",
            prompt_var="FREE_TEXT_SYSTEM_PROMPT",
            source_module="utils.strate_prompts",
        ),
        _agent_card(
            id="strategiia", name="StratégIA", role="Analyse stratégique premium",
            mission="Rapport stratégique premium",
            model="Claude Sonnet 4.5",
            file_path="/app/backend/constants/prompts.py",
            prompt_var="STRATEGIIA_SYSTEM_PROMPT",
            source_module="constants.prompts",
        ),
        _agent_card(
            id="dossier_express", name="Dossier Express IA", role="Pré-expertise documentaire",
            mission="Pré-expertise documentaire",
            model="Claude Sonnet 4.5",
            file_path="/app/backend/constants/prompts.py",
            prompt_var="DOSSIER_EXPRESS_SYSTEM_PROMPT",
            source_module="constants.prompts",
        ),
        _agent_card(
            id="editorial_planner", name="Planner Éditorial", role="Architecte d'article SEO",
            mission="Plan structuré",
            model="Claude Haiku 4.5",
            file_path="/app/backend/routes/editorial.py",
            prompt_var="SYSTEM_PROMPT_PLAN",
            source_module="routes.editorial",
        ),
        _agent_card(
            id="editorial_writer", name="Writer Éditorial", role="Rédacteur de sections",
            mission="Rédige les sections en parallèle",
            model="Claude Haiku 4.5",
            file_path="/app/backend/routes/editorial.py",
            prompt_var="SYSTEM_PROMPT_DRAFT",
            source_module="routes.editorial",
        ),
        _agent_card(
            id="editorial_critic", name="Critic Juridique", role="Auditeur qualité",
            mission="Audite le brouillon",
            model="Claude Haiku 4.5",
            file_path="/app/backend/routes/editorial.py",
            prompt_var="SYSTEM_PROMPT_CRITIC",
            source_module="routes.editorial",
        ),
        _agent_card(
            id="editorial_structurer", name="Structurer Éditorial", role="Mise en forme publishable",
            mission="Convertit le brouillon en JSON structuré",
            model="Claude Haiku 4.5",
            file_path="/app/backend/routes/editorial.py",
            prompt_var="SYSTEM_PROMPT_STRUCTURE",
            source_module="routes.editorial",
        ),
    ]

    # Strip non-essential fields and keep only what matters for audit
    agents_audit = [{
        "id": a["id"],
        "name": a["name"],
        "role": a["role"],
        "model": a["model"],
        "prompt_var": a["prompt_var"],
        "file_path": a["file_path"],
        "prompt": a.get("prompt", ""),
    } for a in agents]

    # Red flag patterns (governance rule)
    red_flag_patterns = _extract_red_flag_patterns()

    # Legal base — DB-backed
    legal_refs_count = 0
    legal_refs_sample = []
    try:
        legal_refs_count = await db.editorial_legal_refs.count_documents({})
        legal_refs_sample = await db.editorial_legal_refs.find(
            {}, {"_id": 0, "label": 1, "kind": 1}
        ).limit(20).to_list(20)
    except Exception:
        pass

    # Workflow / IA params (extracted from editorial.py source)
    workflow_config = {
        "writer_max_tokens": 1400,
        "plan_max_tokens": 3000,
        "critic_max_tokens": 3500,
        "structure_max_tokens": 4500,
        "section_legal_refs_limit": 50,
        "plan_legal_refs_limit": 30,
    }

    state = {
        "agents": agents_audit,
        "red_flag_patterns": red_flag_patterns,
        "red_flag_count": len(red_flag_patterns),
        "legal_refs_count": legal_refs_count,
        "legal_refs_sample": legal_refs_sample,
        "workflow_config": workflow_config,
    }
    return state


def compute_hash(state: dict) -> str:
    """Deterministic SHA256 of the snapshot state."""
    canonical = json.dumps(state, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def compute_diff(prev: dict | None, curr: dict) -> list[str]:
    """Return human-readable list of major changes between two states."""
    if not prev:
        return ["Snapshot initial — aucune version antérieure"]

    changes = []

    # Agents
    prev_by_id = {a["id"]: a for a in prev.get("agents", [])}
    curr_by_id = {a["id"]: a for a in curr.get("agents", [])}

    added = set(curr_by_id) - set(prev_by_id)
    removed = set(prev_by_id) - set(curr_by_id)
    for aid in sorted(added):
        changes.append(f"Agent ajouté : {curr_by_id[aid]['name']}")
    for aid in sorted(removed):
        changes.append(f"Agent supprimé : {prev_by_id[aid]['name']}")

    for aid in sorted(set(curr_by_id) & set(prev_by_id)):
        p, c = prev_by_id[aid], curr_by_id[aid]
        if (p.get("prompt") or "") != (c.get("prompt") or ""):
            p_lines = (p.get("prompt") or "").count("\n")
            c_lines = (c.get("prompt") or "").count("\n")
            delta = c_lines - p_lines
            sign = "+" if delta >= 0 else ""
            changes.append(f"Prompt modifié : {c['name']} ({sign}{delta} lignes)")
        if p.get("model") != c.get("model"):
            changes.append(f"Modèle changé : {c['name']} ({p.get('model')} → {c.get('model')})")

    # Red flags
    if len(prev.get("red_flag_patterns", [])) != len(curr.get("red_flag_patterns", [])):
        changes.append(
            f"Red flags : {len(prev.get('red_flag_patterns', []))} → {len(curr.get('red_flag_patterns', []))} règles"
        )
    else:
        prev_pats = sorted([p["pattern"] for p in prev.get("red_flag_patterns", [])])
        curr_pats = sorted([p["pattern"] for p in curr.get("red_flag_patterns", [])])
        if prev_pats != curr_pats:
            changes.append("Red flags : règles modifiées (même nombre)")

    # Legal base
    if prev.get("legal_refs_count") != curr.get("legal_refs_count"):
        changes.append(
            f"Base juridique : {prev.get('legal_refs_count', 0)} → {curr.get('legal_refs_count', 0)} références"
        )

    # Workflow config
    pw = prev.get("workflow_config", {})
    cw = curr.get("workflow_config", {})
    for k in set(list(pw) + list(cw)):
        if pw.get(k) != cw.get(k):
            changes.append(f"Workflow : {k} ({pw.get(k)} → {cw.get(k)})")

    if not changes:
        changes.append("Aucun changement majeur détecté")
    return changes


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
