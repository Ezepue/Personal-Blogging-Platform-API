"""Notification domain: persistence, preference gating, real-time delivery."""
import json
import logging

from sqlalchemy.orm import Session
from fastapi import WebSocket

from app.models.notification import NotificationDB
from app.models.user import UserDB
from app.ws import websocket_manager

logger = logging.getLogger(__name__)

_PREF_FOR_TYPE = {
    "like": "notify_likes",
    "comment": "notify_comments",
    "mention": "notify_comments",  # mentions arrive via comments; gate them together
    "follow": "notify_follows",
}


def serialize_notification(notification: NotificationDB) -> dict:
    """JSON-safe representation used for WebSocket delivery."""
    return {
        "id": notification.id,
        "user_id": notification.user_id,
        "message": notification.message,
        "type": notification.type,
        "is_read": notification.is_read,
        "extra_data": notification.extra_data,
        "created_at": notification.created_at.isoformat() if notification.created_at else None,
    }


def _recipient_allows(db: Session, user_id: int, notif_type: str) -> bool:
    """Check the recipient's preferences for this event type.

    Mention and system notifications are always delivered.
    """
    pref_field = _PREF_FOR_TYPE.get(notif_type)
    if pref_field is None:
        return True
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    return bool(user and getattr(user, pref_field, True))


def fetch_unread_notifications(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    """Unread notifications, newest first (empty list when none)."""
    return (
        db.query(NotificationDB)
        .filter(NotificationDB.user_id == user_id, NotificationDB.is_read == False)
        .order_by(NotificationDB.created_at.desc())
        .offset(max(0, skip))
        .limit(limit)
        .all()
    )


async def send_notification_to_user(
    db: Session,
    user_id: int,
    message: str,
    websocket: WebSocket = None,
    notif_type: str = "system",
    extra_data: dict = None,
):
    """Persist a notification and push it in real time when the user is connected.

    Respects the recipient's notification preferences; failures in real-time
    delivery are swallowed — the stored notification is the source of truth.
    """
    try:
        if not _recipient_allows(db, user_id, notif_type):
            return None

        new_notification = NotificationDB(
            user_id=user_id, message=message, is_read=False,
            type=notif_type, extra_data=extra_data,
        )
        db.add(new_notification)
        db.commit()
        db.refresh(new_notification)

        payload = serialize_notification(new_notification)
        try:
            if websocket:
                await websocket.send_json(payload)
            else:
                await websocket_manager.send_message(user_id, json.dumps(payload))
        except Exception as ws_error:
            logger.debug(f"Real-time delivery skipped for user {user_id}: {ws_error}")

        return new_notification
    except Exception as e:
        logger.error(f"Failed to send notification to user {user_id}: {e}")
        return None
