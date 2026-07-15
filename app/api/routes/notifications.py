from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from typing import List
from app.models.notification import NotificationDB
from app.schemas.notification import NotificationResponse
from app.services.notifications import fetch_unread_notifications, serialize_notification
from app.ws import websocket_manager
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import UserDB
import logging

from fastapi import Query, HTTPException, status
from app.api.deps import verify_access_token

router = APIRouter()
logger = logging.getLogger(__name__)


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, token: str = Query(...)):
    """WebSocket endpoint authenticated by a short-lived, single-purpose ws ticket.

    Only ``token_type == "ws"`` is accepted; the long-lived access token is never
    valid here, so it never needs to appear in a URL/query string.
    """
    try:
        user_data = verify_access_token(token)
    except HTTPException:
        user_data = None

    valid = (
        user_data is not None
        and user_data.get("token_type") == "ws"
        and str(user_data.get("sub")) == str(user_id)
    )
    if not valid:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket_manager.connect(websocket, user_id)

    try:
        while True:
            data = await websocket.receive_text()
            if data == "get_notifications":
                db_gen = get_db()
                db = next(db_gen)
                try:
                    notifications = fetch_unread_notifications(db, user_id, 0, 10)
                    payload = [serialize_notification(n) for n in notifications]
                finally:
                    db_gen.close()
                await websocket.send_json({"notifications": payload})
            else:
                await websocket.send_text(f"Received unknown command: {data}")

    except WebSocketDisconnect:
        await websocket_manager.disconnect(user_id, websocket)
    except Exception:
        logger.warning(f"WebSocket error for user {user_id}", exc_info=True)
        await websocket_manager.disconnect(user_id, websocket)

@router.get("/unread", response_model=List[NotificationResponse])
def get_unread_notifications(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
    skip: int = 0,
    limit: int = 10
):
    """Fetch unread notifications for the current user."""
    return fetch_unread_notifications(db, current_user.id, skip, limit)


@router.get("/", response_model=List[NotificationResponse])
def get_all_notifications(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
    skip: int = 0,
    limit: int = 30,
):
    """Fetch all notifications (read and unread), newest first."""
    limit = min(100, max(1, limit))
    return (
        db.query(NotificationDB)
        .filter(NotificationDB.user_id == current_user.id)
        .order_by(NotificationDB.created_at.desc())
        .offset(max(0, skip))
        .limit(limit)
        .all()
    )

@router.post("/read/{notification_id}")
async def mark_read(
    notification_id: int,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notif = db.query(NotificationDB).filter(
        NotificationDB.id == notification_id,
        NotificationDB.user_id == current_user.id,
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    db.commit()
    return {"message": "Marked as read"}

@router.post("/read-all")
async def mark_all_read(
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.query(NotificationDB).filter(
        NotificationDB.user_id == current_user.id,
        NotificationDB.is_read == False,
    ).update({"is_read": True})
    db.commit()
    return {"message": "All notifications marked as read"}

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notif = db.query(NotificationDB).filter(
        NotificationDB.id == notification_id,
        NotificationDB.user_id == current_user.id,
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    db.delete(notif)
    db.commit()
    return {"message": "Deleted"}

