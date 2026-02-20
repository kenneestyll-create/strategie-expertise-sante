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

# Security
security = HTTPBearer()

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

# ==================== MODELS ====================

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

# ==================== AUTH HELPERS ====================

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def create_token(admin_id: str, admin_email: str) -> str:
    payload = {
        "sub": admin_id,
        "email": admin_email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        admin_id = payload.get("sub")
        if admin_id is None:
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
        <p style="color: #787570; font-size: 12px;">
            Reçu le {contact.created_at.strftime('%d/%m/%Y à %H:%M')}
        </p>
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
    
    # Send notification email (non-blocking)
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
    # Decode URL-encoded category (e.g., "AT%2FMP" -> "AT/MP")
    from urllib.parse import unquote
    decoded_categorie = unquote(categorie)
    faqs = await db.faq.find({"categorie": decoded_categorie}, {"_id": 0}).sort("ordre", 1).to_list(100)
    return faqs

# ==================== AUTH ROUTES ====================

@api_router.post("/auth/login", response_model=TokenResponse)
async def admin_login(credentials: AdminLogin):
    admin = await db.admins.find_one({"email": credentials.email}, {"_id": 0})
    
    if not admin:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    if not verify_password(credentials.password, admin['password_hash']):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    token = create_token(admin['id'], admin['email'])
    
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
            # AT/MP
            FAQItem(question="Qu'est-ce qu'une maladie professionnelle ?", 
                    reponse="Une maladie professionnelle est une affection contractée en raison de l'exposition à un risque lors de l'exercice de votre activité professionnelle. Elle doit figurer dans un tableau des maladies professionnelles ou être reconnue par le CRRMP.", 
                    categorie="AT/MP", ordre=1),
            FAQItem(question="Comment faire reconnaître une maladie professionnelle ?", 
                    reponse="Vous devez déclarer votre maladie à la CPAM dans les 15 jours suivant la date de cessation de travail. Un formulaire spécifique (cerfa) accompagné d'un certificat médical initial est nécessaire. La caisse dispose ensuite de 3 mois pour statuer.", 
                    categorie="AT/MP", ordre=2),
            FAQItem(question="Qu'est-ce que l'IPP ?", 
                    reponse="L'Incapacité Permanente Partielle (IPP) est un taux qui évalue vos séquelles définitives suite à un accident du travail ou une maladie professionnelle. Ce taux détermine le montant de votre indemnisation.", 
                    categorie="AT/MP", ordre=3),
            FAQItem(question="Qu'est-ce que le CRRMP ?", 
                    reponse="Le Comité Régional de Reconnaissance des Maladies Professionnelles intervient quand votre maladie ne figure pas dans un tableau, ou que les conditions du tableau ne sont pas remplies. Il établit un lien direct entre votre travail et votre maladie.", 
                    categorie="AT/MP", ordre=4),
            # Expertises
            FAQItem(question="Comment se préparer à une expertise médicale ?", 
                    reponse="Préparez un dossier complet avec tous vos documents médicaux, listez vos symptômes au quotidien, et n'hésitez pas à vous faire accompagner. L'expertise dure généralement 30 à 60 minutes. Soyez honnête et précis dans vos réponses.", 
                    categorie="Expertises", ordre=1),
            FAQItem(question="Puis-je contester une expertise médicale ?", 
                    reponse="Oui, vous pouvez demander une contre-expertise. Il est conseillé de consulter votre propre médecin expert pour obtenir un avis différent. Vous disposez de délais légaux pour contester.", 
                    categorie="Expertises", ordre=2),
            FAQItem(question="L'expert médical est-il impartial ?", 
                    reponse="L'expert est tenu à l'impartialité, mais il est désigné et rémunéré par l'assurance. C'est pourquoi il est important de bien préparer votre dossier et de connaître vos droits.", 
                    categorie="Expertises", ordre=3),
            # Assurances
            FAQItem(question="Qu'est-ce que la PTIA ?", 
                    reponse="La Perte Totale et Irréversible d'Autonomie (PTIA) est une garantie d'assurance qui couvre l'impossibilité définitive d'exercer toute activité professionnelle et la nécessité d'une assistance pour les actes de la vie quotidienne.", 
                    categorie="Assurances", ordre=1),
            FAQItem(question="Mon assurance refuse de m'indemniser, que faire ?", 
                    reponse="Commencez par demander les motifs précis du refus par écrit. Vérifiez votre contrat et les conditions générales. Vous pouvez saisir le médiateur de l'assurance ou engager une procédure de contestation.", 
                    categorie="Assurances", ordre=2),
            FAQItem(question="Comment fonctionne une assurance prévoyance ?", 
                    reponse="L'assurance prévoyance vous couvre contre les risques liés à la personne : incapacité de travail, invalidité, décès. Elle verse des indemnités ou une rente selon votre contrat et le niveau de votre incapacité.", 
                    categorie="Assurances", ordre=3),
            # MDPH
            FAQItem(question="Comment demander la RQTH ?", 
                    reponse="La Reconnaissance de la Qualité de Travailleur Handicapé (RQTH) se demande auprès de la MDPH de votre département. Un formulaire unique accompagné d'un certificat médical est nécessaire. Le délai moyen de traitement est de 4 à 6 mois.", 
                    categorie="MDPH", ordre=1),
            FAQItem(question="Qu'est-ce que l'AAH ?", 
                    reponse="L'Allocation aux Adultes Handicapés (AAH) est une aide financière pour les personnes handicapées ayant un taux d'incapacité d'au moins 80%, ou entre 50% et 79% avec une restriction substantielle d'accès à l'emploi.", 
                    categorie="MDPH", ordre=2),
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
