from sqlalchemy.orm import Session
from models.notification import NotificationDB

def create_notification(db: Session, user_id: int, message: str):
    notification = NotificationDB(user_id=user_id, message=message)
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification

def fetch_unread_notifications(db: Session, user_id: int):
    return db.query(NotificationDB).filter(NotificationDB.user_id == user_id, NotificationDB.is_read == False).all()
