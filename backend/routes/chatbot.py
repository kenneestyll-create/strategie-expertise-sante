from fastapi import APIRouter
from typing import Optional
from datetime import datetime, timezone
import uuid

from config import db
from models import ChatMessage, ChatResponse
from utils.chatbot import find_faq_response, get_ai_response

router = APIRouter()


@router.post("/chatbot", response_model=ChatResponse)
async def chatbot_message(chat_input: ChatMessage):
    session_id = chat_input.session_id or str(uuid.uuid4())

    session_doc = await db.chatbot_sessions.find_one({"session_id": session_id}, {"_id": 0})
    question_count = (session_doc.get("count", 0) if session_doc else 0) + 1

    if question_count > 5:
        return ChatResponse(
            response="Vous avez atteint la limite de 5 questions gratuites pour cette session.\n\n"
                     "Pour aller plus loin dans votre démarche :\n"
                     "- [Réservez un appel gratuit](/agenda) avec notre expert\n"
                     "- [Découvrez le Dossier Express IA](/dossier-express) pour une analyse complète\n"
                     "- [Consultez nos tarifs](/tarifs) pour un accompagnement personnalisé\n\n"
                     "Première consultation téléphonique gratuite — 10 minutes pour évaluer votre situation.",
            is_faq=False,
            session_id=session_id
        )

    await db.chatbot_sessions.update_one(
        {"session_id": session_id},
        {"$set": {"count": question_count, "updated_at": datetime.now(timezone.utc).isoformat()},
         "$setOnInsert": {"created_at": datetime.now(timezone.utc).isoformat()}},
        upsert=True
    )

    faq_response = find_faq_response(chat_input.message)
    if faq_response:
        return ChatResponse(response=faq_response, is_faq=True, session_id=session_id)

    ai_response = await get_ai_response(chat_input.message, session_id)
    return ChatResponse(response=ai_response, is_faq=False, session_id=session_id)


@router.get("/chatbot/quota/{session_id}")
async def chatbot_quota(session_id: str):
    session_doc = await db.chatbot_sessions.find_one({"session_id": session_id}, {"_id": 0})
    used = session_doc.get("count", 0) if session_doc else 0
    return {"remaining": max(0, 5 - used), "limit": 5, "used": min(used, 5)}
