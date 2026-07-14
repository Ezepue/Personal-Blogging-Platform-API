import json
import logging

from models.notification import NotificationDB
from database import get_db
from models.comment import CommentDB
from websocket_manager import websocket_manager

from sqlalchemy.orm import Session
from fastapi import HTTPException
from fastapi import WebSocket

# Logger setup
logger = logging.getLogger(__name__)


def serialize_notification(notification: NotificationDB) -> dict:
    """JSON-safe representation of a notification for WebSocket/HTTP delivery."""
    return {
        "id": notification.id,
        "user_id": notification.user_id,
        "message": notification.message,
        "is_read": notification.is_read,
        "extra_data": notification.extra_data,
        "created_at": notification.created_at.isoformat() if notification.created_at else None,
    }

def create_notification(db: Session, user_id: int, message: str):
    """Create a notification for a user."""
    notification = NotificationDB(user_id=user_id, message=message)
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification

def fetch_unread_notifications(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    """Fetch unread notifications for a user (newest first, empty list when none)."""
    return (
        db.query(NotificationDB)
        .filter(NotificationDB.user_id == user_id, NotificationDB.is_read == False)
        .order_by(NotificationDB.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def mark_notifications_as_read(db: Session, user_id: int, notification_ids: list):
    """Mark notifications as read."""
    notifications = db.query(NotificationDB).filter(
        NotificationDB.id.in_(notification_ids),
        NotificationDB.user_id == user_id
    ).all()

    if not notifications:
        raise HTTPException(status_code=404, detail="Notifications not found.")

    for notification in notifications:
        notification.is_read = True
    db.commit()
    return {"message": "Notifications marked as read successfully."}

async def send_notification_to_user(db: Session, user_id: int, message: str, websocket: WebSocket = None):
    """
    Sends a notification to a user asynchronously.
    - Stores the notification in the database.
    - Sends a real-time notification via WebSockets if available.
    """
    try:
        # Store notification in DB
        new_notification = NotificationDB(user_id=user_id, message=message, is_read=False)
        db.add(new_notification)
        db.commit()
        db.refresh(new_notification)

        logger.info(f"Notification sent to user {user_id}: {message}")

        payload = serialize_notification(new_notification)

        # Deliver in real time: to the explicit socket if given, otherwise to the
        # recipient's active connection (if any) via the shared manager.
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


