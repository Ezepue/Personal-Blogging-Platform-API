from models.notification import NotificationDB
from database import get_db
from models.comment import CommentDB

from sqlalchemy.orm import Session
from fastapi import HTTPException
from fastapi import WebSocket
import logging

# Logger setup
logger = logging.getLogger(__name__)

def create_notification(db: Session, user_id: int, message: str):
    """Create a notification for a user."""
    notification = NotificationDB(user_id=user_id, message=message)
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification

def fetch_unread_notifications(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    """Fetch unread notifications for a user with pagination support."""
    notifications = db.query(NotificationDB).filter(
        NotificationDB.user_id == user_id,
        NotificationDB.is_read == False
    ).offset(skip).limit(limit).all()

    if not notifications:
        raise HTTPException(status_code=404, detail="No unread notifications found.")

    return notifications

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

        # Send real-time notification via WebSockets
        if websocket:
            await websocket.send_json({"user_id": user_id, "message": message})

        return new_notification
    except Exception as e:
        logger.error(f"Failed to send notification to user {user_id}: {e}")
        return None


