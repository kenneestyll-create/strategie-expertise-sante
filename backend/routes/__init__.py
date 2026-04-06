from routes.public import router as public_router
from routes.chatbot import router as chatbot_router
from routes.forum import router as forum_router
from routes.payments import router as payments_router
from routes.admin import router as admin_router
from routes.client import router as client_router
from routes.strategiia import router as strategiia_router
from routes.dossier_express import router as dossier_express_router
from routes.misc import router as misc_router
from routes.conseils import router as conseils_router
from routes.tracking import router as tracking_router
from routes.upload import router as upload_router
from routes.knowledge_patterns import router as knowledge_patterns_router
from routes.predictive_v2_admin import router as predictive_v2_router
from routes.feedback import router as feedback_router

all_routers = [
    public_router,
    chatbot_router,
    forum_router,
    payments_router,
    admin_router,
    client_router,
    strategiia_router,
    dossier_express_router,
    misc_router,
    conseils_router,
    tracking_router,
    upload_router,
    knowledge_patterns_router,
    predictive_v2_router,
    feedback_router,
]
