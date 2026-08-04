"""Test garde-fou SENDER_EMAIL / NOTIFICATION_EMAIL dans config.py."""
import subprocess
import sys
import textwrap


def _run(env_setup: str) -> str:
    code = (
        "import os, importlib, sys\n"
        "sys.path.insert(0, '/app/backend')\n"
        + env_setup + "\n"
        "import config\n"
        "importlib.reload(config)\n"
        "print('SENDER=' + config.SENDER_EMAIL)\n"
        "print('NOTIF=' + config.NOTIFICATION_EMAIL)\n"
    )
    r = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True, timeout=30)
    assert r.returncode == 0, f"stderr: {r.stderr}\nstdout: {r.stdout}"
    return r.stdout


def test_guard_perimee_sandbox_resend():
    """SENDER=onboarding@resend.dev + NOTIF vide -> les 2 forcees a l'adresse legitime."""
    out = _run(
        "os.environ['SENDER_EMAIL']='onboarding@resend.dev'\n"
        "os.environ['NOTIFICATION_EMAIL']=''"
    )
    assert 'SENDER=contact@strategie-expertise-sante.fr' in out
    assert 'NOTIF=contact@strategie-expertise-sante.fr' in out


def test_guard_env_absent():
    """Cles absentes -> fallback legitime."""
    out = _run(
        "os.environ.pop('SENDER_EMAIL', None)\n"
        "os.environ.pop('NOTIFICATION_EMAIL', None)"
    )
    assert 'SENDER=contact@strategie-expertise-sante.fr' in out
    assert 'NOTIF=contact@strategie-expertise-sante.fr' in out


def test_guard_env_valide_respecte():
    """SENDER legitime custom -> respecte tel quel."""
    out = _run(
        "os.environ['SENDER_EMAIL']='autre@strategie-expertise-sante.fr'\n"
        "os.environ['NOTIFICATION_EMAIL']='admin@strategie-expertise-sante.fr'"
    )
    assert 'SENDER=autre@strategie-expertise-sante.fr' in out
    assert 'NOTIF=admin@strategie-expertise-sante.fr' in out


def test_guard_resend_dev_variant():
    """Toute adresse @resend.dev doit etre neutralisee."""
    out = _run("os.environ['SENDER_EMAIL']='foo@bar.resend.dev'")
    assert 'SENDER=contact@strategie-expertise-sante.fr' in out
