from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import PlainTextResponse, Response
from fastapi.middleware.gzip import GZipMiddleware
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import asyncio
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
import httpx
import base64

try:
    import resend
    RESEND_AVAILABLE = True
except ImportError:
    RESEND_AVAILABLE = False

# Import Emergent LLM
from emergentintegrations.llm.chat import LlmChat, UserMessage

# Import Stripe
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest
from fastapi import Request

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Resend configuration
if RESEND_AVAILABLE:
    resend.api_key = os.environ.get('RESEND_API_KEY', '')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'onboarding@resend.dev')
NOTIFICATION_EMAIL = os.environ.get('NOTIFICATION_EMAIL', '')

# JWT configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'accompagn-sante-secret-key-2024')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24
FORUM_JWT_EXPIRATION_HOURS = 168  # 7 days for forum users

# Emergent LLM Key
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')

# Stripe configuration
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY', '')

# PayPal configuration
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID', '')
PAYPAL_SECRET = os.environ.get('PAYPAL_SECRET', '')
PAYPAL_MODE = os.environ.get('PAYPAL_MODE', 'sandbox')
PAYPAL_BASE_URL = "https://api-m.sandbox.paypal.com" if PAYPAL_MODE == "sandbox" else "https://api-m.paypal.com"

# Payment packages - FIXED prices defined on backend
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
security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)

# Create the main app
app = FastAPI(title="Stratégie & Expertise Santé API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ==================== EXISTING MODELS ====================

class ContactRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nom: str
    prenom: str
    email: EmailStr
    telephone: Optional[str] = None
    sujet: str
    message: str
    type_accompagnement: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "nouveau"
    notes_admin: Optional[str] = None

class ContactRequestCreate(BaseModel):
    nom: str
    prenom: str
    email: EmailStr
    telephone: Optional[str] = None
    sujet: str
    message: str
    type_accompagnement: Optional[str] = None

class ContactRequestUpdate(BaseModel):
    status: Optional[str] = None
    notes_admin: Optional[str] = None

class FAQItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str
    reponse: str
    categorie: str
    ordre: int = 0

class FAQItemCreate(BaseModel):
    question: str
    reponse: str
    categorie: str
    ordre: int = 0

class AdminUser(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    password_hash: str
    nom: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin_name: str

# Avis / Témoignages
class Avis(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nom: str
    situation: Optional[str] = None
    note: int = Field(ge=1, le=5)
    temoignage: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "en_attente"

class AvisCreate(BaseModel):
    nom: str
    situation: Optional[str] = None
    note: int = Field(ge=1, le=5)
    temoignage: str

class AvisUpdate(BaseModel):
    status: Optional[str] = None

# ==================== FORUM MODELS ====================

class ForumUser(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: Optional[EmailStr] = None
    password_hash: Optional[str] = None
    pseudo: str
    is_anonymous: bool = False
    avatar_color: str = "#C17B5D"  # Default accent color
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_banned: bool = False
    ban_reason: Optional[str] = None

class ForumUserRegister(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    pseudo: str
    is_anonymous: bool = False

class ForumUserLogin(BaseModel):
    email: EmailStr
    password: str

class ForumTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    pseudo: str
    is_anonymous: bool

class ForumCategory(BaseModel):
    id: str
    name: str
    slug: str
    description: str
    icon: str
    order: int

class ForumTopic(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category_id: str
    title: str
    content: str
    author_id: str
    author_pseudo: str
    is_anonymous: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    views: int = 0
    likes: List[str] = []
    replies_count: int = 0
    is_pinned: bool = False
    is_locked: bool = False
    status: str = "published"  # published, hidden, deleted

class ForumTopicCreate(BaseModel):
    category_id: str
    title: str
    content: str

class ForumReply(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    topic_id: str
    content: str
    author_id: str
    author_pseudo: str
    is_anonymous: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    likes: List[str] = []
    status: str = "published"

class ForumReplyCreate(BaseModel):
    content: str

class ForumReport(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    reporter_id: str
    target_type: str  # topic, reply
    target_id: str
    reason: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "pending"  # pending, reviewed, dismissed

class ForumReportCreate(BaseModel):
    target_type: str
    target_id: str
    reason: str

# ==================== CHATBOT MODELS ====================

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    is_faq: bool
    session_id: str

# ==================== PAYMENT MODELS ====================

class PaymentTransaction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    package_id: str
    package_name: str
    amount: float
    currency: str
    email: Optional[str] = None
    customer_name: Optional[str] = None
    status: str = "pending"  # pending, paid, failed, expired
    payment_status: str = "initiated"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Optional[dict] = None

class CreateCheckoutRequest(BaseModel):
    package_id: str
    origin_url: str
    customer_email: Optional[str] = None
    customer_name: Optional[str] = None
    referral_code: Optional[str] = None  # Code parrainage

# ==================== VISITOR & REFERRAL MODELS ====================

class VisitorCount(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = "visitor_counter"
    count: int = 0
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ReferralCode(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str
    owner_email: str
    owner_name: Optional[str] = None
    uses_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True

class ReferralUse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    referral_code: str
    referred_email: str
    referred_name: Optional[str] = None
    discount_applied: float = 10.0  # 10%
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CreateReferralRequest(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class ClientHistory(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    orders_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_order_at: Optional[datetime] = None

# ==================== BOOKING MODELS ====================

class Booking(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: str
    phone: Optional[str] = None
    booking_type: str = "telephone"  # telephone, visio
    date: str  # YYYY-MM-DD
    time_slot: str  # HH:MM
    message: Optional[str] = None
    status: str = "confirme"  # confirme, annule, termine
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BookingCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    booking_type: str = "telephone"
    date: str
    time_slot: str
    message: Optional[str] = None

# ==================== CLIENT PORTAL MODELS ====================

class ClientUser(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    password_hash: str
    name: str
    phone: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ClientRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: Optional[str] = None

class ClientLogin(BaseModel):
    email: EmailStr
    password: str

class ClientCase(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str
    title: str
    description: str
    status: str = "en_cours"  # en_cours, en_attente, termine
    notes: Optional[str] = None
    updates: List[dict] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ==================== SIMULATOR MODEL ====================

class SimulatorResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    answers: dict
    profile: str
    recommendations: List[str] = []
    email: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ==================== ABANDONED CHECKOUT MODEL ====================

class AbandonedCheckout(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: Optional[str] = None
    package_id: str
    package_name: str
    amount: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    relance_sent: bool = False
    relance_sent_at: Optional[str] = None

# ==================== AUTH HELPERS ====================

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def create_token(user_id: str, email: str, is_admin: bool = False, expiration_hours: int = JWT_EXPIRATION_HOURS) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "is_admin": is_admin,
        "exp": datetime.now(timezone.utc) + timedelta(hours=expiration_hours)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def create_forum_token(user_id: str, pseudo: str, is_anonymous: bool) -> str:
    payload = {
        "sub": user_id,
        "pseudo": pseudo,
        "is_anonymous": is_anonymous,
        "is_forum_user": True,
        "exp": datetime.now(timezone.utc) + timedelta(hours=FORUM_JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        admin_id = payload.get("sub")
        if admin_id is None or payload.get("is_forum_user"):
            raise HTTPException(status_code=401, detail="Token invalide")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalide")

async def get_current_forum_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None or not payload.get("is_forum_user"):
            raise HTTPException(status_code=401, detail="Token invalide")
        
        # Check if user is banned
        user = await db.forum_users.find_one({"id": user_id}, {"_id": 0})
        if user and user.get("is_banned"):
            raise HTTPException(status_code=403, detail="Votre compte a été suspendu")
        
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalide")

async def get_optional_forum_user(credentials: HTTPAuthorizationCredentials = Depends(security_optional)):
    if credentials is None:
        return None
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if not payload.get("is_forum_user"):
            return None
        return payload
    except:
        return None

def create_client_token(client_id: str, email: str, name: str) -> str:
    payload = {
        "sub": client_id,
        "email": email,
        "name": name,
        "is_client": True,
        "exp": datetime.now(timezone.utc) + timedelta(hours=FORUM_JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_client(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        client_id = payload.get("sub")
        if client_id is None or not payload.get("is_client"):
            raise HTTPException(status_code=401, detail="Token invalide")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalide")

# ==================== EMAIL HELPER ====================

async def send_notification_email(contact: ContactRequest):
    if not RESEND_AVAILABLE or not os.environ.get('RESEND_API_KEY') or not NOTIFICATION_EMAIL:
        logger.info("Email notification skipped - Resend not configured")
        return False
    
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #2D2A26;">Nouvelle demande de contact</h2>
        <div style="background: #F9F7F2; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <p><strong>Nom:</strong> {contact.prenom} {contact.nom}</p>
            <p><strong>Email:</strong> {contact.email}</p>
            <p><strong>Téléphone:</strong> {contact.telephone or 'Non renseigné'}</p>
            <p><strong>Type d'accompagnement:</strong> {contact.type_accompagnement or 'Non spécifié'}</p>
            <p><strong>Sujet:</strong> {contact.sujet}</p>
            <hr style="border: 1px solid #E5E0D6;">
            <p><strong>Message:</strong></p>
            <p>{contact.message}</p>
        </div>
    </body>
    </html>
    """
    
    params = {
        "from": SENDER_EMAIL,
        "to": [NOTIFICATION_EMAIL],
        "subject": f"Nouvelle demande: {contact.sujet}",
        "html": html_content
    }
    
    try:
        await asyncio.to_thread(resend.Emails.send, params)
        logger.info(f"Notification email sent for contact {contact.id}")
        return True
    except Exception as e:
        logger.error(f"Failed to send notification email: {str(e)}")
        return False

# ==================== CHATBOT HELPER ====================

FAQ_DATABASE = {
    "expertise médicale": {
        "keywords": ["expertise", "médical", "médecin", "expert", "préparer", "préparation"],
        "response": """**Comment se préparer à une expertise médicale ?**

Voici les étapes essentielles :

1. **Rassemblez vos documents** : tous vos certificats médicaux, comptes-rendus, imageries, ordonnances
2. **Préparez une chronologie** de votre parcours médical
3. **Listez vos symptômes** au quotidien et leur impact sur votre vie
4. **Notez vos questions** pour l'expert
5. **Restez honnête et précis** dans vos réponses

L'expertise dure généralement 30 à 60 minutes. Vous pouvez vous faire accompagner.

👉 [Découvrez notre accompagnement personnalisé](/expertise-medicale)"""
    },
    "mdph": {
        "keywords": ["mdph", "handicap", "rqth", "aah", "allocation", "reconnaissance"],
        "response": """**Qu'est-ce que la MDPH ?**

La **Maison Départementale des Personnes Handicapées** est votre interlocuteur unique pour :

- La **RQTH** (Reconnaissance de la Qualité de Travailleur Handicapé)
- L'**AAH** (Allocation aux Adultes Handicapés)
- Les **cartes d'invalidité** et de stationnement
- Les aides humaines et matérielles

**Pour constituer un dossier :**
1. Téléchargez le formulaire unique sur le site de votre MDPH
2. Faites remplir le certificat médical par votre médecin
3. Joignez tous les justificatifs demandés

Délai moyen : 4 à 6 mois.

👉 [En savoir plus sur les démarches MDPH](/mdph)"""
    },
    "accident travail": {
        "keywords": ["accident", "travail", "at", "mp", "maladie", "professionnelle", "droits", "droit"],
        "response": """**Quels sont vos droits après un accident du travail ?**

En cas d'AT/MP, vous avez droit à :

- **Prise en charge à 100%** des soins liés à l'accident
- **Indemnités journalières** pendant l'arrêt de travail
- **Rente ou capital** en cas de séquelles permanentes (IPP)
- **Protection contre le licenciement** pendant l'arrêt

**Étapes clés :**
1. Déclaration dans les 24h à l'employeur
2. Certificat médical initial
3. Suivi médical et consolidation
4. Évaluation du taux d'IPP

👉 [Comprendre vos droits AT/MP](/accident-travail-maladie-professionnelle)"""
    },
    "protection juridique": {
        "keywords": ["protection", "juridique", "assurance", "avocat", "activer", "litige"],
        "response": """**Comment activer votre protection juridique ?**

La protection juridique est souvent incluse dans vos contrats d'assurance (habitation, auto, santé). Elle peut couvrir les frais d'avocat et d'expertise.

**Pour l'activer :**
1. Vérifiez vos contrats d'assurance
2. Identifiez les garanties couvertes
3. Déclarez votre litige par écrit à l'assureur
4. Constituez votre dossier

**Bon à savoir :** Vous avez le droit de choisir votre propre avocat, même si l'assurance vous en propose un.

👉 [Guide complet sur la protection juridique](/protection-juridique)"""
    },
    "tarifs": {
        "keywords": ["tarif", "prix", "coût", "combien", "prestation", "accompagnement"],
        "response": """**Nos tarifs**

- **Analyse de dossier** : à partir de 150 €
- **Préparation à expertise médicale** : à partir de 250 €
- **Accompagnement MDPH** : à partir de 200 €
- **Protection juridique** : à partir de 200 €
- **Accompagnement complet** : à partir de 500 € (sur devis)
- **Séminaires / Formations** : sur devis
- **Conseil entreprises** : sur devis

**Le premier échange téléphonique est gratuit et sans engagement.**

👉 [Voir tous nos tarifs](/tarifs)"""
    },
    "contact": {
        "keywords": ["contact", "rendez-vous", "joindre", "téléphone", "email", "contacter"],
        "response": """**Comment nous contacter ?**

Vous pouvez me contacter pour un premier échange gratuit et sans engagement :

- **Par le formulaire de contact** sur notre site
- **Par email** : contact@accompagn-sante.fr
- **Par téléphone** : 06 00 00 00 00

Je vous répondrai dans les 24 à 48 heures.

👉 [Accéder au formulaire de contact](/contact)"""
    }
}

def find_faq_response(message: str) -> Optional[str]:
    """Search for a matching FAQ response based on keywords"""
    message_lower = message.lower()
    
    for topic, data in FAQ_DATABASE.items():
        for keyword in data["keywords"]:
            if keyword in message_lower:
                return data["response"]
    
    return None

async def get_ai_response(message: str, session_id: str) -> str:
    """Get response from Claude AI for complex questions"""
    if not EMERGENT_LLM_KEY:
        return "Je suis désolé, le service IA n'est pas disponible actuellement. Veuillez consulter nos ressources ou me contacter directement."
    
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=session_id,
            system_message="""Tu es l'assistant virtuel de Stratégie & Expertise Santé, un service français d'accompagnement pour les personnes confrontées à des maladies professionnelles, accidents du travail, expertises médicales et litiges avec les assurances.

Ton rôle est d'aider les visiteurs à comprendre leurs droits et les orienter vers les bonnes ressources.

Règles importantes :
- Réponds toujours en français
- Sois empathique et rassurant
- Utilise un langage simple, sans jargon excessif
- Ne donne jamais de conseils médicaux ou juridiques spécifiques
- Oriente vers les professionnels compétents quand nécessaire
- Suggère de prendre contact pour un accompagnement personnalisé
- Sois concis mais complet

Pages du site à suggérer si pertinent :
- /expertise-medicale : Préparation aux expertises
- /accident-travail-maladie-professionnelle : Droits AT/MP
- /mdph : Démarches MDPH
- /protection-juridique : Protection juridique
- /tarifs : Nos tarifs
- /contact : Formulaire de contact
- /ressources : FAQ et glossaire"""
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")
        
        user_message = UserMessage(text=message)
        response = await chat.send_message(user_message)
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting AI response: {str(e)}")
        return "Je suis désolé, une erreur s'est produite. Veuillez réessayer ou consulter nos ressources directement sur le site."

# ==================== FORUM CATEGORIES ====================

FORUM_CATEGORIES = [
    ForumCategory(
        id="accident-travail",
        name="Accident du travail",
        slug="accident-travail",
        description="Échangez sur les accidents du travail, déclarations, indemnisations",
        icon="AlertTriangle",
        order=1
    ),
    ForumCategory(
        id="maladie-professionnelle",
        name="Maladie professionnelle",
        slug="maladie-professionnelle",
        description="Partagez vos expériences sur les maladies professionnelles et leur reconnaissance",
        icon="Stethoscope",
        order=2
    ),
    ForumCategory(
        id="expertise-medicale",
        name="Expertise médicale",
        slug="expertise-medicale",
        description="Conseils et retours d'expérience sur les expertises médicales",
        icon="FileSearch",
        order=3
    ),
    ForumCategory(
        id="invalidite",
        name="Invalidité",
        slug="invalidite",
        description="Discussions sur l'invalidité, les rentes et les démarches associées",
        icon="Heart",
        order=4
    ),
    ForumCategory(
        id="mdph",
        name="Démarches MDPH",
        slug="mdph",
        description="Aide et conseils sur les dossiers MDPH, RQTH, AAH",
        icon="Building",
        order=5
    ),
    ForumCategory(
        id="protection-juridique",
        name="Protection juridique",
        slug="protection-juridique",
        description="Questions sur la protection juridique et les litiges",
        icon="Shield",
        order=6
    )
]

# ==================== PUBLIC ROUTES ====================

@api_router.get("/")
async def root():
    return {"message": "Bienvenue sur l'API Stratégie & Expertise Santé"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# Contact Routes
@api_router.post("/contact", response_model=dict)
async def create_contact(input_data: ContactRequestCreate):
    contact_dict = input_data.model_dump()
    contact_obj = ContactRequest(**contact_dict)
    
    doc = contact_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.contacts.insert_one(doc)
    asyncio.create_task(send_notification_email(contact_obj))
    
    return {
        "success": True,
        "message": "Votre demande a été envoyée avec succès. Nous vous recontacterons rapidement.",
        "id": contact_obj.id
    }

# FAQ Routes
@api_router.get("/faq", response_model=List[FAQItem])
async def get_faq():
    faqs = await db.faq.find({}, {"_id": 0}).sort("ordre", 1).to_list(100)
    return faqs

@api_router.get("/faq/category/{categorie:path}", response_model=List[FAQItem])
async def get_faq_by_category(categorie: str):
    from urllib.parse import unquote
    decoded_categorie = unquote(categorie)
    faqs = await db.faq.find({"categorie": decoded_categorie}, {"_id": 0}).sort("ordre", 1).to_list(100)
    return faqs

# Avis Routes (Public)
@api_router.get("/avis", response_model=List[Avis])
async def get_published_avis():
    avis_list = await db.avis.find({"status": "publie"}, {"_id": 0}).sort("created_at", -1).to_list(100)
    for avis in avis_list:
        if isinstance(avis.get('created_at'), str):
            avis['created_at'] = datetime.fromisoformat(avis['created_at'])
    return avis_list

@api_router.post("/avis", response_model=dict)
async def create_avis(input_data: AvisCreate):
    avis_obj = Avis(**input_data.model_dump())
    doc = avis_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.avis.insert_one(doc)
    
    return {
        "success": True,
        "message": "Votre témoignage a été soumis et sera publié après validation.",
        "id": avis_obj.id
    }

# ==================== VISITOR COUNTER ROUTES ====================

@api_router.get("/visitors/count")
async def get_visitor_count():
    """Get current visitor count"""
    counter = await db.visitor_counter.find_one({"id": "visitor_counter"}, {"_id": 0})
    if not counter:
        return {"count": 0}
    return {"count": counter.get("count", 0)}

@api_router.post("/visitors/increment")
async def increment_visitor_count():
    """Increment visitor count"""
    result = await db.visitor_counter.find_one_and_update(
        {"id": "visitor_counter"},
        {
            "$inc": {"count": 1},
            "$set": {"last_updated": datetime.now(timezone.utc).isoformat()}
        },
        upsert=True,
        return_document=True
    )
    # Exclude _id from response
    count = result.get("count", 1) if result else 1
    return {"count": count}

# ==================== REFERRAL & DISCOUNT ROUTES ====================

@api_router.post("/referral/create")
async def create_referral_code(request: CreateReferralRequest):
    """Create a referral code for a client"""
    # Check if client already has a code
    existing = await db.referral_codes.find_one({"owner_email": request.email}, {"_id": 0})
    if existing:
        return {"code": existing["code"], "message": "Code existant récupéré"}
    
    # Generate unique code
    import random
    import string
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    referral = ReferralCode(
        code=code,
        owner_email=request.email,
        owner_name=request.name
    )
    
    doc = referral.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.referral_codes.insert_one(doc)
    
    return {
        "success": True,
        "code": code,
        "message": "Votre code parrainage a été créé. Partagez-le pour offrir 10% de réduction !"
    }

@api_router.get("/referral/validate/{code}")
async def validate_referral_code(code: str):
    """Validate a referral code"""
    referral = await db.referral_codes.find_one({"code": code.upper(), "is_active": True}, {"_id": 0})
    if not referral:
        return {"valid": False, "message": "Code invalide ou expiré"}
    
    return {
        "valid": True,
        "discount": 10,
        "message": "Code valide ! 10% de réduction appliquée."
    }

@api_router.get("/client/discount/{email}")
async def get_client_discount(email: str):
    """Get applicable discount for a client (loyalty + referral)"""
    # Check order history for loyalty discount
    client = await db.client_history.find_one({"email": email.lower()}, {"_id": 0})
    orders_count = client.get("orders_count", 0) if client else 0
    
    # Loyalty discount: 15% from 2nd order
    loyalty_discount = 15 if orders_count >= 1 else 0
    
    return {
        "orders_count": orders_count,
        "loyalty_discount": loyalty_discount,
        "message": f"{'15% de fidélité appliqués !' if loyalty_discount else 'Première commande'}"
    }

@api_router.post("/client/record-order")
async def record_client_order(email: str, name: Optional[str] = None):
    """Record a client order for loyalty tracking"""
    await db.client_history.update_one(
        {"email": email.lower()},
        {
            "$inc": {"orders_count": 1},
            "$set": {
                "last_order_at": datetime.now(timezone.utc).isoformat(),
                "name": name
            },
            "$setOnInsert": {
                "id": str(uuid.uuid4()),
                "created_at": datetime.now(timezone.utc).isoformat()
            }
        },
        upsert=True
    )
    return {"success": True}

# ==================== CHATBOT ROUTES ====================

@api_router.post("/chatbot", response_model=ChatResponse)
async def chatbot_message(chat_input: ChatMessage):
    """Handle chatbot messages - first check FAQ, then use AI. Limited to 5 free questions per session."""
    session_id = chat_input.session_id or str(uuid.uuid4())

    # Track and check chatbot quota (5 questions per session)
    session_doc = await db.chatbot_sessions.find_one({"session_id": session_id}, {"_id": 0})
    question_count = (session_doc.get("count", 0) if session_doc else 0) + 1

    if question_count > 5:
        return ChatResponse(
            response="Vous avez atteint la limite de 5 questions gratuites pour cette session.\n\n"
                     "Pour aller plus loin dans votre démarche :\n"
                     "- [Réservez un appel gratuit](/agenda) avec notre expert\n"
                     "- [Découvrez le Dossier Express](/dossier-express) pour une analyse complète\n"
                     "- [Consultez nos tarifs](/tarifs) pour un accompagnement personnalisé\n\n"
                     "Premier échange toujours gratuit et sans engagement.",
            is_faq=False,
            session_id=session_id
        )

    # Update session counter
    await db.chatbot_sessions.update_one(
        {"session_id": session_id},
        {"$set": {"count": question_count, "updated_at": datetime.now(timezone.utc).isoformat()},
         "$setOnInsert": {"created_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )

    # First, try to find a FAQ response
    faq_response = find_faq_response(chat_input.message)

    if faq_response:
        return ChatResponse(
            response=faq_response,
            is_faq=True,
            session_id=session_id
        )

    # If no FAQ match, use AI
    ai_response = await get_ai_response(chat_input.message, session_id)

    return ChatResponse(
        response=ai_response,
        is_faq=False,
        session_id=session_id
    )

@api_router.get("/chatbot/quota/{session_id}")
async def chatbot_quota(session_id: str):
    """Check remaining free chatbot questions for this session."""
    session_doc = await db.chatbot_sessions.find_one({"session_id": session_id}, {"_id": 0})
    used = session_doc.get("count", 0) if session_doc else 0
    return {"remaining": max(0, 5 - used), "limit": 5, "used": min(used, 5)}

# ==================== PAYMENT ROUTES ====================

@api_router.get("/payments/packages")
async def get_payment_packages():
    """Get available payment packages"""
    return [
        {"id": k, "name": v["name"], "amount": v["amount"], "currency": v["currency"]}
        for k, v in PAYMENT_PACKAGES.items()
    ]

@api_router.post("/payments/checkout")
async def create_checkout_session(request_data: CreateCheckoutRequest, request: Request):
    """Create a Stripe checkout session with discount logic"""
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Stripe non configuré")
    
    # Validate package
    if request_data.package_id not in PAYMENT_PACKAGES:
        raise HTTPException(status_code=400, detail="Forfait invalide")
    
    package = PAYMENT_PACKAGES[request_data.package_id]
    base_amount = package["amount"]
    discount_percent = 0
    discount_type = ""
    
    # 1) Loyalty discount: 15% from 2nd order
    if request_data.customer_email:
        client = await db.client_history.find_one(
            {"email": request_data.customer_email.lower()}, {"_id": 0}
        )
        if client and client.get("orders_count", 0) >= 1:
            discount_percent = 15
            discount_type = "fidélité"
    
    # 2) Referral discount: 10% (only if no loyalty discount already applied)
    if discount_percent == 0 and request_data.referral_code:
        referral = await db.referral_codes.find_one(
            {"code": request_data.referral_code.upper(), "is_active": True}, {"_id": 0}
        )
        if referral:
            discount_percent = 10
            discount_type = "parrainage"
            # Record referral use
            referral_use = ReferralUse(
                referral_code=request_data.referral_code.upper(),
                referred_email=request_data.customer_email or "",
                referred_name=request_data.customer_name,
                discount_applied=10.0
            )
            doc_ref = referral_use.model_dump()
            doc_ref['created_at'] = doc_ref['created_at'].isoformat()
            await db.referral_uses.insert_one(doc_ref)
            # Increment referral uses count
            await db.referral_codes.update_one(
                {"code": request_data.referral_code.upper()},
                {"$inc": {"uses_count": 1}}
            )
    
    # Calculate final amount
    final_amount = round(base_amount * (1 - discount_percent / 100), 2)
    
    # Build URLs from provided origin
    origin_url = request_data.origin_url.rstrip('/')
    success_url = f"{origin_url}/tarifs?payment=success&session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{origin_url}/tarifs?payment=cancelled"
    
    # Initialize Stripe
    host_url = str(request.base_url).rstrip('/')
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    # Create checkout session
    metadata = {
        "package_id": request_data.package_id,
        "package_name": package["name"],
        "customer_email": request_data.customer_email or "",
        "customer_name": request_data.customer_name or "",
        "discount_percent": str(discount_percent),
        "discount_type": discount_type,
        "original_amount": str(base_amount)
    }
    
    checkout_request = CheckoutSessionRequest(
        amount=final_amount,
        currency=package["currency"],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata=metadata
    )
    
    try:
        session = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Record client order for loyalty tracking
        if request_data.customer_email:
            await db.client_history.update_one(
                {"email": request_data.customer_email.lower()},
                {
                    "$inc": {"orders_count": 1},
                    "$set": {
                        "last_order_at": datetime.now(timezone.utc).isoformat(),
                        "name": request_data.customer_name
                    },
                    "$setOnInsert": {
                        "id": str(uuid.uuid4()),
                        "created_at": datetime.now(timezone.utc).isoformat()
                    }
                },
                upsert=True
            )
        
        # Create payment transaction record
        transaction = PaymentTransaction(
            session_id=session.session_id,
            package_id=request_data.package_id,
            package_name=package["name"],
            amount=final_amount,
            currency=package["currency"],
            email=request_data.customer_email,
            customer_name=request_data.customer_name,
            status="pending",
            payment_status="initiated",
            metadata=metadata
        )
        
        doc = transaction.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        doc['updated_at'] = doc['updated_at'].isoformat()
        await db.payment_transactions.insert_one(doc)
        
        return {
            "url": session.url,
            "session_id": session.session_id,
            "discount_applied": discount_percent,
            "discount_type": discount_type,
            "original_amount": base_amount,
            "final_amount": final_amount
        }
        
    except Exception as e:
        logger.error(f"Stripe checkout error: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de la création du paiement")

@api_router.get("/payments/status/{session_id}")
async def get_payment_status(session_id: str, request: Request):
    """Get payment status and update transaction"""
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Stripe non configuré")
    
    # Check if already processed
    transaction = await db.payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
    if transaction and transaction.get("payment_status") == "paid":
        return {
            "status": "complete",
            "payment_status": "paid",
            "package_name": transaction.get("package_name"),
            "amount": transaction.get("amount"),
            "currency": transaction.get("currency")
        }
    
    # Initialize Stripe and check status
    host_url = str(request.base_url).rstrip('/')
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    try:
        status = await stripe_checkout.get_checkout_status(session_id)
        
        # Update transaction
        new_status = "paid" if status.payment_status == "paid" else status.status
        await db.payment_transactions.update_one(
            {"session_id": session_id},
            {"$set": {
                "status": status.status,
                "payment_status": status.payment_status,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        return {
            "status": status.status,
            "payment_status": status.payment_status,
            "amount": status.amount_total / 100,  # Convert from cents
            "currency": status.currency,
            "metadata": status.metadata
        }
        
    except Exception as e:
        logger.error(f"Payment status error: {str(e)}")
        raise HTTPException(status_code=500, detail="Erreur lors de la vérification du paiement")

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks"""
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Stripe non configuré")
    
    body = await request.body()
    sig_header = request.headers.get("Stripe-Signature")
    
    host_url = str(request.base_url).rstrip('/')
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    
    try:
        webhook_response = await stripe_checkout.handle_webhook(body, sig_header)
        
        # Update transaction based on webhook event
        if webhook_response.session_id:
            await db.payment_transactions.update_one(
                {"session_id": webhook_response.session_id},
                {"$set": {
                    "status": webhook_response.event_type,
                    "payment_status": webhook_response.payment_status,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }}
            )
        
        return {"received": True}
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=400, detail="Webhook error")

# ==================== PAYPAL ROUTES ====================

@api_router.post("/paypal/calculate")
async def calculate_paypal_amount(request: Request):
    """Calculate the final amount with discounts for PayPal"""
    body = await request.json()
    package_id = body.get("package_id")
    
    if package_id not in PAYMENT_PACKAGES:
        raise HTTPException(status_code=400, detail="Forfait invalide")
    
    package = PAYMENT_PACKAGES[package_id]
    base_amount = package["amount"]
    discount_percent = 0
    discount_type = ""
    
    customer_email = body.get("customer_email", "")
    referral_code = body.get("referral_code")
    
    # Loyalty discount
    if customer_email:
        client_doc = await db.client_history.find_one({"email": customer_email.lower()}, {"_id": 0})
        if client_doc and client_doc.get("orders_count", 0) >= 1:
            discount_percent = 15
            discount_type = "fidélité"
    
    # Referral discount
    if discount_percent == 0 and referral_code:
        referral = await db.referral_codes.find_one(
            {"code": referral_code.upper(), "is_active": True}, {"_id": 0}
        )
        if referral:
            discount_percent = 10
            discount_type = "parrainage"
    
    final_amount = round(base_amount * (1 - discount_percent / 100), 2)
    
    return {
        "package_name": package["name"],
        "base_amount": base_amount,
        "discount_percent": discount_percent,
        "discount_type": discount_type,
        "final_amount": final_amount
    }

@api_router.post("/paypal/record")
async def record_paypal_payment(request: Request):
    """Record a completed PayPal payment"""
    body = await request.json()
    order_id = body.get("order_id", "")
    package_id = body.get("package_id", "")
    customer_email = body.get("customer_email", "")
    customer_name = body.get("customer_name", "")
    amount = body.get("amount", 0)
    referral_code = body.get("referral_code")
    
    package = PAYMENT_PACKAGES.get(package_id, {})
    
    # Store transaction
    transaction = PaymentTransaction(
        session_id=order_id,
        package_id=package_id,
        package_name=package.get("name", package_id),
        amount=amount,
        currency="eur",
        email=customer_email,
        customer_name=customer_name,
        status="completed",
        payment_status="paid",
        metadata={"payment_method": "paypal"}
    )
    doc = transaction.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.payment_transactions.insert_one(doc)
    
    # Record client order for loyalty tracking
    if customer_email:
        await db.client_history.update_one(
            {"email": customer_email.lower()},
            {
                "$inc": {"orders_count": 1},
                "$set": {
                    "last_order_at": datetime.now(timezone.utc).isoformat(),
                    "name": customer_name
                },
                "$setOnInsert": {
                    "id": str(uuid.uuid4()),
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
            },
            upsert=True
        )
    
    # Handle referral use
    if referral_code:
        referral = await db.referral_codes.find_one({"code": referral_code.upper(), "is_active": True}, {"_id": 0})
        if referral:
            referral_use = ReferralUse(
                referral_code=referral_code.upper(),
                referred_email=customer_email,
                referred_name=customer_name,
                discount_applied=10.0
            )
            doc_ref = referral_use.model_dump()
            doc_ref['created_at'] = doc_ref['created_at'].isoformat()
            await db.referral_uses.insert_one(doc_ref)
            await db.referral_codes.update_one(
                {"code": referral_code.upper()},
                {"$inc": {"uses_count": 1}}
            )
    
    return {"success": True, "order_id": order_id}

# ==================== FORUM PUBLIC ROUTES ====================

@api_router.get("/forum/categories")
async def get_forum_categories():
    """Get all forum categories"""
    return [cat.model_dump() for cat in FORUM_CATEGORIES]

@api_router.post("/forum/register", response_model=ForumTokenResponse)
async def register_forum_user(input_data: ForumUserRegister):
    """Register a new forum user (email-based or anonymous)"""
    
    # Check if pseudo is already taken
    existing_pseudo = await db.forum_users.find_one({"pseudo": input_data.pseudo})
    if existing_pseudo:
        raise HTTPException(status_code=400, detail="Ce pseudonyme est déjà utilisé")
    
    if input_data.is_anonymous:
        # Anonymous registration - no email/password required
        user = ForumUser(
            pseudo=input_data.pseudo,
            is_anonymous=True,
            avatar_color=f"#{uuid.uuid4().hex[:6]}"  # Random color
        )
    else:
        # Email registration
        if not input_data.email or not input_data.password:
            raise HTTPException(status_code=400, detail="Email et mot de passe requis pour l'inscription classique")
        
        # Check if email is already used
        existing_email = await db.forum_users.find_one({"email": input_data.email})
        if existing_email:
            raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")
        
        user = ForumUser(
            email=input_data.email,
            password_hash=hash_password(input_data.password),
            pseudo=input_data.pseudo,
            is_anonymous=False,
            avatar_color=f"#{uuid.uuid4().hex[:6]}"
        )
    
    doc = user.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.forum_users.insert_one(doc)
    
    token = create_forum_token(user.id, user.pseudo, user.is_anonymous)
    
    return ForumTokenResponse(
        access_token=token,
        user_id=user.id,
        pseudo=user.pseudo,
        is_anonymous=user.is_anonymous
    )

@api_router.post("/forum/login", response_model=ForumTokenResponse)
async def login_forum_user(credentials: ForumUserLogin):
    """Login for email-based forum users"""
    user = await db.forum_users.find_one({"email": credentials.email}, {"_id": 0})
    
    if not user:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    if user.get('is_anonymous'):
        raise HTTPException(status_code=401, detail="Ce compte est anonyme, pas de connexion possible")
    
    if not verify_password(credentials.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    if user.get('is_banned'):
        raise HTTPException(status_code=403, detail="Votre compte a été suspendu")
    
    token = create_forum_token(user['id'], user['pseudo'], False)
    
    return ForumTokenResponse(
        access_token=token,
        user_id=user['id'],
        pseudo=user['pseudo'],
        is_anonymous=False
    )

@api_router.get("/forum/topics")
async def get_forum_topics(
    category_id: Optional[str] = None,
    page: int = 1,
    limit: int = 20
):
    """Get forum topics, optionally filtered by category"""
    query = {"status": "published"}
    if category_id:
        query["category_id"] = category_id
    
    skip = (page - 1) * limit
    
    topics = await db.forum_topics.find(query, {"_id": 0}).sort([
        ("is_pinned", -1),
        ("created_at", -1)
    ]).skip(skip).limit(limit).to_list(limit)
    
    total = await db.forum_topics.count_documents(query)
    
    for topic in topics:
        if isinstance(topic.get('created_at'), str):
            topic['created_at'] = datetime.fromisoformat(topic['created_at'])
    
    return {
        "topics": topics,
        "total": total,
        "page": page,
        "pages": (total + limit - 1) // limit
    }

@api_router.get("/forum/topics/{topic_id}")
async def get_forum_topic(topic_id: str):
    """Get a single topic with its replies"""
    topic = await db.forum_topics.find_one({"id": topic_id, "status": "published"}, {"_id": 0})
    
    if not topic:
        raise HTTPException(status_code=404, detail="Sujet non trouvé")
    
    # Increment views
    await db.forum_topics.update_one({"id": topic_id}, {"$inc": {"views": 1}})
    
    # Get replies
    replies = await db.forum_replies.find(
        {"topic_id": topic_id, "status": "published"},
        {"_id": 0}
    ).sort("created_at", 1).to_list(1000)
    
    for reply in replies:
        if isinstance(reply.get('created_at'), str):
            reply['created_at'] = datetime.fromisoformat(reply['created_at'])
    
    if isinstance(topic.get('created_at'), str):
        topic['created_at'] = datetime.fromisoformat(topic['created_at'])
    
    return {
        "topic": topic,
        "replies": replies
    }

@api_router.post("/forum/topics")
async def create_forum_topic(
    input_data: ForumTopicCreate,
    user: dict = Depends(get_current_forum_user)
):
    """Create a new forum topic"""
    # Validate category
    valid_categories = [cat.id for cat in FORUM_CATEGORIES]
    if input_data.category_id not in valid_categories:
        raise HTTPException(status_code=400, detail="Catégorie invalide")
    
    topic = ForumTopic(
        category_id=input_data.category_id,
        title=input_data.title,
        content=input_data.content,
        author_id=user["sub"],
        author_pseudo=user["pseudo"],
        is_anonymous=user.get("is_anonymous", False)
    )
    
    doc = topic.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.forum_topics.insert_one(doc)
    
    return {"success": True, "topic_id": topic.id}

@api_router.post("/forum/topics/{topic_id}/replies")
async def create_forum_reply(
    topic_id: str,
    input_data: ForumReplyCreate,
    user: dict = Depends(get_current_forum_user)
):
    """Add a reply to a topic"""
    # Check topic exists and is not locked
    topic = await db.forum_topics.find_one({"id": topic_id, "status": "published"}, {"_id": 0})
    if not topic:
        raise HTTPException(status_code=404, detail="Sujet non trouvé")
    
    if topic.get('is_locked'):
        raise HTTPException(status_code=403, detail="Ce sujet est verrouillé")
    
    reply = ForumReply(
        topic_id=topic_id,
        content=input_data.content,
        author_id=user["sub"],
        author_pseudo=user["pseudo"],
        is_anonymous=user.get("is_anonymous", False)
    )
    
    doc = reply.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.forum_replies.insert_one(doc)
    
    # Update topic replies count and updated_at
    await db.forum_topics.update_one(
        {"id": topic_id},
        {
            "$inc": {"replies_count": 1},
            "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
        }
    )
    
    return {"success": True, "reply_id": reply.id}

@api_router.post("/forum/topics/{topic_id}/like")
async def like_topic(topic_id: str, user: dict = Depends(get_current_forum_user)):
    """Like/unlike a topic"""
    topic = await db.forum_topics.find_one({"id": topic_id}, {"_id": 0})
    if not topic:
        raise HTTPException(status_code=404, detail="Sujet non trouvé")
    
    user_id = user["sub"]
    likes = topic.get('likes', [])
    
    if user_id in likes:
        # Unlike
        await db.forum_topics.update_one({"id": topic_id}, {"$pull": {"likes": user_id}})
        return {"liked": False, "likes_count": len(likes) - 1}
    else:
        # Like
        await db.forum_topics.update_one({"id": topic_id}, {"$push": {"likes": user_id}})
        return {"liked": True, "likes_count": len(likes) + 1}

@api_router.post("/forum/replies/{reply_id}/like")
async def like_reply(reply_id: str, user: dict = Depends(get_current_forum_user)):
    """Like/unlike a reply"""
    reply = await db.forum_replies.find_one({"id": reply_id}, {"_id": 0})
    if not reply:
        raise HTTPException(status_code=404, detail="Réponse non trouvée")
    
    user_id = user["sub"]
    likes = reply.get('likes', [])
    
    if user_id in likes:
        await db.forum_replies.update_one({"id": reply_id}, {"$pull": {"likes": user_id}})
        return {"liked": False, "likes_count": len(likes) - 1}
    else:
        await db.forum_replies.update_one({"id": reply_id}, {"$push": {"likes": user_id}})
        return {"liked": True, "likes_count": len(likes) + 1}

@api_router.post("/forum/report")
async def report_content(
    input_data: ForumReportCreate,
    user: dict = Depends(get_current_forum_user)
):
    """Report a topic or reply"""
    report = ForumReport(
        reporter_id=user["sub"],
        target_type=input_data.target_type,
        target_id=input_data.target_id,
        reason=input_data.reason
    )
    
    doc = report.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.forum_reports.insert_one(doc)
    
    return {"success": True, "message": "Signalement envoyé. Merci de votre vigilance."}

# ==================== AUTH ROUTES (ADMIN) ====================

@api_router.post("/auth/login", response_model=TokenResponse)
async def admin_login(credentials: AdminLogin):
    admin = await db.admins.find_one({"email": credentials.email}, {"_id": 0})
    
    if not admin:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    if not verify_password(credentials.password, admin['password_hash']):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    token = create_token(admin['id'], admin['email'], is_admin=True)
    
    return TokenResponse(
        access_token=token,
        admin_name=admin['nom']
    )

@api_router.get("/auth/me")
async def get_current_user(admin: dict = Depends(get_current_admin)):
    return {"email": admin.get("email"), "id": admin.get("sub")}

# ==================== ADMIN ROUTES ====================

@api_router.get("/admin/contacts", response_model=List[ContactRequest])
async def get_all_contacts(
    status: Optional[str] = None,
    admin: dict = Depends(get_current_admin)
):
    query = {}
    if status:
        query["status"] = status
    
    contacts = await db.contacts.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    
    for contact in contacts:
        if isinstance(contact.get('created_at'), str):
            contact['created_at'] = datetime.fromisoformat(contact['created_at'])
    
    return contacts

@api_router.get("/admin/contacts/{contact_id}", response_model=ContactRequest)
async def get_contact(contact_id: str, admin: dict = Depends(get_current_admin)):
    contact = await db.contacts.find_one({"id": contact_id}, {"_id": 0})
    
    if not contact:
        raise HTTPException(status_code=404, detail="Contact non trouvé")
    
    if isinstance(contact.get('created_at'), str):
        contact['created_at'] = datetime.fromisoformat(contact['created_at'])
    
    return contact

@api_router.patch("/admin/contacts/{contact_id}", response_model=ContactRequest)
async def update_contact(
    contact_id: str,
    update_data: ContactRequestUpdate,
    admin: dict = Depends(get_current_admin)
):
    update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="Aucune donnée à mettre à jour")
    
    result = await db.contacts.update_one(
        {"id": contact_id},
        {"$set": update_dict}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Contact non trouvé")
    
    contact = await db.contacts.find_one({"id": contact_id}, {"_id": 0})
    
    if isinstance(contact.get('created_at'), str):
        contact['created_at'] = datetime.fromisoformat(contact['created_at'])
    
    return contact

@api_router.delete("/admin/contacts/{contact_id}")
async def delete_contact(contact_id: str, admin: dict = Depends(get_current_admin)):
    result = await db.contacts.delete_one({"id": contact_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Contact non trouvé")
    
    return {"success": True, "message": "Contact supprimé"}

@api_router.get("/admin/stats")
async def get_stats(admin: dict = Depends(get_current_admin)):
    total = await db.contacts.count_documents({})
    nouveau = await db.contacts.count_documents({"status": "nouveau"})
    en_cours = await db.contacts.count_documents({"status": "en_cours"})
    traite = await db.contacts.count_documents({"status": "traite"})
    
    return {
        "total": total,
        "nouveau": nouveau,
        "en_cours": en_cours,
        "traite": traite
    }

# FAQ Admin Routes
@api_router.post("/admin/faq", response_model=FAQItem)
async def create_faq(input_data: FAQItemCreate, admin: dict = Depends(get_current_admin)):
    faq_obj = FAQItem(**input_data.model_dump())
    doc = faq_obj.model_dump()
    await db.faq.insert_one(doc)
    return faq_obj

@api_router.delete("/admin/faq/{faq_id}")
async def delete_faq(faq_id: str, admin: dict = Depends(get_current_admin)):
    result = await db.faq.delete_one({"id": faq_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="FAQ non trouvée")
    
    return {"success": True, "message": "FAQ supprimée"}

# Avis Admin Routes
@api_router.get("/admin/avis", response_model=List[Avis])
async def get_all_avis(
    status: Optional[str] = None,
    admin: dict = Depends(get_current_admin)
):
    query = {}
    if status:
        query["status"] = status
    
    avis_list = await db.avis.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    
    for avis in avis_list:
        if isinstance(avis.get('created_at'), str):
            avis['created_at'] = datetime.fromisoformat(avis['created_at'])
    
    return avis_list

@api_router.get("/admin/avis/stats")
async def get_avis_stats(admin: dict = Depends(get_current_admin)):
    total = await db.avis.count_documents({})
    en_attente = await db.avis.count_documents({"status": "en_attente"})
    publie = await db.avis.count_documents({"status": "publie"})
    rejete = await db.avis.count_documents({"status": "rejete"})
    
    return {
        "total": total,
        "en_attente": en_attente,
        "publie": publie,
        "rejete": rejete
    }

@api_router.patch("/admin/avis/{avis_id}")
async def update_avis_status(
    avis_id: str,
    update_data: AvisUpdate,
    admin: dict = Depends(get_current_admin)
):
    update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="Aucune donnée à mettre à jour")
    
    result = await db.avis.update_one(
        {"id": avis_id},
        {"$set": update_dict}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Avis non trouvé")
    
    return {"success": True, "message": "Avis mis à jour"}

@api_router.delete("/admin/avis/{avis_id}")
async def delete_avis(avis_id: str, admin: dict = Depends(get_current_admin)):
    result = await db.avis.delete_one({"id": avis_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Avis non trouvé")
    
    return {"success": True, "message": "Avis supprimé"}

# ==================== FORUM ADMIN ROUTES ====================

@api_router.get("/admin/forum/stats")
async def get_forum_stats(admin: dict = Depends(get_current_admin)):
    total_users = await db.forum_users.count_documents({})
    total_topics = await db.forum_topics.count_documents({})
    total_replies = await db.forum_replies.count_documents({})
    pending_reports = await db.forum_reports.count_documents({"status": "pending"})
    banned_users = await db.forum_users.count_documents({"is_banned": True})
    
    return {
        "total_users": total_users,
        "total_topics": total_topics,
        "total_replies": total_replies,
        "pending_reports": pending_reports,
        "banned_users": banned_users
    }

@api_router.get("/admin/forum/reports")
async def get_forum_reports(
    status: Optional[str] = None,
    admin: dict = Depends(get_current_admin)
):
    query = {}
    if status:
        query["status"] = status
    
    reports = await db.forum_reports.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    
    for report in reports:
        if isinstance(report.get('created_at'), str):
            report['created_at'] = datetime.fromisoformat(report['created_at'])
    
    return reports

@api_router.patch("/admin/forum/reports/{report_id}")
async def update_report_status(
    report_id: str,
    status: str,
    admin: dict = Depends(get_current_admin)
):
    if status not in ["reviewed", "dismissed"]:
        raise HTTPException(status_code=400, detail="Statut invalide")
    
    result = await db.forum_reports.update_one(
        {"id": report_id},
        {"$set": {"status": status}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Signalement non trouvé")
    
    return {"success": True}

@api_router.delete("/admin/forum/topics/{topic_id}")
async def admin_delete_topic(topic_id: str, admin: dict = Depends(get_current_admin)):
    result = await db.forum_topics.update_one(
        {"id": topic_id},
        {"$set": {"status": "deleted"}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Sujet non trouvé")
    
    return {"success": True, "message": "Sujet supprimé"}

@api_router.delete("/admin/forum/replies/{reply_id}")
async def admin_delete_reply(reply_id: str, admin: dict = Depends(get_current_admin)):
    result = await db.forum_replies.update_one(
        {"id": reply_id},
        {"$set": {"status": "deleted"}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Réponse non trouvée")
    
    return {"success": True, "message": "Réponse supprimée"}

@api_router.post("/admin/forum/users/{user_id}/ban")
async def ban_forum_user(
    user_id: str,
    reason: str = "Violation des règles du forum",
    admin: dict = Depends(get_current_admin)
):
    result = await db.forum_users.update_one(
        {"id": user_id},
        {"$set": {"is_banned": True, "ban_reason": reason}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    return {"success": True, "message": "Utilisateur banni"}

@api_router.post("/admin/forum/users/{user_id}/unban")
async def unban_forum_user(user_id: str, admin: dict = Depends(get_current_admin)):
    result = await db.forum_users.update_one(
        {"id": user_id},
        {"$set": {"is_banned": False, "ban_reason": None}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    return {"success": True, "message": "Utilisateur débanni"}

@api_router.get("/admin/forum/users")
async def get_forum_users(admin: dict = Depends(get_current_admin)):
    users = await db.forum_users.find({}, {"_id": 0, "password_hash": 0}).sort("created_at", -1).to_list(1000)
    
    for user in users:
        if isinstance(user.get('created_at'), str):
            user['created_at'] = datetime.fromisoformat(user['created_at'])
    
    return users

# ==================== ADMIN REFERRAL STATS ====================

@api_router.get("/admin/referrals")
async def get_admin_referrals(admin: dict = Depends(get_current_admin)):
    """Get all referral codes with usage stats"""
    codes = await db.referral_codes.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    uses = await db.referral_uses.find({}, {"_id": 0}).sort("created_at", -1).to_list(5000)
    
    total_codes = len(codes)
    active_codes = sum(1 for c in codes if c.get("is_active", True))
    total_uses = sum(c.get("uses_count", 0) for c in codes)
    total_discount_given = sum(u.get("discount_applied", 0) for u in uses)
    
    return {
        "codes": codes,
        "recent_uses": uses[:50],
        "stats": {
            "total_codes": total_codes,
            "active_codes": active_codes,
            "total_uses": total_uses,
            "total_discount_given": total_discount_given
        }
    }

# ==================== BOOKING ROUTES ====================

AVAILABLE_SLOTS = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00"]

@api_router.get("/bookings/slots/{date}")
async def get_available_slots(date: str):
    """Get available time slots for a given date"""
    booked = await db.bookings.find(
        {"date": date, "status": {"$ne": "annule"}}, {"_id": 0, "time_slot": 1}
    ).to_list(100)
    booked_slots = {b["time_slot"] for b in booked}
    available = [s for s in AVAILABLE_SLOTS if s not in booked_slots]
    return {"date": date, "slots": available}

@api_router.post("/bookings")
async def create_booking(data: BookingCreate):
    """Create a new booking"""
    existing = await db.bookings.find_one(
        {"date": data.date, "time_slot": data.time_slot, "status": {"$ne": "annule"}}, {"_id": 0}
    )
    if existing:
        raise HTTPException(status_code=409, detail="Ce créneau n'est plus disponible")
    
    booking = Booking(**data.model_dump())
    doc = booking.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.bookings.insert_one(doc)
    return {"success": True, "booking_id": booking.id, "message": "Rendez-vous confirmé"}

@api_router.get("/admin/bookings")
async def get_admin_bookings(admin: dict = Depends(get_current_admin)):
    bookings = await db.bookings.find({}, {"_id": 0}).sort("date", -1).to_list(500)
    return bookings

@api_router.patch("/admin/bookings/{booking_id}")
async def update_booking_status(booking_id: str, status: str, admin: dict = Depends(get_current_admin)):
    result = await db.bookings.update_one({"id": booking_id}, {"$set": {"status": status}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Rendez-vous non trouvé")
    return {"success": True}

# ==================== CLIENT PORTAL ROUTES ====================

@api_router.post("/client/register")
async def register_client(data: ClientRegister):
    existing = await db.client_users.find_one({"email": data.email.lower()}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=409, detail="Un compte existe déjà avec cet email")
    
    client = ClientUser(
        email=data.email.lower(),
        password_hash=hash_password(data.password),
        name=data.name,
        phone=data.phone
    )
    doc = client.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.client_users.insert_one(doc)
    
    token = create_client_token(client.id, client.email, client.name)
    return {"access_token": token, "token_type": "bearer", "client_name": client.name, "client_id": client.id}

@api_router.post("/client/login")
async def login_client(data: ClientLogin):
    client = await db.client_users.find_one({"email": data.email.lower()}, {"_id": 0})
    if not client or not verify_password(data.password, client["password_hash"]):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    token = create_client_token(client["id"], client["email"], client["name"])
    return {"access_token": token, "token_type": "bearer", "client_name": client["name"], "client_id": client["id"]}

@api_router.get("/client/profile")
async def get_client_profile(client: dict = Depends(get_current_client)):
    user = await db.client_users.find_one({"id": client["sub"]}, {"_id": 0, "password_hash": 0})
    if not user:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    return user

@api_router.get("/client/cases")
async def get_client_cases(client: dict = Depends(get_current_client)):
    cases = await db.client_cases.find({"client_id": client["sub"]}, {"_id": 0}).sort("updated_at", -1).to_list(100)
    return cases

@api_router.get("/client/cases/{case_id}")
async def get_client_case(case_id: str, client: dict = Depends(get_current_client)):
    case = await db.client_cases.find_one({"id": case_id, "client_id": client["sub"]}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Dossier non trouvé")
    return case

@api_router.get("/client/notifications")
async def get_client_notifications(client: dict = Depends(get_current_client)):
    notifs = await db.client_notifications.find(
        {"client_id": client["sub"]}, {"_id": 0}
    ).sort("created_at", -1).to_list(50)
    unread = sum(1 for n in notifs if not n.get("read"))
    return {"notifications": notifs, "unread_count": unread}

@api_router.patch("/client/notifications/{notif_id}/read")
async def mark_notification_read(notif_id: str, client: dict = Depends(get_current_client)):
    await db.client_notifications.update_one(
        {"id": notif_id, "client_id": client["sub"]},
        {"$set": {"read": True}}
    )
    return {"success": True}

@api_router.patch("/client/notifications/read-all")
async def mark_all_notifications_read(client: dict = Depends(get_current_client)):
    await db.client_notifications.update_many(
        {"client_id": client["sub"], "read": False},
        {"$set": {"read": True}}
    )
    return {"success": True}

# Admin client management
@api_router.get("/admin/clients")
async def get_admin_clients(admin: dict = Depends(get_current_admin)):
    clients = await db.client_users.find({}, {"_id": 0, "password_hash": 0}).sort("created_at", -1).to_list(500)
    for c in clients:
        c["cases_count"] = await db.client_cases.count_documents({"client_id": c["id"]})
    return clients

@api_router.post("/admin/clients/{client_id}/cases")
async def create_client_case(client_id: str, request: Request, admin: dict = Depends(get_current_admin)):
    body = await request.json()
    client_exists = await db.client_users.find_one({"id": client_id}, {"_id": 0})
    if not client_exists:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    case = ClientCase(
        client_id=client_id,
        title=body.get("title", ""),
        description=body.get("description", "")
    )
    doc = case.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.client_cases.insert_one(doc)
    
    # Create notification for client
    notif = {
        "id": str(uuid.uuid4()),
        "client_id": client_id,
        "type": "case_created",
        "title": "Nouveau dossier créé",
        "message": f"Votre dossier \"{case.title}\" a été créé par votre accompagnant.",
        "case_id": case.id,
        "read": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.client_notifications.insert_one(notif)
    
    return {"success": True, "case_id": case.id}

@api_router.patch("/admin/cases/{case_id}")
async def update_client_case(case_id: str, request: Request, admin: dict = Depends(get_current_admin)):
    body = await request.json()
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
    
    # Get case to find client_id for notification
    case = await db.client_cases.find_one({"id": case_id}, {"_id": 0})
    if not case:
        raise HTTPException(status_code=404, detail="Dossier non trouvé")
    
    notification_message = ""
    
    if "status" in body:
        update_data["status"] = body["status"]
        status_labels = {"en_cours": "en cours", "en_attente": "en attente", "termine": "terminé"}
        notification_message = f"Le statut de votre dossier \"{case.get('title', '')}\" est passé à : {status_labels.get(body['status'], body['status'])}."
    
    if "notes" in body:
        update_data["notes"] = body["notes"]
    
    if "update_message" in body:
        new_update = {
            "message": body["update_message"],
            "date": datetime.now(timezone.utc).isoformat(),
            "author": "Administrateur"
        }
        await db.client_cases.update_one({"id": case_id}, {"$push": {"updates": new_update}})
        notification_message = f"Nouvelle mise à jour sur votre dossier \"{case.get('title', '')}\" : {body['update_message']}"
    
    await db.client_cases.update_one({"id": case_id}, {"$set": update_data})
    
    # Create notification for client
    if notification_message and case.get("client_id"):
        notif = {
            "id": str(uuid.uuid4()),
            "client_id": case["client_id"],
            "type": "case_updated",
            "title": "Dossier mis à jour",
            "message": notification_message,
            "case_id": case_id,
            "read": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.client_notifications.insert_one(notif)
    
    return {"success": True}

# ==================== SIMULATOR ROUTES ====================

@api_router.post("/simulator/result")
async def save_simulator_result(request: Request):
    body = await request.json()
    result = SimulatorResult(
        answers=body.get("answers", {}),
        profile=body.get("profile", ""),
        recommendations=body.get("recommendations", []),
        email=body.get("email")
    )
    doc = result.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['droits'] = body.get("droits", [])
    doc['demarches'] = body.get("demarches", [])
    doc['delais'] = body.get("delais", [])
    doc['prestation'] = body.get("prestation", "")
    await db.simulator_results.insert_one(doc)

    # HubSpot CRM sync (when configured)
    hubspot_portal = os.environ.get('HUBSPOT_PORTAL_ID')
    hubspot_token = os.environ.get('HUBSPOT_ACCESS_TOKEN')
    if hubspot_portal and hubspot_token and body.get("email"):
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"https://api.hubapi.com/crm/v3/objects/contacts",
                    headers={"Authorization": f"Bearer {hubspot_token}", "Content-Type": "application/json"},
                    json={
                        "properties": {
                            "email": body["email"],
                            "firstname": body.get("nom", ""),
                            "lastname": "",
                            "company": "Simulateur Diagnostic",
                            "lifecyclestage": "lead",
                            "hs_lead_status": "NEW",
                            "notes_last_updated": f"Profil: {body.get('profile', '')}. Recommandations: {'; '.join(body.get('recommendations', []))}"
                        }
                    }
                )
            logger.info(f"HubSpot contact created for {body['email']}")
        except Exception as e:
            logger.error(f"HubSpot sync error: {e}")

    return {"success": True, "id": result.id}

@api_router.get("/admin/simulator/stats")
async def get_simulator_stats(admin: dict = Depends(get_current_admin)):
    total = await db.simulator_results.count_documents({})
    results = await db.simulator_results.find({}, {"_id": 0}).sort("created_at", -1).to_list(50)
    return {"total": total, "recent": results}

# ==================== STRATEGIIA ROUTES ====================

STRATEGIIA_SYSTEM_PROMPT = """Tu es StratégiIA, l'outil d'analyse stratégique exclusif de Stratégie & Expertise Santé.

Tu analyses les dossiers de victimes d'accidents du travail, maladies professionnelles, litiges assurantiels et demandes MDPH en t'appuyant sur :

1. JURISPRUDENCES DE RÉFÉRENCE :
- Cass. soc. 2019 : L'employeur doit prouver qu'il a pris les mesures de prévention (obligation de sécurité de résultat → obligation de moyens renforcée depuis 2015)
- Cass. 2e civ. 2020 : Le taux d'IPP doit tenir compte de l'incidence professionnelle réelle
- CE 2018 : La MDPH doit motiver ses décisions de refus et répondre sous 4 mois
- Cass. 2e civ. 2021 : La faute inexcusable peut être reconnue même en cas de respect partiel des normes
- Cass. 2e civ. 2022 : Le silence de la CPAM au-delà du délai vaut acceptation implicite
- TA/CAA multiples : Le CRRMP doit examiner le lien direct et essentiel avec le travail habituel

2. STATISTIQUES CNAM (données publiques) :
- ~650 000 AT/an, ~50 000 MP/an reconnues
- TMS (Tableau 57) = 87% des MP reconnues
- Taux moyen d'IPP AT : 9%, MP : 14%
- Délai moyen instruction CPAM : 3-4 mois
- Taux de contestation aboutissant : ~35% en CRA, ~45% au tribunal
- Faute inexcusable reconnue dans ~60% des cas portés en justice

3. BARÈMES IPP OFFICIELS :
- Taux < 10% : capital forfaitaire (barème annexe Code SS)
- Taux ≥ 10% : rente = salaire × taux utile (moitié jusqu'à 50%, totalité au-delà)
- Barème indicatif d'invalidité AT/MP (annexe à l'art. R434-32 du Code SS)

RÈGLES :
- Réponds TOUJOURS en français
- Structure ta réponse en sections claires : Analyse de la situation, Jurisprudences applicables, Stratégie recommandée, Chances de succès estimées, Prochaines étapes
- Donne un score de pertinence sur 100 basé sur la similarité avec des cas similaires
- Sois précis et factuel, cite les textes et jurisprudences pertinents
- Rappelle TOUJOURS que c'est un outil d'aide à la décision et non un conseil juridique
- Si des cas anonymisés similaires existent dans la base, mentionne les statistiques de résultats"""

STRATEGIIA_BASIC_PROMPT = """Analyse BASIQUE demandée. Fournis :
1. Une synthèse courte de la situation (3-4 lignes)
2. Les principaux droits identifiés (liste à puces, max 4)
3. La première démarche prioritaire à effectuer
4. Un score de pertinence approximatif sur 100

Reste concis (max 300 mots). Mentionne qu'un rapport complet est disponible pour une analyse approfondie."""

STRATEGIIA_PREMIUM_PROMPT = """Analyse COMPLÈTE demandée. Fournis un rapport détaillé structuré :

## Analyse de votre situation
(Résumé détaillé en 5-6 lignes)

## Jurisprudences applicables
(2-3 jurisprudences pertinentes avec références et ce qu'elles impliquent)

## Vos droits identifiés
(Liste exhaustive avec explications)

## Stratégie recommandée
(Plan d'action en étapes numérotées avec justification)

## Estimation des chances de succès
(Score sur 100 avec explication des facteurs pris en compte)

## Délais importants
(Dates limites et échéances à respecter)

## Prochaines étapes immédiates
(3 actions concrètes à réaliser dans les prochains jours)

Sois exhaustif et précis (600-800 mots)."""

# ==================== DOSSIER EXPRESS ====================

DOSSIER_EXPRESS_PROMPT = """Tu es un expert en droit de la sécurité sociale, accidents du travail, maladies professionnelles et handicap (MDPH).
On te fournit les documents et la description d'un dossier client. Rédige un RAPPORT D'ANALYSE COMPLET et PROFESSIONNEL.

Structure ton rapport ainsi :

# RAPPORT D'ANALYSE - DOSSIER EXPRESS
## Stratégie & Expertise Santé

### 1. SYNTHÈSE DU DOSSIER
(Résumé factuel de la situation en 5-6 lignes)

### 2. ANALYSE DES DOCUMENTS
(Analyse détaillée de chaque document fourni, points forts et faiblesses)

### 3. CADRE JURIDIQUE APPLICABLE
(Textes de loi, articles du Code de la Sécurité Sociale, jurisprudences pertinentes)

### 4. DROITS IDENTIFIÉS
(Liste exhaustive des droits avec explications claires)

### 5. POINTS DE VIGILANCE
(Faiblesses du dossier, pièces manquantes, risques identifiés)

### 6. STRATÉGIE RECOMMANDÉE
(Plan d'action en étapes numérotées avec justification et délais)

### 7. ESTIMATION DES CHANCES DE SUCCÈS
(Score sur 100 avec explication des facteurs)

### 8. PROCHAINES ÉTAPES IMMÉDIATES
(5 actions concrètes prioritaires à réaliser)

### 9. CONCLUSION ET RECOMMANDATIONS
(Synthèse finale et orientation vers un accompagnement personnalisé si nécessaire)

Sois exhaustif, précis et professionnel (1000-1500 mots).
Rappelle que ce rapport est un outil d'aide à la décision et ne constitue pas un avis juridique.
Mentionne que pour un accompagnement personnalisé, le client peut contacter Stratégie & Expertise Santé."""

@api_router.post("/dossier-express/submit")
async def dossier_express_submit(request: Request):
    """Submit a Dossier Express after payment - triggers AI analysis + PDF + email."""
    body = await request.json()
    session_id = body.get("session_id", "")
    email = body.get("email", "")
    name = body.get("name", "")
    situation = body.get("situation", "")
    type_dossier = body.get("type_dossier", "")
    regime = body.get("regime", "")
    documents_text = body.get("documents_text", "")

    if not email or not situation:
        raise HTTPException(status_code=400, detail="Email et description requis")

    # Create dossier record
    dossier_id = str(uuid.uuid4())
    dossier = {
        "id": dossier_id,
        "session_id": session_id,
        "email": email,
        "name": name,
        "situation": situation,
        "type_dossier": type_dossier,
        "regime": regime,
        "documents_text": documents_text[:10000],
        "status": "processing",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.dossier_express.insert_one(dossier)

    # Trigger async analysis
    asyncio.create_task(_process_dossier_express(dossier_id, email, name, situation, type_dossier, regime, documents_text))

    return {"success": True, "dossier_id": dossier_id, "message": "Votre dossier est en cours d'analyse. Vous recevrez le rapport par email sous 2 heures."}


async def _process_dossier_express(dossier_id: str, email: str, name: str, situation: str, type_dossier: str, regime: str, documents_text: str):
    """Background task: AI analysis → PDF generation → email delivery."""
    try:
        if not EMERGENT_LLM_KEY:
            logger.error("Dossier Express: EMERGENT_LLM_KEY not available")
            await db.dossier_express.update_one({"id": dossier_id}, {"$set": {"status": "error", "error": "Service IA non disponible"}})
            return

        # Fetch similar cases
        similar_cases = []
        if type_dossier:
            similar_cases = await db.cas_anonymises.find(
                {"type_dossier": type_dossier}, {"_id": 0}
            ).sort("score_pertinence", -1).to_list(5)

        case_context = ""
        if similar_cases:
            case_context = "\n\nCAS SIMILAIRES DANS LA BASE :\n"
            for c in similar_cases:
                case_context += f"- Type: {c.get('type_dossier')}, Régime: {c.get('regime')}, Stratégie: {c.get('strategie')}, Résultat: {c.get('resultat')}\n"

        user_msg = f"""DOSSIER EXPRESS - Analyse complète demandée

Client : {name}
Type de dossier : {type_dossier}
Régime : {regime}

DESCRIPTION DE LA SITUATION :
{situation}

CONTENU DES DOCUMENTS FOURNIS :
{documents_text[:8000] if documents_text else "(Aucun document textuel fourni)"}
{case_context}

{DOSSIER_EXPRESS_PROMPT}"""

        # Call Claude for analysis
        session_id_llm = f"dossier_{dossier_id[:8]}"
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=session_id_llm,
            system_message=STRATEGIIA_SYSTEM_PROMPT
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")

        analysis = await chat.send_message(UserMessage(text=user_msg))

        # Generate PDF
        pdf_bytes = _generate_dossier_pdf(name, email, type_dossier, regime, analysis)

        # Send email with PDF attachment
        email_sent = False
        if RESEND_AVAILABLE and resend.api_key:
            try:
                pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")
                resend.Emails.send({
                    "from": SENDER_EMAIL,
                    "to": [email],
                    "subject": "Votre Rapport Dossier Express - Stratégie & Expertise Santé",
                    "html": f"""
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                        <h1 style="color: #1a1a2e;">Votre Rapport Dossier Express</h1>
                        <p>Bonjour {name or 'Madame, Monsieur'},</p>
                        <p>Merci pour votre confiance. Veuillez trouver ci-joint votre rapport d'analyse complet réalisé par notre outil StratégiIA.</p>
                        <p>Ce rapport contient :</p>
                        <ul>
                            <li>L'analyse détaillée de votre situation</li>
                            <li>Le cadre juridique applicable</li>
                            <li>Vos droits identifiés</li>
                            <li>La stratégie recommandée</li>
                            <li>Les prochaines étapes à suivre</li>
                        </ul>
                        <p>Pour un accompagnement personnalisé, n'hésitez pas à nous contacter :</p>
                        <p><a href="https://expertise-health.preview.emergentagent.com/contact" style="color: #0f3460;">Prendre rendez-vous</a></p>
                        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                        <p style="font-size: 12px; color: #666;">Ce rapport est un outil d'aide à la décision et ne constitue pas un avis juridique.<br>Stratégie & Expertise Santé</p>
                    </div>
                    """,
                    "attachments": [{"filename": f"Rapport_Dossier_Express_{dossier_id[:8]}.pdf", "content": list(pdf_bytes)}]
                })
                email_sent = True
                logger.info(f"Dossier Express {dossier_id}: email sent to {email}")
            except Exception as e:
                logger.error(f"Dossier Express email error: {e}")

        # Update status
        await db.dossier_express.update_one(
            {"id": dossier_id},
            {"$set": {
                "status": "completed",
                "analysis": analysis[:5000],
                "email_sent": email_sent,
                "completed_at": datetime.now(timezone.utc).isoformat()
            }}
        )

    except Exception as e:
        logger.error(f"Dossier Express processing error: {e}")
        await db.dossier_express.update_one(
            {"id": dossier_id},
            {"$set": {"status": "error", "error": str(e)}}
        )


def _generate_dossier_pdf(name: str, email: str, type_dossier: str, regime: str, analysis: str) -> bytes:
    """Generate a professional PDF report from the AI analysis."""
    from fpdf import FPDF
    import textwrap

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=25)
    pdf.add_page()

    # Header
    pdf.set_fill_color(26, 26, 46)
    pdf.rect(0, 0, 210, 45, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_y(10)
    pdf.cell(0, 10, "Strategie & Expertise Sante", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, "Rapport Dossier Express", align="C", new_x="LMARGIN", new_y="NEXT")

    # Client info box
    pdf.set_y(55)
    pdf.set_text_color(50, 50, 50)
    pdf.set_fill_color(245, 245, 250)
    pdf.rect(15, 52, 180, 28, 'F')
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_x(20)
    pdf.cell(0, 7, f"Client : {name or 'Non renseigne'}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_x(20)
    pdf.cell(0, 6, f"Email : {email}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(20)
    pdf.cell(0, 6, f"Type : {type_dossier or 'Non precise'}  |  Regime : {regime or 'Non precise'}  |  Date : {datetime.now().strftime('%d/%m/%Y')}", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(8)

    # Parse and render analysis content
    lines = analysis.split('\n')
    for line in lines:
        stripped = line.strip()
        if not stripped:
            pdf.ln(3)
            continue

        if stripped.startswith('# '):
            pdf.set_font("Helvetica", "B", 16)
            pdf.set_text_color(26, 26, 46)
            pdf.ln(5)
            pdf.multi_cell(0, 8, stripped[2:].encode('latin-1', 'replace').decode('latin-1'))
        elif stripped.startswith('## '):
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(26, 26, 46)
            pdf.ln(4)
            pdf.multi_cell(0, 7, stripped[3:].encode('latin-1', 'replace').decode('latin-1'))
        elif stripped.startswith('### '):
            pdf.set_font("Helvetica", "B", 12)
            pdf.set_text_color(15, 52, 96)
            pdf.ln(3)
            pdf.multi_cell(0, 7, stripped[4:].encode('latin-1', 'replace').decode('latin-1'))
        elif stripped.startswith('- ') or stripped.startswith('* '):
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(50, 50, 50)
            text = stripped[2:].encode('latin-1', 'replace').decode('latin-1')
            pdf.set_x(20)
            pdf.multi_cell(170, 6, f"  {text}")
        elif stripped.startswith('**') and stripped.endswith('**'):
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(50, 50, 50)
            text = stripped.strip('*').encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 6, text)
        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(50, 50, 50)
            text = stripped.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 6, text)

    # Footer disclaimer
    pdf.ln(10)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(5)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(130, 130, 130)
    pdf.multi_cell(0, 5, "Ce rapport est un outil d'aide a la decision et ne constitue pas un avis juridique. Pour un accompagnement personnalise, contactez Strategie & Expertise Sante.")

    return pdf.output()


@api_router.post("/dossier-express/checkout")
async def dossier_express_checkout(request: Request):
    """Create Stripe checkout for Dossier Express (97 EUR)."""
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Stripe non configure")

    body = await request.json()
    origin_url = body.get("origin_url", "").rstrip('/')
    email = body.get("email", "")
    name = body.get("name", "")

    success_url = f"{origin_url}/dossier-express?payment=success&session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{origin_url}/dossier-express?payment=cancelled"

    host_url = str(request.base_url).rstrip('/')
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)

    checkout_request = CheckoutSessionRequest(
        amount=97.00,
        currency="eur",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "package_id": "dossier_express",
            "package_name": "Dossier Express StratégiIA",
            "customer_email": email,
            "customer_name": name
        }
    )

    try:
        session = await stripe_checkout.create_checkout_session(checkout_request)
        return {"success": True, "url": session.url, "session_id": session.session_id}
    except Exception as e:
        logger.error(f"Dossier Express checkout error: {e}")
        raise HTTPException(status_code=500, detail="Erreur de paiement")


@api_router.get("/dossier-express/status/{dossier_id}")
async def dossier_express_status(dossier_id: str):
    """Check the status of a Dossier Express analysis."""
    dossier = await db.dossier_express.find_one({"id": dossier_id}, {"_id": 0, "documents_text": 0})
    if not dossier:
        raise HTTPException(status_code=404, detail="Dossier non trouve")
    return dossier


@api_router.get("/admin/dossier-express")
async def admin_dossier_express(admin: dict = Depends(get_current_admin)):
    """Admin: list all Dossier Express submissions."""
    dossiers = await db.dossier_express.find({}, {"_id": 0, "documents_text": 0, "analysis": 0}).sort("created_at", -1).to_list(100)
    stats = {
        "total": len(dossiers),
        "completed": sum(1 for d in dossiers if d.get("status") == "completed"),
        "processing": sum(1 for d in dossiers if d.get("status") == "processing"),
        "errors": sum(1 for d in dossiers if d.get("status") == "error"),
    }
    return {"items": dossiers, "stats": stats}



@api_router.post("/strategiia/analyze")
async def strategiia_analyze(request: Request):
    body = await request.json()
    situation = body.get("situation", "")
    type_dossier = body.get("type_dossier", "")
    regime = body.get("regime", "")
    is_premium = body.get("premium", False)
    email = body.get("email", "").strip().lower()

    if not situation.strip():
        raise HTTPException(status_code=400, detail="Description de la situation requise")
    if not email:
        raise HTTPException(status_code=400, detail="Email obligatoire pour utiliser StratégiIA")

    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=503, detail="Service IA non disponible")

    # Check quota for free analyses (3/month per email) — premium analyses are unlimited
    if not is_premium:
        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
        usage_count = await db.strategiia_analyses.count_documents({
            "email": email, "is_premium": False,
            "created_at": {"$gte": month_start}
        })
        if usage_count >= 3:
            return {
                "success": False,
                "quota_exceeded": True,
                "remaining": 0,
                "message": "Vous avez utilisé vos 3 analyses gratuites ce mois-ci. Passez au Dossier Express pour une analyse complète."
            }

    # Fetch similar anonymized cases
    similar_cases = []
    if type_dossier:
        similar_cases = await db.cas_anonymises.find(
            {"type_dossier": type_dossier}, {"_id": 0}
        ).sort("score_pertinence", -1).to_list(5)

    case_context = ""
    if similar_cases:
        case_context = "\n\nCAS SIMILAIRES ANONYMISÉS DANS LA BASE :\n"
        for c in similar_cases:
            case_context += f"- Type: {c.get('type_dossier')}, Régime: {c.get('regime')}, Durée: {c.get('duree')}, Stratégie: {c.get('strategie')}, Résultat: {c.get('resultat')}, Score: {c.get('score_pertinence', 'N/A')}/100\n"

    analysis_prompt = STRATEGIIA_PREMIUM_PROMPT if is_premium else STRATEGIIA_BASIC_PROMPT

    user_msg = f"""Type de dossier : {type_dossier}
Régime : {regime}
Description de la situation : {situation}
{case_context}

{analysis_prompt}"""

    try:
        session_id = f"strategiia_{str(uuid.uuid4())[:8]}"
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=session_id,
            system_message=STRATEGIIA_SYSTEM_PROMPT
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")

        response = await chat.send_message(UserMessage(text=user_msg))

        # Save analysis
        analysis_doc = {
            "id": str(uuid.uuid4()),
            "type_dossier": type_dossier,
            "regime": regime,
            "situation": situation[:500],
            "is_premium": is_premium,
            "email": email,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.strategiia_analyses.insert_one(analysis_doc)

        # Compute remaining free analyses this month
        remaining = 3
        if not is_premium:
            now = datetime.now(timezone.utc)
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
            usage_count = await db.strategiia_analyses.count_documents({
                "email": email, "is_premium": False,
                "created_at": {"$gte": month_start}
            })
            remaining = max(0, 3 - usage_count)

        return {"success": True, "analysis": response, "cases_found": len(similar_cases), "remaining": remaining}

    except Exception as e:
        logger.error(f"StratégiIA error: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'analyse IA")

@api_router.get("/strategiia/quota/{email}")
async def strategiia_quota(email: str):
    """Check remaining free StratégiIA analyses for this month."""
    email = email.strip().lower()
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).isoformat()
    usage_count = await db.strategiia_analyses.count_documents({
        "email": email, "is_premium": False,
        "created_at": {"$gte": month_start}
    })
    remaining = max(0, 3 - usage_count)
    return {"remaining": remaining, "limit": 3, "used": min(usage_count, 3)}

@api_router.post("/strategiia/checkout")
async def strategiia_checkout(request: Request):
    """Create Stripe checkout for premium StratégiIA report (29€)"""
    if not STRIPE_API_KEY:
        raise HTTPException(status_code=500, detail="Stripe non configuré")

    body = await request.json()
    origin_url = body.get("origin_url", "").rstrip('/')
    email = body.get("email", "")
    analysis_context = body.get("context", "")

    success_url = f"{origin_url}/simulateur?strategiia=success&session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{origin_url}/simulateur?strategiia=cancelled"

    host_url = str(request.base_url).rstrip('/')
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)

    checkout_request = CheckoutSessionRequest(
        amount=29.00,
        currency="eur",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "product": "strategiia_premium",
            "customer_email": email,
            "context": analysis_context[:200]
        }
    )

    try:
        session = await stripe_checkout.create_checkout_session(checkout_request)
        return {"url": session.url, "session_id": session.session_id}
    except Exception as e:
        logger.error(f"StratégiIA checkout error: {e}")
        raise HTTPException(status_code=500, detail="Erreur de paiement")

# Admin: anonymized cases CRUD
@api_router.get("/admin/cas-anonymises")
async def get_cas_anonymises(admin: dict = Depends(get_current_admin)):
    cases = await db.cas_anonymises.find({}, {"_id": 0}).sort("created_at", -1).to_list(500)
    return {"items": cases, "total": len(cases)}

@api_router.post("/admin/cas-anonymises")
async def create_cas_anonymise(request: Request, admin: dict = Depends(get_current_admin)):
    body = await request.json()
    cas = {
        "id": str(uuid.uuid4()),
        "type_dossier": body.get("type_dossier", ""),
        "regime": body.get("regime", ""),
        "duree": body.get("duree", ""),
        "strategie": body.get("strategie", ""),
        "resultat": body.get("resultat", ""),
        "score_pertinence": body.get("score_pertinence", 0),
        "notes": body.get("notes", ""),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.cas_anonymises.insert_one(cas)
    return {"success": True, "id": cas["id"]}

@api_router.delete("/admin/cas-anonymises/{case_id}")
async def delete_cas_anonymise(case_id: str, admin: dict = Depends(get_current_admin)):
    await db.cas_anonymises.delete_one({"id": case_id})
    return {"success": True}

@api_router.get("/admin/strategiia/stats")
async def get_strategiia_stats(admin: dict = Depends(get_current_admin)):
    total_analyses = await db.strategiia_analyses.count_documents({})
    premium = await db.strategiia_analyses.count_documents({"is_premium": True})
    total_cases = await db.cas_anonymises.count_documents({})
    recent = await db.strategiia_analyses.find({}, {"_id": 0}).sort("created_at", -1).to_list(20)
    return {"total_analyses": total_analyses, "premium": premium, "total_cases": total_cases, "recent": recent}

# ==================== CALCULATOR COUNTER ROUTES ====================

@api_router.post("/calculator/track")
async def track_calculator_usage(request: Request):
    body = await request.json()
    calc_type = body.get("type", "unknown")
    await db.calculator_usage.insert_one({
        "type": calc_type,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    return {"success": True}

@api_router.get("/calculator/count")
async def get_calculator_weekly_count():
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    count = await db.calculator_usage.count_documents({"created_at": {"$gte": week_ago}})
    return {"count": count}

# ==================== URGENT ALERT ROUTES ====================

@api_router.post("/alerte-urgente")
async def create_urgent_alert(request: Request):
    body = await request.json()
    if not body.get("nom") or not body.get("telephone"):
        raise HTTPException(status_code=400, detail="Nom et téléphone requis")
    alert = {
        "id": str(uuid.uuid4()),
        "nom": body["nom"],
        "telephone": body["telephone"],
        "email": body.get("email", ""),
        "message": body.get("message", ""),
        "formule": body.get("formule", "2h"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "nouveau",
        "traite": False
    }
    await db.urgent_alerts.insert_one(alert)
    # Try to send notification email
    if RESEND_AVAILABLE and os.environ.get('RESEND_API_KEY') and NOTIFICATION_EMAIL:
        try:
            prix = "80€" if alert["formule"] == "30min" else "50€"
            await asyncio.to_thread(resend.Emails.send, {
                "from": SENDER_EMAIL,
                "to": [NOTIFICATION_EMAIL],
                "subject": f"ALERTE URGENTE - {alert['nom']} ({prix})",
                "html": f"""
                <h2 style="color:red;">Demande urgente !</h2>
                <p><strong>Formule:</strong> Réponse sous {alert['formule']} — {prix}</p>
                <p><strong>Nom:</strong> {alert['nom']}</p>
                <p><strong>Téléphone:</strong> {alert['telephone']}</p>
                <p><strong>Email:</strong> {alert.get('email', 'Non renseigné')}</p>
                <p><strong>Message:</strong> {alert.get('message', 'Aucun')}</p>
                """
            })
        except Exception as e:
            logger.error(f"Urgent alert email error: {e}")
    return {"success": True, "id": alert["id"]}

@api_router.get("/admin/alertes-urgentes")
async def get_urgent_alerts(admin: dict = Depends(get_current_admin)):
    alerts = await db.urgent_alerts.find({}, {"_id": 0}).sort("created_at", -1).to_list(200)
    return {"items": alerts, "total": len(alerts), "non_traite": sum(1 for a in alerts if not a.get("traite"))}

@api_router.put("/admin/alertes-urgentes/{alert_id}")
async def update_urgent_alert(alert_id: str, request: Request, admin: dict = Depends(get_current_admin)):
    body = await request.json()
    await db.urgent_alerts.update_one({"id": alert_id}, {"$set": {"traite": body.get("traite", True), "status": body.get("status", "traité")}})
    return {"success": True}

# ==================== ABANDONED CHECKOUT / RELANCE ROUTES ====================

@api_router.post("/relance/track")
async def track_abandoned_checkout(request: Request):
    body = await request.json()
    if not body.get("email"):
        raise HTTPException(status_code=400, detail="Email requis")
    
    pkg_id = body.get("package_id", "")
    pkg = PAYMENT_PACKAGES.get(pkg_id, {})
    
    abandoned = AbandonedCheckout(
        email=body["email"],
        name=body.get("name", ""),
        package_id=pkg_id,
        package_name=pkg.get("name", pkg_id),
        amount=pkg.get("amount", 0)
    )
    doc = abandoned.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.abandoned_checkouts.insert_one(doc)
    return {"success": True}

@api_router.get("/admin/relance")
async def get_abandoned_checkouts(admin: dict = Depends(get_current_admin)):
    abandoned = await db.abandoned_checkouts.find({}, {"_id": 0}).sort("created_at", -1).to_list(200)
    stats = {
        "total": len(abandoned),
        "not_sent": sum(1 for a in abandoned if not a.get("relance_sent")),
        "sent": sum(1 for a in abandoned if a.get("relance_sent"))
    }
    return {"items": abandoned, "stats": stats}

@api_router.post("/admin/relance/send/{item_id}")
async def send_relance_email(item_id: str, admin: dict = Depends(get_current_admin)):
    item = await db.abandoned_checkouts.find_one({"id": item_id}, {"_id": 0})
    if not item:
        raise HTTPException(status_code=404, detail="Élément non trouvé")
    
    # Try to send email via Resend if configured
    email_sent = False
    error_detail = ""
    if RESEND_AVAILABLE and resend.api_key and resend.api_key != '':
        try:
            resend.Emails.send({
                "from": SENDER_EMAIL,
                "to": item["email"],
                "subject": "Stratégie & Expertise Santé - Finalisez votre démarche",
                "html": f"""
                <h2>Bonjour {item.get('name', '')},</h2>
                <p>Vous aviez commencé à réserver notre prestation <strong>{item.get('package_name', '')}</strong>.</p>
                <p>N'hésitez pas à finaliser votre inscription ou à nous contacter si vous avez des questions.</p>
                <p>Premier échange gratuit et sans engagement.</p>
                <p>Cordialement,<br>Stratégie & Expertise Santé</p>
                """
            })
            email_sent = True
        except Exception as e:
            logger.error(f"Resend error: {e}")
            error_detail = str(e)
    
    await db.abandoned_checkouts.update_one(
        {"id": item_id},
        {"$set": {"relance_sent": True, "relance_sent_at": datetime.now(timezone.utc).isoformat()}}
    )
    
    if email_sent:
        msg = "Email de relance envoyé avec succès"
    elif error_detail:
        msg = f"Relance marquée mais email échoué : {error_detail}"
    else:
        msg = "Relance marquée (email non configuré)"
    
    return {"success": True, "email_sent": email_sent, "message": msg}

# ==================== RESOURCES / LIBRARY ROUTES ====================

@api_router.post("/resources/download")
async def track_resource_download(request: Request):
    body = await request.json()
    await db.resource_downloads.insert_one({
        "resource_id": body.get("resource_id", ""),
        "resource_title": body.get("resource_title", ""),
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    return {"success": True}

@api_router.get("/admin/resources/stats")
async def get_resource_stats(admin: dict = Depends(get_current_admin)):
    pipeline = [
        {"$group": {"_id": "$resource_id", "title": {"$first": "$resource_title"}, "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    stats = await db.resource_downloads.aggregate(pipeline).to_list(100)
    total = await db.resource_downloads.count_documents({})
    return {"total_downloads": total, "by_resource": stats}

@api_router.get("/admin/email/status")
async def get_email_status(admin: dict = Depends(get_current_admin)):
    """Diagnostic endpoint to check Resend email configuration status."""
    key = os.environ.get('RESEND_API_KEY', '')
    has_key = bool(key and key.strip())
    return {
        "resend_installed": RESEND_AVAILABLE,
        "api_key_configured": has_key,
        "api_key_preview": f"{key[:8]}...{key[-4:]}" if has_key and len(key) > 12 else ("set" if has_key else "missing"),
        "sender_email": SENDER_EMAIL,
        "notification_email": NOTIFICATION_EMAIL or "(non configuré)",
    }

@api_router.post("/admin/email/test")
async def test_email(request: Request, admin: dict = Depends(get_current_admin)):
    """Send a test email to verify Resend configuration."""
    body = await request.json()
    to_email = body.get("email", "")
    if not to_email:
        raise HTTPException(status_code=400, detail="Email destinataire requis")
    if not RESEND_AVAILABLE or not resend.api_key:
        return {"success": False, "message": "Resend non configuré"}
    try:
        result = await asyncio.to_thread(resend.Emails.send, {
            "from": SENDER_EMAIL,
            "to": [to_email],
            "subject": "Stratégie & Expertise Santé - Test email",
            "html": "<h2>Test réussi !</h2><p>Votre configuration email Resend fonctionne correctement.</p>"
        })
        return {"success": True, "message": "Email de test envoyé", "resend_id": str(result)}
    except Exception as e:
        return {"success": False, "message": f"Erreur Resend : {str(e)}"}


# ==================== SEED DATA ====================

@api_router.post("/seed")
async def seed_data():
    """Seed initial data - FAQ items and default admin"""
    
    # Check if admin exists
    existing_admin = await db.admins.find_one({"email": "admin@accompagn-sante.fr"})
    if not existing_admin:
        admin = AdminUser(
            email="admin@accompagn-sante.fr",
            password_hash=hash_password("Admin2024!"),
            nom="Administrateur"
        )
        doc = admin.model_dump()
        doc['created_at'] = doc['created_at'].isoformat()
        await db.admins.insert_one(doc)
        logger.info("Default admin created")
    
    # Seed FAQ if empty
    faq_count = await db.faq.count_documents({})
    if faq_count == 0:
        faqs = [
            FAQItem(question="Qu'est-ce qu'une maladie professionnelle ?", 
                    reponse="Une maladie professionnelle est une affection contractée en raison de l'exposition à un risque lors de l'exercice de votre activité professionnelle.", 
                    categorie="AT/MP", ordre=1),
            FAQItem(question="Comment faire reconnaître une maladie professionnelle ?", 
                    reponse="Vous devez déclarer votre maladie à la CPAM dans les 15 jours suivant la date de cessation de travail.", 
                    categorie="AT/MP", ordre=2),
            FAQItem(question="Qu'est-ce que l'IPP ?", 
                    reponse="L'Incapacité Permanente Partielle (IPP) est un taux qui évalue vos séquelles définitives.", 
                    categorie="AT/MP", ordre=3),
            FAQItem(question="Comment se préparer à une expertise médicale ?", 
                    reponse="Préparez un dossier complet avec tous vos documents médicaux, listez vos symptômes au quotidien.", 
                    categorie="Expertises", ordre=1),
            FAQItem(question="Qu'est-ce que la PTIA ?", 
                    reponse="La Perte Totale et Irréversible d'Autonomie est une garantie d'assurance couvrant l'impossibilité définitive d'exercer toute activité.", 
                    categorie="Assurances", ordre=1),
            FAQItem(question="Comment demander la RQTH ?", 
                    reponse="La RQTH se demande auprès de la MDPH de votre département.", 
                    categorie="MDPH", ordre=1),
        ]
        
        for faq in faqs:
            await db.faq.insert_one(faq.model_dump())
        logger.info(f"Seeded {len(faqs)} FAQ items")
    
    return {"success": True, "message": "Données initiales créées"}


# ==================== SEO ENDPOINTS ====================

SITE_URL = "https://expertise-health.preview.emergentagent.com"

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

@api_router.get("/sitemap.xml")
async def sitemap_xml():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    urls = ""
    for path, priority, freq in SITEMAP_PAGES:
        urls += f"""  <url>
    <loc>{SITE_URL}{path}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{priority}</priority>
  </url>\n"""
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}</urlset>"""
    return Response(content=xml, media_type="application/xml")


@api_router.get("/robots.txt")
async def robots_txt():
    content = f"""User-agent: *
Allow: /
Disallow: /admin
Disallow: /admin/login
Disallow: /espace-client

Sitemap: {SITE_URL}/api/sitemap.xml
"""
    return PlainTextResponse(content=content)


# Include the router in the main app
app.include_router(api_router)

# GZip compression for all responses
app.add_middleware(GZipMiddleware, minimum_size=500)

# Cache-Control middleware for static-like API responses
@app.middleware("http")
async def add_cache_headers(request: Request, call_next):
    response = await call_next(request)
    path = request.url.path
    # Cache static SEO files aggressively
    if path in ("/api/sitemap.xml", "/api/robots.txt"):
        response.headers["Cache-Control"] = "public, max-age=86400"
    # Cache GET API responses briefly
    elif request.method == "GET" and path.startswith("/api/") and "admin" not in path:
        response.headers["Cache-Control"] = "public, max-age=60, stale-while-revalidate=120"
    return response

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Background task for automatic abandoned cart reminders
async def auto_relance_task():
    """Periodically sends reminder emails for abandoned checkouts (every 30 min)."""
    while True:
        await asyncio.sleep(1800)
        if not RESEND_AVAILABLE or not os.environ.get('RESEND_API_KEY'):
            continue
        try:
            cutoff = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
            unsent = await db.abandoned_checkouts.find(
                {"relance_sent": False, "created_at": {"$lte": cutoff}},
                {"_id": 0}
            ).to_list(50)
            for item in unsent:
                try:
                    resend.Emails.send({
                        "from": SENDER_EMAIL,
                        "to": item["email"],
                        "subject": "Stratégie & Expertise Santé - Finalisez votre démarche",
                        "html": f"""
                        <h2>Bonjour {item.get('name', '')},</h2>
                        <p>Vous aviez commencé à réserver notre prestation <strong>{item.get('package_name', '')}</strong>.</p>
                        <p>N'hésitez pas à finaliser votre inscription ou à nous contacter si vous avez des questions.</p>
                        <p>Premier échange gratuit et sans engagement.</p>
                        <p>Cordialement,<br>Stratégie & Expertise Santé</p>
                        """
                    })
                    await db.abandoned_checkouts.update_one(
                        {"id": item["id"]},
                        {"$set": {"relance_sent": True, "relance_sent_at": datetime.now(timezone.utc).isoformat()}}
                    )
                    logger.info(f"Auto-relance sent to {item['email']}")
                except Exception as e:
                    logger.error(f"Auto-relance error for {item.get('email')}: {e}")
        except Exception as e:
            logger.error(f"Auto-relance task error: {e}")

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(auto_relance_task())
    logger.info("Auto-relance background task started")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
