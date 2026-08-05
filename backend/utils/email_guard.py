"""Garde-fou d'envoi email — ordre executif 04/08/2026 (P1).

Deux protections cumulees :
1. Blocage universel des adresses de test (tous environnements) — les schedulers
   ne peuvent plus consommer le quota Resend avec des comptes pytest/test.
2. En environnement PREVIEW (detecte via la variable OS `preview_endpoint`,
   propre au pod de dev et absente du conteneur de production), seuls les envois
   vers les adresses internes (admin/expediteur/notification) sont autorises.
   La production conserve donc l'exclusivite du quota Resend.
"""
import os
import re
import logging

logger = logging.getLogger(__name__)

_TEST_PATTERNS = re.compile(
    r"(@test\.com$|@example\.com$|@test\.fr$|^pytest-|^ratelimit_|^upload_test_|^integ-|^anon-|^test_|^testuser)",
    re.IGNORECASE,
)

IS_PREVIEW = bool(
    os.environ.get("preview_endpoint")
    or "preview.emergentagent.com" in os.environ.get("APP_URL", "")
)

_PREVIEW_ALLOWLIST = {
    a.strip().lower()
    for a in [
        os.environ.get("SENDER_EMAIL", ""),
        os.environ.get("NOTIFICATION_EMAIL", ""),
        "admin@accompagn-sante.fr",
        "backup@strategie-expertise-sante.fr",
        "contact@strategie-expertise-sante.fr",
    ]
    if a and a.strip()
}


TEST_EMAIL_REGEX = _TEST_PATTERNS.pattern


def is_test_address(email: str) -> bool:
    return bool(_TEST_PATTERNS.search((email or "").strip().lower()))


def is_blocked(email: str) -> bool:
    e = (email or "").strip().lower()
    if not e:
        return True
    if _TEST_PATTERNS.search(e):
        return True
    if IS_PREVIEW and e not in _PREVIEW_ALLOWLIST:
        return True
    return False


def install_email_guard() -> bool:
    """Enveloppe resend.Emails.send — point de passage unique de tous les envois."""
    try:
        import resend
    except ImportError:
        return False
    if getattr(resend.Emails, "_ses_guard_installed", False):
        return True

    original_send = resend.Emails.send

    def guarded_send(params, *args, **kwargs):
        to = params.get("to") if isinstance(params, dict) else None
        recipients = to if isinstance(to, list) else [to]
        allowed = [r for r in recipients if not is_blocked(r)]
        blocked = [r for r in recipients if is_blocked(r)]
        if blocked:
            logger.warning(
                f"[EMAIL_GUARD] {len(blocked)} envoi(s) BLOQUE(S) vers {blocked[:3]}{'...' if len(blocked) > 3 else ''} "
                f"(env={'preview' if IS_PREVIEW else 'production'})"
            )
        if not allowed:
            return {"id": "blocked-by-email-guard"}
        if blocked and isinstance(params, dict):
            params = {**params, "to": allowed}
        return original_send(params, *args, **kwargs)

    resend.Emails.send = guarded_send
    resend.Emails._ses_guard_installed = True
    logger.info(f"[EMAIL_GUARD] Actif — mode {'PREVIEW (allowlist interne)' if IS_PREVIEW else 'PRODUCTION (blocage adresses de test uniquement)'}")
    return True
