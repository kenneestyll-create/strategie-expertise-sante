import os
import json
import logging
from pywebpush import webpush, WebPushException

logger = logging.getLogger(__name__)

VAPID_PRIVATE_KEY = os.environ.get("VAPID_PRIVATE_KEY", "").replace("\\n", "\n")
VAPID_PUBLIC_KEY = os.environ.get("VAPID_PUBLIC_KEY", "")
VAPID_SUBJECT = os.environ.get("VAPID_SUBJECT", "mailto:contact@strategie-expertise-sante.fr")


def send_push_notification(subscription_info: dict, title: str, body: str, url: str = "/espace-client", tag: str = "default") -> bool:
    if not VAPID_PRIVATE_KEY or not subscription_info:
        return False
    try:
        payload = json.dumps({
            "title": title,
            "body": body,
            "icon": "/logo-icon.svg",
            "badge": "/logo-icon.svg",
            "url": url,
            "tag": tag,
        })
        webpush(
            subscription_info=subscription_info,
            data=payload,
            vapid_private_key=VAPID_PRIVATE_KEY,
            vapid_claims={"sub": VAPID_SUBJECT},
        )
        return True
    except WebPushException as e:
        logger.error(f"Push notification failed: {e}")
        if "410" in str(e) or "404" in str(e):
            return False
        return False
    except Exception as e:
        logger.error(f"Push notification error: {e}")
        return False


async def send_push_to_client(db, client_id: str, title: str, body: str, url: str = "/espace-client", tag: str = "default"):
    subscriptions = await db.push_subscriptions.find(
        {"client_id": client_id},
        {"_id": 0}
    ).to_list(10)

    expired = []
    for sub in subscriptions:
        success = send_push_notification(sub["subscription"], title, body, url, tag)
        if not success:
            expired.append(sub["id"])

    if expired:
        await db.push_subscriptions.delete_many({"id": {"$in": expired}})
