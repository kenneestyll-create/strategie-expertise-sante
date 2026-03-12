from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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

try:
    import resend
    RESEND_AVAILABLE = True
except ImportError:
    RESEND_AVAILABLE = False

# Import Emergent LLM
from emergentintegrations.llm.chat import LlmChat, UserMessage

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

# Security
security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)

# Create the main app
app = FastAPI(title="Accompagn'Santé API")

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
            system_message="""Tu es l'assistant virtuel d'Accompagn'Santé, un service français d'accompagnement pour les personnes confrontées à des maladies professionnelles, accidents du travail, expertises médicales et litiges avec les assurances.

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
    return {"message": "Bienvenue sur l'API Accompagn'Santé"}

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

# ==================== CHATBOT ROUTES ====================

@api_router.post("/chatbot", response_model=ChatResponse)
async def chatbot_message(chat_input: ChatMessage):
    """Handle chatbot messages - first check FAQ, then use AI"""
    session_id = chat_input.session_id or str(uuid.uuid4())
    
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

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
