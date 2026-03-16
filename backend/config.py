from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pathlib import Path
import os
import logging

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

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

SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'onboarding@resend.dev')
NOTIFICATION_EMAIL = os.environ.get('NOTIFICATION_EMAIL', '')

# JWT
JWT_SECRET = os.environ.get('JWT_SECRET', 'accompagn-sante-secret-key-2024')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24
FORUM_JWT_EXPIRATION_HOURS = 168

# LLM
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')

# Stripe
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY', '')

# PayPal
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID', '')
PAYPAL_SECRET = os.environ.get('PAYPAL_SECRET', '')
PAYPAL_MODE = os.environ.get('PAYPAL_MODE', 'sandbox')
PAYPAL_BASE_URL = "https://api-m.sandbox.paypal.com" if PAYPAL_MODE == "sandbox" else "https://api-m.paypal.com"

# Payment packages
PAYMENT_PACKAGES = {
    "dossier_express": {"name": "Dossier Express StratégiIA", "amount": 97.00, "currency": "eur"},
    "analyse_dossier": {"name": "Analyse de dossier", "amount": 150.00, "currency": "eur"},
    "preparation_expertise": {"name": "Préparation expertise médicale", "amount": 250.00, "currency": "eur"},
    "accompagnement_mdph": {"name": "Accompagnement MDPH", "amount": 200.00, "currency": "eur"},
    "protection_juridique": {"name": "Protection juridique", "amount": 200.00, "currency": "eur"},
    "accompagnement_complet": {"name": "Accompagnement complet", "amount": 500.00, "currency": "eur"},
    "urgent_analyse_dossier": {"name": "Analyse de dossier URGENT 48h", "amount": 250.00, "currency": "eur"},
    "urgent_preparation_expertise": {"name": "Préparation expertise URGENT 48h", "amount": 400.00, "currency": "eur"},
    "urgent_accompagnement_mdph": {"name": "Accompagnement MDPH URGENT 48h", "amount": 320.00, "currency": "eur"},
    "urgent_accompagnement_complet": {"name": "Accompagnement complet URGENT 48h", "amount": 750.00, "currency": "eur"},
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

# Booking
AVAILABLE_SLOTS = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00"]

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
SITE_URL = "https://engage-suite-3.preview.emergentagent.com"
SITEMAP_PAGES = [
    ("/", "1.0", "daily"),
    ("/a-propos", "0.8", "monthly"),
    ("/accompagnements", "0.8", "monthly"),
    ("/expertise-medicale", "0.8", "monthly"),
    ("/accident-travail-maladie-professionnelle", "0.8", "monthly"),
    ("/mdph", "0.8", "monthly"),
    ("/protection-juridique", "0.8", "monthly"),
    ("/tarifs", "0.9", "weekly"),
    ("/dossier-express", "0.9", "weekly"),
    ("/simulateur", "0.7", "monthly"),
    ("/calculatrice-ipp", "0.7", "monthly"),
    ("/calculatrice-aah", "0.7", "monthly"),
    ("/ressources", "0.8", "weekly"),
    ("/contact", "0.7", "monthly"),
    ("/agenda", "0.7", "monthly"),
    ("/forum", "0.6", "daily"),
    ("/avis", "0.6", "weekly"),
    ("/seminaires", "0.5", "monthly"),
    ("/entreprises", "0.5", "monthly"),
    ("/partenaires", "0.5", "monthly"),
    ("/parrainage", "0.4", "monthly"),
    ("/espace-client", "0.3", "monthly"),
    ("/mentions-legales", "0.2", "yearly"),
]
