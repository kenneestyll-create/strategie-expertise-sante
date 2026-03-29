"""
CONSOLIDATION_ARCHITECTURE — Constantes de workflow centralisées.
Définit les configurations par service (pricing, prompts refs, pipeline steps).
"""
from constants.statuses import Service


# ========== PRICING PAR SERVICE ==========
PRICING = {
    Service.STRATEGIIA: {
        "base": 29.00,
        "premium_pdf": 19.00,
        "analyse_premium": 29.00,
        "label": "StratégiIA Premium",
    },
    Service.DOSSIER_EXPRESS: {
        "base": 97.00,
        "premium_pdf": 19.00,
        "analyse_premium": 49.00,
        "label": "Dossier Express IA",
    },
}


# ========== PRODUCT TAGS STRIPE ==========
def get_stripe_tag(service: str, premium_pdf: bool, analyse_premium: bool) -> str:
    """Deterministic Stripe metadata tag based on options."""
    if service == Service.STRATEGIIA:
        if premium_pdf and analyse_premium:
            return "strategiia_premium_full"
        if premium_pdf:
            return "strategiia_premium_pdf"
        if analyse_premium:
            return "strategiia_analyse_premium"
        return "strategiia_premium"
    elif service == Service.DOSSIER_EXPRESS:
        if premium_pdf and analyse_premium:
            return "dossier_express_full"
        if premium_pdf:
            return "dossier_express_pdf_pro"
        if analyse_premium:
            return "dossier_express_analyse_premium"
        return "dossier_express"
    return service


# ========== RETRY CONFIG ==========
LLM_MAX_RETRIES = 3
LLM_RETRY_DELAY_SECONDS = 3
LLM_MIN_ANALYSIS_LENGTH = 200  # chars — below this, analysis is considered failed

# ========== QUOTAS ==========
STRATEGIIA_FREE_MONTHLY_QUOTA = 3

# ========== DOCUMENTS ==========
MAX_FILE_SIZE = 50 * 1024 * 1024   # 50 MB
MAX_TOTAL_SIZE = 100 * 1024 * 1024  # 100 MB
MAX_FILES = 10
