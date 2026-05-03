from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Optional
from datetime import datetime, timezone
import uuid
import re

from config import db, limiter
from models import (
    ForumUser, ForumUserRegister, ForumUserLogin, ForumTokenResponse,
    ForumCategory, ForumTopic, ForumTopicCreate,
    ForumReply, ForumReplyCreate,
    ForumReport, ForumReportCreate
)
from utils.auth import (
    hash_password, verify_password, create_forum_token,
    get_current_forum_user, get_current_admin
)

router = APIRouter()

FORUM_CATEGORIES = [
    ForumCategory(id="accident-travail", name="Accident du travail", slug="accident-travail",
                  description="Échangez sur les accidents du travail, déclarations, indemnisations", icon="AlertTriangle", order=1),
    ForumCategory(id="maladie-professionnelle", name="Maladie professionnelle", slug="maladie-professionnelle",
                  description="Partagez vos expériences sur les maladies professionnelles et leur reconnaissance", icon="Stethoscope", order=2),
    ForumCategory(id="expertise-medicale", name="Expertise médicale", slug="expertise-medicale",
                  description="Conseils et retours d'expérience sur les expertises médicales", icon="FileSearch", order=3),
    ForumCategory(id="invalidite", name="Invalidité", slug="invalidite",
                  description="Discussions sur l'invalidité, les rentes et les démarches associées", icon="Heart", order=4),
    ForumCategory(id="mdph", name="Démarches MDPH", slug="mdph",
                  description="Aide et conseils sur les dossiers MDPH, RQTH, AAH", icon="Building", order=5),
    ForumCategory(id="protection-juridique", name="Protection juridique", slug="protection-juridique",
                  description="Questions sur la protection juridique et les litiges", icon="Shield", order=6),
]


# ==================== PUBLIC FORUM ====================

@router.get("/forum/categories")
async def get_forum_categories():
    return [cat.model_dump() for cat in FORUM_CATEGORIES]

@router.post("/forum/register", response_model=ForumTokenResponse)
@limiter.limit("5/minute")
async def register_forum_user(request: Request, input_data: ForumUserRegister):
    existing_pseudo = await db.forum_users.find_one({"pseudo": input_data.pseudo})
    if existing_pseudo:
        raise HTTPException(status_code=400, detail="Ce pseudonyme est déjà utilisé")

    if input_data.is_anonymous:
        user = ForumUser(pseudo=input_data.pseudo, is_anonymous=True, avatar_color=f"#{uuid.uuid4().hex[:6]}")
    else:
        if not input_data.email or not input_data.password:
            raise HTTPException(status_code=400, detail="Email et mot de passe requis pour l'inscription classique")
        existing_email = await db.forum_users.find_one({"email": input_data.email})
        if existing_email:
            raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")
        user = ForumUser(
            email=input_data.email, password_hash=hash_password(input_data.password),
            pseudo=input_data.pseudo, is_anonymous=False, avatar_color=f"#{uuid.uuid4().hex[:6]}"
        )

    doc = user.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.forum_users.insert_one(doc)
    token = create_forum_token(user.id, user.pseudo, user.is_anonymous)
    return ForumTokenResponse(access_token=token, user_id=user.id, pseudo=user.pseudo, is_anonymous=user.is_anonymous)

@router.post("/forum/login", response_model=ForumTokenResponse)
@limiter.limit("5/minute")
async def login_forum_user(request: Request, credentials: ForumUserLogin):
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
    return ForumTokenResponse(access_token=token, user_id=user['id'], pseudo=user['pseudo'], is_anonymous=False)

@router.get("/forum/topics")
async def get_forum_topics(category_id: Optional[str] = None, page: int = 1, limit: int = 20):
    query = {"status": "published"}
    if category_id:
        query["category_id"] = category_id
    skip = (page - 1) * limit
    topics = await db.forum_topics.find(query, {"_id": 0}).sort([("is_pinned", -1), ("created_at", -1)]).skip(skip).limit(limit).to_list(limit)
    total = await db.forum_topics.count_documents(query)
    for topic in topics:
        if isinstance(topic.get('created_at'), str):
            topic['created_at'] = datetime.fromisoformat(topic['created_at'])
    return {"topics": topics, "total": total, "page": page, "pages": (total + limit - 1) // limit}

@router.get("/forum/topics/{topic_id}")
async def get_forum_topic(topic_id: str):
    topic = await db.forum_topics.find_one({"id": topic_id, "status": "published"}, {"_id": 0})
    if not topic:
        raise HTTPException(status_code=404, detail="Sujet non trouvé")
    await db.forum_topics.update_one({"id": topic_id}, {"$inc": {"views": 1}})
    replies = await db.forum_replies.find({"topic_id": topic_id, "status": "published"}, {"_id": 0}).sort("created_at", 1).to_list(1000)
    for reply in replies:
        if isinstance(reply.get('created_at'), str):
            reply['created_at'] = datetime.fromisoformat(reply['created_at'])
    if isinstance(topic.get('created_at'), str):
        topic['created_at'] = datetime.fromisoformat(topic['created_at'])
    return {"topic": topic, "replies": replies}

@router.post("/forum/topics")
async def create_forum_topic(input_data: ForumTopicCreate, user: dict = Depends(get_current_forum_user)):
    valid_categories = [cat.id for cat in FORUM_CATEGORIES]
    if input_data.category_id not in valid_categories:
        raise HTTPException(status_code=400, detail="Catégorie invalide")
    topic = ForumTopic(
        category_id=input_data.category_id, title=input_data.title, content=input_data.content,
        author_id=user["sub"], author_pseudo=user["pseudo"], is_anonymous=user.get("is_anonymous", False)
    )
    doc = topic.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    await db.forum_topics.insert_one(doc)
    return {"success": True, "topic_id": topic.id}

@router.post("/forum/topics/{topic_id}/replies")
async def create_forum_reply(topic_id: str, input_data: ForumReplyCreate, user: dict = Depends(get_current_forum_user)):
    topic = await db.forum_topics.find_one({"id": topic_id, "status": "published"}, {"_id": 0})
    if not topic:
        raise HTTPException(status_code=404, detail="Sujet non trouvé")
    if topic.get('is_locked'):
        raise HTTPException(status_code=403, detail="Ce sujet est verrouillé")
    reply = ForumReply(
        topic_id=topic_id, content=input_data.content,
        author_id=user["sub"], author_pseudo=user["pseudo"], is_anonymous=user.get("is_anonymous", False)
    )
    doc = reply.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.forum_replies.insert_one(doc)
    await db.forum_topics.update_one({"id": topic_id}, {"$inc": {"replies_count": 1}, "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}})
    return {"success": True, "reply_id": reply.id}

@router.post("/forum/topics/{topic_id}/like")
async def like_topic(topic_id: str, user: dict = Depends(get_current_forum_user)):
    topic = await db.forum_topics.find_one({"id": topic_id}, {"_id": 0})
    if not topic:
        raise HTTPException(status_code=404, detail="Sujet non trouvé")
    user_id = user["sub"]
    likes = topic.get('likes', [])
    if user_id in likes:
        await db.forum_topics.update_one({"id": topic_id}, {"$pull": {"likes": user_id}})
        return {"liked": False, "likes_count": len(likes) - 1}
    else:
        await db.forum_topics.update_one({"id": topic_id}, {"$push": {"likes": user_id}})
        return {"liked": True, "likes_count": len(likes) + 1}

@router.post("/forum/replies/{reply_id}/like")
async def like_reply(reply_id: str, user: dict = Depends(get_current_forum_user)):
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

@router.post("/forum/report")
async def report_content(input_data: ForumReportCreate, user: dict = Depends(get_current_forum_user)):
    report = ForumReport(reporter_id=user["sub"], target_type=input_data.target_type, target_id=input_data.target_id, reason=input_data.reason)
    doc = report.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.forum_reports.insert_one(doc)
    return {"success": True, "message": "Signalement envoyé. Merci de votre vigilance."}


# ==================== FORUM ADMIN ====================

@router.get("/admin/forum/stats")
async def get_forum_stats(admin: dict = Depends(get_current_admin)):
    total_users = await db.forum_users.count_documents({})
    total_topics = await db.forum_topics.count_documents({})
    total_replies = await db.forum_replies.count_documents({})
    pending_reports = await db.forum_reports.count_documents({"status": "pending"})
    banned_users = await db.forum_users.count_documents({"is_banned": True})
    return {"total_users": total_users, "total_topics": total_topics, "total_replies": total_replies, "pending_reports": pending_reports, "banned_users": banned_users}

@router.get("/admin/forum/reports")
async def get_forum_reports(status: Optional[str] = None, admin: dict = Depends(get_current_admin)):
    query = {}
    if status:
        query["status"] = status
    reports = await db.forum_reports.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    for report in reports:
        if isinstance(report.get('created_at'), str):
            report['created_at'] = datetime.fromisoformat(report['created_at'])
    return reports

@router.patch("/admin/forum/reports/{report_id}")
async def update_report_status(report_id: str, status: str, admin: dict = Depends(get_current_admin)):
    if status not in ["reviewed", "dismissed"]:
        raise HTTPException(status_code=400, detail="Statut invalide")
    result = await db.forum_reports.update_one({"id": report_id}, {"$set": {"status": status}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Signalement non trouvé")
    return {"success": True}

@router.delete("/admin/forum/topics/{topic_id}")
async def admin_delete_topic(topic_id: str, admin: dict = Depends(get_current_admin)):
    result = await db.forum_topics.update_one({"id": topic_id}, {"$set": {"status": "deleted"}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Sujet non trouvé")
    return {"success": True, "message": "Sujet supprimé"}

@router.delete("/admin/forum/replies/{reply_id}")
async def admin_delete_reply(reply_id: str, admin: dict = Depends(get_current_admin)):
    result = await db.forum_replies.update_one({"id": reply_id}, {"$set": {"status": "deleted"}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Réponse non trouvée")
    return {"success": True, "message": "Réponse supprimée"}

@router.post("/admin/forum/users/{user_id}/ban")
async def ban_forum_user(user_id: str, reason: str = "Violation des règles du forum", admin: dict = Depends(get_current_admin)):
    result = await db.forum_users.update_one({"id": user_id}, {"$set": {"is_banned": True, "ban_reason": reason}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return {"success": True, "message": "Utilisateur banni"}

@router.post("/admin/forum/users/{user_id}/unban")
async def unban_forum_user(user_id: str, admin: dict = Depends(get_current_admin)):
    result = await db.forum_users.update_one({"id": user_id}, {"$set": {"is_banned": False, "ban_reason": None}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return {"success": True, "message": "Utilisateur débanni"}

@router.get("/admin/forum/users")
async def get_forum_users(admin: dict = Depends(get_current_admin)):
    users = await db.forum_users.find({}, {"_id": 0, "password_hash": 0}).sort("created_at", -1).to_list(1000)
    for user in users:
        if isinstance(user.get('created_at'), str):
            user['created_at'] = datetime.fromisoformat(user['created_at'])
    return users


# ==================== ADMIN SEED TOPICS (amorçage communautaire) ====================
# L'administrateur peut publier des "sujets graines" au nom de l'équipe afin
# d'amorcer la communauté avec du contenu éditorial validé (conforme RGPD,
# aucun faux témoignage). Ces sujets sont authentifiés comme étant publiés
# par "Équipe S.E.S", épinglés par défaut, et marqués is_seed=True pour
# traçabilité.

SEED_AUTHOR_ID = "admin-seed-ses"
SEED_DEFAULT_PSEUDO = "Équipe S.E.S"


@router.post("/admin/forum/seed-topic")
async def admin_seed_topic(
    input_data: ForumTopicCreate,
    pseudo: Optional[str] = None,
    is_pinned: bool = True,
    admin: dict = Depends(get_current_admin),
):
    """Crée un sujet éditorial publié au nom de l'Équipe S.E.S (sans passer
    par l'inscription publique). is_pinned=True par défaut pour le mettre en avant."""
    valid_categories = [cat.id for cat in FORUM_CATEGORIES]
    if input_data.category_id not in valid_categories:
        raise HTTPException(status_code=400, detail="Catégorie invalide")

    author_pseudo = (pseudo or SEED_DEFAULT_PSEUDO).strip() or SEED_DEFAULT_PSEUDO

    topic = ForumTopic(
        category_id=input_data.category_id,
        title=input_data.title,
        content=input_data.content,
        author_id=SEED_AUTHOR_ID,
        author_pseudo=author_pseudo,
        is_anonymous=False,
        is_pinned=is_pinned,
    )
    doc = topic.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    doc['is_seed'] = True  # flag éditorial
    doc['seeded_by'] = admin.get("sub") or admin.get("email")
    await db.forum_topics.insert_one(doc)
    return {"success": True, "topic_id": topic.id, "is_pinned": is_pinned}


@router.get("/admin/forum/seed-topics")
async def admin_list_seed_topics(admin: dict = Depends(get_current_admin)):
    """Liste les sujets éditoriaux publiés par l'Équipe S.E.S."""
    topics = await db.forum_topics.find(
        {"author_id": SEED_AUTHOR_ID},
        {"_id": 0}
    ).sort([("is_pinned", -1), ("created_at", -1)]).to_list(200)
    for t in topics:
        if isinstance(t.get('created_at'), str):
            t['created_at'] = datetime.fromisoformat(t['created_at'])
        if isinstance(t.get('updated_at'), str):
            t['updated_at'] = datetime.fromisoformat(t['updated_at'])
    return topics


@router.patch("/admin/forum/topics/{topic_id}/pin")
async def admin_pin_topic(topic_id: str, is_pinned: bool = True, admin: dict = Depends(get_current_admin)):
    """Épingle ou désépingle un sujet du forum."""
    result = await db.forum_topics.update_one(
        {"id": topic_id},
        {"$set": {"is_pinned": is_pinned, "updated_at": datetime.now(timezone.utc).isoformat()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Sujet non trouvé")
    return {"success": True, "is_pinned": is_pinned}


# ==================== ADMIN CLEANUP PYTEST DATA (production-safe) ====================
# Endpoints pour identifier et supprimer chirurgicalement les données pytest qui
# ont pu polluer la DB de production. Règle d'or : on ne touche JAMAIS aux posts
# réels — uniquement ceux qui correspondent aux patterns pytest connus.

_PYTEST_PSEUDO_REGEX = r'^(pytest-|TestUser\d+|AnonUser\d+|anon-|integ-)'
_PYTEST_EMAIL_REGEX = r'(@test\.com$|@example\.com$|^pytest-.*@)'
_PYTEST_TITLE_MARKERS = [
    'Test pytest topic', 'Test Topic from API', 'Reply test',
    'Like test', 'Report test', 'Integration test topic',
]
_PYTEST_CONTENT_MARKERS = [
    'Pytest reply', 'Content from pytest',
    'This is a test topic created during API testing',
    'Content from integration test',
]
_PYTEST_REPORT_REASONS = ['Spam test']


async def _identify_pytest_artifacts():
    """Identifie tous les documents pytest sans rien modifier.

    Retourne un dictionnaire avec :
      - pytest_user_ids : set d'ids utilisateurs pytest
      - pytest_topic_ids : set d'ids topics à supprimer
      - sample_* : échantillons (max 5) pour preview
      - counts : nombre de docs dans chaque collection qui seront supprimés
    """
    users = await db.forum_users.find(
        {}, {"_id": 0, "id": 1, "pseudo": 1, "email": 1}
    ).to_list(length=None)

    pytest_user_ids = set()
    pytest_user_samples = []
    for u in users:
        p = u.get('pseudo') or ''
        e = u.get('email') or ''
        if re.match(_PYTEST_PSEUDO_REGEX, p) or (e and re.search(_PYTEST_EMAIL_REGEX, e)):
            pytest_user_ids.add(u['id'])
            if len(pytest_user_samples) < 5:
                pytest_user_samples.append({"pseudo": p, "email": e or None})

    # Topics authored by pytest users + topics with pytest title markers
    topic_or = [{"author_id": {"$in": list(pytest_user_ids)}}] if pytest_user_ids else []
    topic_or.append({"title": {"$in": _PYTEST_TITLE_MARKERS}})

    topics_to_delete = await db.forum_topics.find(
        {"$or": topic_or}, {"_id": 0, "id": 1, "title": 1, "author_pseudo": 1}
    ).to_list(length=None)
    pytest_topic_ids = {t['id'] for t in topics_to_delete}
    topic_samples = [
        {"title": t.get('title'), "author_pseudo": t.get('author_pseudo')}
        for t in topics_to_delete[:5]
    ]

    # Replies: authored by pytest OR matching content markers OR orphan (topic_id in deleted)
    reply_or = []
    if pytest_user_ids:
        reply_or.append({"author_id": {"$in": list(pytest_user_ids)}})
    reply_or.append({"content": {"$in": _PYTEST_CONTENT_MARKERS}})
    if pytest_topic_ids:
        reply_or.append({"topic_id": {"$in": list(pytest_topic_ids)}})
    replies_count = await db.forum_replies.count_documents({"$or": reply_or}) if reply_or else 0

    # Reports: reporter pytest OR matching reason OR target topic pytest
    report_or = []
    if pytest_user_ids:
        report_or.append({"reporter_id": {"$in": list(pytest_user_ids)}})
    report_or.append({"reason": {"$in": _PYTEST_REPORT_REASONS}})
    if pytest_topic_ids:
        report_or.append({"target_type": "topic", "target_id": {"$in": list(pytest_topic_ids)}})
    reports_count = await db.forum_reports.count_documents({"$or": report_or}) if report_or else 0

    return {
        "pytest_user_ids": pytest_user_ids,
        "pytest_topic_ids": pytest_topic_ids,
        "counts": {
            "users": len(pytest_user_ids),
            "topics": len(pytest_topic_ids),
            "replies": replies_count,
            "reports": reports_count,
        },
        "samples": {
            "users": pytest_user_samples,
            "topics": topic_samples,
        },
    }


@router.get("/admin/forum/cleanup-pytest-preview")
async def admin_cleanup_pytest_preview(admin: dict = Depends(get_current_admin)):
    """DRY-RUN : affiche exactement ce qui SERAIT supprimé, sans rien toucher.
    À appeler AVANT le nettoyage pour vérifier qu'aucun vrai post n'est ciblé."""
    report = await _identify_pytest_artifacts()
    return {
        "dry_run": True,
        "counts": report["counts"],
        "samples": report["samples"],
        "total_to_delete": sum(report["counts"].values()),
    }


@router.post("/admin/forum/cleanup-pytest")
async def admin_cleanup_pytest(
    confirm: str,
    admin: dict = Depends(get_current_admin),
):
    """Supprime chirurgicalement les données pytest de la DB.
    Protégé par double confirmation : confirm doit valoir 'NETTOYER'.
    Opération idempotente : peut être relancée sans risque."""
    if confirm != "NETTOYER":
        raise HTTPException(
            status_code=400,
            detail="Confirmation requise : passez ?confirm=NETTOYER"
        )

    report = await _identify_pytest_artifacts()
    pytest_user_ids = list(report["pytest_user_ids"])
    pytest_topic_ids = list(report["pytest_topic_ids"])

    deleted_topics = 0
    deleted_replies = 0
    deleted_reports = 0
    deleted_users = 0

    # 1) Topics
    topic_or = []
    if pytest_user_ids:
        topic_or.append({"author_id": {"$in": pytest_user_ids}})
    topic_or.append({"title": {"$in": _PYTEST_TITLE_MARKERS}})
    if topic_or:
        r = await db.forum_topics.delete_many({"$or": topic_or})
        deleted_topics = r.deleted_count

    # 2) Replies (pytest authors + markers + orphan of deleted topics)
    reply_or = []
    if pytest_user_ids:
        reply_or.append({"author_id": {"$in": pytest_user_ids}})
    reply_or.append({"content": {"$in": _PYTEST_CONTENT_MARKERS}})
    if pytest_topic_ids:
        reply_or.append({"topic_id": {"$in": pytest_topic_ids}})
    if reply_or:
        r = await db.forum_replies.delete_many({"$or": reply_or})
        deleted_replies = r.deleted_count

    # 3) Reports (pytest reporters + reason markers + target topic pytest)
    report_or = []
    if pytest_user_ids:
        report_or.append({"reporter_id": {"$in": pytest_user_ids}})
    report_or.append({"reason": {"$in": _PYTEST_REPORT_REASONS}})
    if pytest_topic_ids:
        report_or.append({"target_type": "topic", "target_id": {"$in": pytest_topic_ids}})
    if report_or:
        r = await db.forum_reports.delete_many({"$or": report_or})
        deleted_reports = r.deleted_count

    # 4) Users (last, since replies/reports may still reference them via author_id)
    if pytest_user_ids:
        r = await db.forum_users.delete_many({"id": {"$in": pytest_user_ids}})
        deleted_users = r.deleted_count

    return {
        "success": True,
        "deleted": {
            "users": deleted_users,
            "topics": deleted_topics,
            "replies": deleted_replies,
            "reports": deleted_reports,
        },
        "total_deleted": deleted_users + deleted_topics + deleted_replies + deleted_reports,
        "performed_by": admin.get("sub") or admin.get("email"),
        "performed_at": datetime.now(timezone.utc).isoformat(),
    }
