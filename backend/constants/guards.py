"""
CONSOLIDATION_ARCHITECTURE — Garde-fous et assertions métier.
Ces fonctions DOIVENT être appelées avant toute opération critique
pour empêcher toute contamination croisée entre services.
"""
from config import logger
from constants.statuses import Service


class ServiceGuardError(Exception):
    """Raised when a cross-service contamination is detected."""
    pass


def assert_service_type(service_type: str, expected: str, context: str = ""):
    """Assert that the service type matches the expected value.
    Raises ServiceGuardError if there's a mismatch — prevents StrategiIA logic
    from accidentally writing into Dossier Express data and vice versa.
    """
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
    """Assert that auto-sending is blocked when relecture is required.
    If relecture_expert_required=True, the document MUST go through
    admin review before being sent to the client.
    """
    if relecture_required:
        msg = f"GARDE-FOU: envoi auto bloqué car relecture_expert_required=True [{context}]"
        logger.warning(msg)
        return False  # Return False to signal "do not auto-send"
    return True  # OK to auto-send


def assert_premium_analyses_entry(entry: dict, context: str = ""):
    """Validate that a premium_analyses entry has all required fields."""
    required = ["id", "type", "email", "status", "relecture_expert_required", "created_at"]
    missing = [f for f in required if f not in entry or entry[f] is None]
    if missing:
        msg = f"GARDE-FOU: premium_analyses entry manque champs {missing} [{context}]"
        logger.error(msg)
        raise ServiceGuardError(msg)
    assert_valid_service(entry["type"], context)
