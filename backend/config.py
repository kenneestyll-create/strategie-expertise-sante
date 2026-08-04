from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pathlib import Path
from slowapi import Limiter
from slowapi.util import get_remote_address
import os
import logging

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env', override=False)

# Rate limiter — SECURITY FIX V2
limiter = Limiter(key_func=get_remote_address)

# MongoDB
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Resend
try:
    import resend
    RESEND_AVAILABLE = True
except ImportError:
    RESEND_AVAILABLE = False

if RESEND_AVAILABLE:
    resend.api_key = os.environ.get('RESEND_API_KEY', '')

SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'contact@strategie-expertise-sante.fr')
NOTIFICATION_EMAIL = os.environ.get('NOTIFICATION_EMAIL', 'contact@strategie-expertise-sante.fr')
# Garde-fou 04/08/2026 : l'env de deploiement production contient des valeurs
# perimees (SENDER_EMAIL=onboarding@resend.dev, NOTIFICATION_EMAIL vide) qui
# ecrasent les fallbacks. Une adresse sandbox Resend ou vide n'est jamais
# une configuration legitime en production.
if not SENDER_EMAIL.strip() or SENDER_EMAIL.strip().lower().endswith('resend.dev'):
    SENDER_EMAIL = 'contact@strategie-expertise-sante.fr'
if not NOTIFICATION_EMAIL.strip():
    NOTIFICATION_EMAIL = 'contact@strategie-expertise-sante.fr'

# JWT — SECURITY FIX V1: No fallback, env var required
JWT_SECRET = os.environ.get('JWT_SECRET')
if not JWT_SECRET:
    raise RuntimeError("FATAL: JWT_SECRET environment variable is not set. Server cannot start without a secure secret key.")
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24
FORUM_JWT_EXPIRATION_HOURS = 168

# LLM — Native SDKs
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

# Stripe
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY', '')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')
STRIPE_MODE = 'live' if STRIPE_API_KEY.startswith('sk_live_') else 'test'

# PayPal
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID', '')
PAYPAL_SECRET = os.environ.get('PAYPAL_SECRET', '')
PAYPAL_MODE = os.environ.get('PAYPAL_MODE', 'sandbox')
PAYPAL_BASE_URL = "https://api-m.sandbox.paypal.com" if PAYPAL_MODE == "sandbox" else "https://api-m.paypal.com"

# Payment packages
PAYMENT_PACKAGES = {
    "dossier_express": {"name": "Dossier Express IA", "amount": 97.00, "currency": "eur"},
    "analyse_dossier": {"name": "Analyse de dossier", "amount": 150.00, "currency": "eur"},
    "preparation_expertise": {"name": "Préparation expertise médicale", "amount": 250.00, "currency": "eur"},
    "accompagnement_mdph": {"name": "Accompagnement MDPH", "amount": 200.00, "currency": "eur"},
    "protection_juridique": {"name": "Protection juridique", "amount": 200.00, "currency": "eur"},
    "accompagnement_complet": {"name": "Accompagnement complet", "amount": 500.00, "currency": "eur"},
    "urgent_analyse_dossier": {"name": "Analyse de dossier URGENT 48h", "amount": 250.00, "currency": "eur"},
    "urgent_preparation_expertise": {"name": "Préparation expertise URGENT 48h", "amount": 400.00, "currency": "eur"},
    "urgent_accompagnement_mdph": {"name": "Accompagnement MDPH URGENT 48h", "amount": 320.00, "currency": "eur"},
    "urgent_accompagnement_complet": {"name": "Accompagnement complet URGENT 48h", "amount": 750.00, "currency": "eur"},
    "appel_conseil": {"name": "Appel Conseil — 30 min", "amount": 75.00, "currency": "eur"},
}

# Security
from fastapi.security import HTTPBearer
security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Booking — Call types & slots
CALL_TYPES = {
    "decouverte": {
        "name": "Appel Decouverte",
        "duration": 10,
        "price": 0,
        "slots": ["09:00", "09:15"],
        "max_per_person": 1,
    },
    "conseil": {
        "name": "Appel Conseil",
        "duration": 30,
        "price": 75.00,
        "slots": ["14:00", "14:30", "15:00", "15:30", "16:00", "16:30"],
    },
}

AVAILABLE_SLOTS = ["09:00", "09:15", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30"]

# Document categories
DOCUMENT_CATEGORIES = {
    "at": "Accident du travail",
    "mp": "Maladie professionnelle",
    "mdph": "MDPH / AAH",
    "expertise": "Expertises médicales",
    "cpam": "Courriers CPAM",
    "tribunal": "Documents juridiques",
    "autre": "Autres documents",
}
DOCUMENT_STATUSES = ["en_attente", "valide", "illisible", "corrige"]

# SEO
SITE_URL = os.environ.get("SITE_URL", os.environ.get("REACT_APP_BACKEND_URL", "https://strategie-expertise-sante.fr")).rstrip("/")
SITEMAP_PAGES = [
    ("/", "1.0", "daily"),
    ("/a-propos", "0.8", "monthly"),
    ("/accompagnements", "0.8", "monthly"),
    ("/expertise-medicale", "0.8", "monthly"),
    ("/accident-travail-maladie-professionnelle", "0.8", "monthly"),
    ("/mdph", "0.8", "monthly"),
    ("/protection-juridique", "0.8", "monthly"),
    ("/medecin-conseil", "0.8", "monthly"),
    ("/tarifs", "0.9", "weekly"),
    ("/dossier-express", "0.9", "weekly"),
    ("/simulateur", "0.7", "monthly"),
    ("/calculatrice-ipp", "0.8", "monthly"),
    ("/calculatrice-aah", "0.7", "monthly"),
    ("/ressources", "0.8", "weekly"),
    ("/contact", "0.7", "monthly"),
    ("/agenda", "0.7", "monthly"),
    ("/forum", "0.6", "daily"),
    ("/avis", "0.6", "weekly"),
    ("/seminaires", "0.5", "monthly"),
    ("/entreprises", "0.5", "monthly"),
    ("/partenaires", "0.5", "monthly"),
    ("/mentions-legales", "0.2", "yearly"),
    ("/cgv", "0.2", "yearly"),
    ("/politique-confidentialite", "0.2", "yearly"),
]
