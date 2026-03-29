"""
CONSOLIDATION_ARCHITECTURE — Garde-fous et assertions metier.
Ces fonctions DOIVENT etre appelees avant toute operation critique
pour empecher toute contamination croisee entre services.
"""
from config import logger
from constants.statuses import Service


class ServiceGuardError(Exception):
    """Raised when a cross-service contamination is detected."""
    pass


def assert_service_type(service_type: str, expected: str, context: str = ""):
    """Assert that the service type matches the expected value."""
    if service_type != expected:
        msg = f"GARDE-FOU: service_type='{service_type}' != expected='{expected}' [{context}]"
        logger.critical(msg)
        raise ServiceGuardError(msg)


def assert_valid_service(service_type: str, context: str = ""):
    """Assert that the service type is one of the known services."""
    if service_type not in Service.ALL:
        msg = f"GARDE-FOU: service_type='{service_type}' inconnu. Valides: {Service.ALL} [{context}]"
        logger.critical(msg)
        raise ServiceGuardError(msg)


def assert_relecture_blocks_auto_send(relecture_required: bool, context: str = ""):
    """Assert that auto-sending is blocked when relecture is required."""
    if relecture_required:
        msg = f"GARDE-FOU: envoi auto bloque car relecture_expert_required=True [{context}]"
        logger.warning(msg)
        return False
    return True


def assert_premium_analyses_entry(entry: dict, context: str = ""):
    """Validate that a premium_analyses entry has all required fields."""
    required = ["id", "type", "email", "status", "relecture_expert_required", "created_at"]
    missing = [f for f in required if f not in entry or entry[f] is None]
    if missing:
        msg = f"GARDE-FOU: premium_analyses entry manque champs {missing} [{context}]"
        logger.error(msg)
        raise ServiceGuardError(msg)
    assert_valid_service(entry["type"], context)


# ==================== STATUS TRANSITION GUARDS ====================

DOSSIER_EXPRESS_TRANSITIONS = {
    None: ["documents_recus"],
    "documents_recus": ["extraction_en_cours", "erreur_ia"],
    "extraction_en_cours": ["analyse_ia", "erreur_ia"],
    "analyse_ia": ["pdf_en_cours", "erreur_ia"],
    "pdf_en_cours": ["envoi_en_cours", "erreur_pdf", "erreur_ia"],
    "envoi_en_cours": ["livre_par_email", "erreur_email"],
    "erreur_email": ["livre_par_email"],
    "erreur_ia": [],
    "erreur_pdf": [],
}

STRATEGIIA_TRANSITIONS = {
    None: ["processing"],
    "processing": ["completed", "error"],
    "completed": [],
    "error": ["processing"],
}

DELIVERY_TRANSITIONS = {
    None: ["en_attente_traitement"],
    "en_attente_traitement": ["genere_sans_email", "livre_par_email", "incident_technique"],
    "genere_sans_email": ["livre_par_email"],
    "incident_technique": ["en_attente_traitement"],
}


def assert_valid_step_transition(current_step, new_step, service, context=""):
    """Validate status transition. Logs warning if invalid but does NOT block
    (to avoid breaking existing flows during stabilization)."""
    transitions = DOSSIER_EXPRESS_TRANSITIONS if service == Service.DOSSIER_EXPRESS else STRATEGIIA_TRANSITIONS
    allowed = transitions.get(current_step, [])
    if new_step not in allowed and allowed:
        logger.warning(
            f"[TRANSITION_GUARD][{service}] Transition non standard: '{current_step}' -> '{new_step}' "
            f"(autorisees: {allowed}) [{context}]"
        )


def assert_collection_ownership(collection_name: str, service: str, context: str = ""):
    """Verify that a route only writes to its own collections."""
    ownership = {
        Service.STRATEGIIA: ["strategiia_analyses", "premium_analyses", "cas_anonymises"],
        Service.DOSSIER_EXPRESS: ["dossier_express", "premium_analyses"],
    }
    allowed = ownership.get(service, [])
    if collection_name not in allowed:
        msg = f"GARDE-FOU: Service '{service}' tente d'ecrire dans '{collection_name}' (autorisees: {allowed}) [{context}]"
        logger.critical(msg)
        raise ServiceGuardError(msg)
