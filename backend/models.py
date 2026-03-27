from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone


# ==================== CONTACT MODELS ====================

class ContactRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nom: str
    prenom: str
    email: str
    telephone: Optional[str] = None
    sujet: str
    message: str
    type_accompagnement: Optional[str] = None
    tracking_via: Optional[str] = None
    tracking_source: Optional[str] = None
    tracking_campaign: Optional[str] = None
    status: str = "nouveau"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ContactRequestCreate(BaseModel):
    nom: str
    prenom: str
    email: str
    telephone: Optional[str] = None
    sujet: str
    message: str
    type_accompagnement: Optional[str] = None
    tracking_via: Optional[str] = None
    tracking_source: Optional[str] = None
    tracking_campaign: Optional[str] = None

class ContactRequestUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None


# ==================== FAQ / AVIS MODELS ====================

class FAQItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    question: str
    reponse: str
    categorie: str = "Général"
    ordre: int = 0

class FAQItemCreate(BaseModel):
    question: str
    reponse: str
    categorie: str = "Général"
    ordre: int = 0

class AdminUser(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    password_hash: str
    nom: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AdminLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin_name: str = ""

class Avis(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    nom: str
    note: int = Field(ge=1, le=5)
    commentaire: str
    type_accompagnement: Optional[str] = None
    status: str = "en_attente"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AvisCreate(BaseModel):
    nom: str
    note: int = Field(ge=1, le=5)
    commentaire: str
    type_accompagnement: Optional[str] = None

class AvisUpdate(BaseModel):
    status: Optional[str] = None


# ==================== FORUM MODELS ====================

class ForumUser(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: Optional[str] = None
    password_hash: Optional[str] = None
    pseudo: str
    is_anonymous: bool = False
    avatar_color: str = "#4A90D9"
    is_banned: bool = False
    ban_reason: Optional[str] = None
    posts_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ForumUserRegister(BaseModel):
    pseudo: str
    email: Optional[str] = None
    password: Optional[str] = None
    is_anonymous: bool = False

class ForumUserLogin(BaseModel):
    email: str
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
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category_id: str
    title: str
    content: str
    author_id: str
    author_pseudo: str
    is_anonymous: bool = False
    is_pinned: bool = False
    is_locked: bool = False
    views: int = 0
    likes: List[str] = Field(default_factory=list)
    replies_count: int = 0
    status: str = "published"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ForumTopicCreate(BaseModel):
    category_id: str
    title: str
    content: str

class ForumReply(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    topic_id: str
    content: str
    author_id: str
    author_pseudo: str
    is_anonymous: bool = False
    likes: List[str] = Field(default_factory=list)
    status: str = "published"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ForumReplyCreate(BaseModel):
    content: str

class ForumReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    reporter_id: str
    target_type: str
    target_id: str
    reason: str
    status: str = "pending"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

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
    is_faq: bool = False
    session_id: str = ""


# ==================== PAYMENT MODELS ====================

class PaymentTransaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    package_id: str
    package_name: str
    amount: float
    currency: str = "eur"
    email: Optional[str] = None
    customer_name: Optional[str] = None
    status: str = "pending"
    payment_status: str = "initiated"
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CreateCheckoutRequest(BaseModel):
    package_id: str
    customer_email: Optional[str] = None
    customer_name: Optional[str] = None
    referral_code: Optional[str] = None
    origin_url: str


# ==================== VISITOR & REFERRAL MODELS ====================

class VisitorCount(BaseModel):
    id: str = "visitor_counter"
    count: int = 0
    last_updated: Optional[str] = None

class ReferralCode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    code: str
    owner_email: str
    owner_name: Optional[str] = None
    uses_count: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ReferralUse(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    referral_code: str
    referred_email: str
    referred_name: Optional[str] = None
    discount_applied: float = 10.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CreateReferralRequest(BaseModel):
    email: str
    name: Optional[str] = None

class ClientHistory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    orders_count: int = 0
    last_order_at: Optional[str] = None
    name: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==================== BOOKING MODELS ====================

class Booking(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date: str
    time_slot: str
    name: str
    email: str
    phone: Optional[str] = None
    type_accompagnement: Optional[str] = None
    message: Optional[str] = None
    status: str = "confirme"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BookingCreate(BaseModel):
    date: str
    time_slot: str
    name: str
    email: str
    phone: Optional[str] = None
    type_accompagnement: Optional[str] = None
    message: Optional[str] = None


# ==================== CLIENT PORTAL MODELS ====================

class ClientUser(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    password_hash: str
    name: str
    phone: Optional[str] = None
    notifications_email: bool = True
    notifications_push: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ClientRegister(BaseModel):
    email: str
    password: str
    name: str
    phone: Optional[str] = None
    notifications_email: bool = True
    notifications_push: bool = True

class ClientLogin(BaseModel):
    email: str
    password: str

class ClientCase(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str
    title: str
    description: str = ""
    status: str = "en_cours"
    notes: str = ""
    updates: list = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==================== SIMULATOR MODEL ====================

class SimulatorResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    answers: dict = Field(default_factory=dict)
    profile: str = ""
    recommendations: List[str] = Field(default_factory=list)
    email: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ==================== ABANDONED CHECKOUT MODEL ====================

class AbandonedCheckout(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: Optional[str] = None
    package_id: str = ""
    package_name: str = ""
    amount: float = 0
    relance_sent: bool = False
    relance_sent_at: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
