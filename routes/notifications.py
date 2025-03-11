from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from models.notification import NotificationDB
from utils.notification_helper import fetch_unread_notifications, send_notification_to_user
from websocket_manager import websocket_manager
from database import get_db
from utils.auth_helpers import get_current_user
from models.user import UserDB
import logging

from fastapi import Query, HTTPException, status
from utils.auth_helpers import verify_access_token

router = APIRouter()
logger = logging.getLogger(__name__)




@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, token: str = Query(...)):
    """WebSocket endpoint with authentication."""
    # Verify the token before allowing connection
    user_data = verify_access_token(token)
    if not user_data or user_data.get("user_id") != user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket_manager.connect(websocket, user_id)

    try:
        while True:
            data = await websocket.receive_text()
            if data == "get_notifications":
                db = next(get_db())
                notifications = fetch_unread_notifications(db, user_id, 0, 10)
                await websocket.send_json({"notifications": notifications})
            else:
                await websocket.send_text(f"Received unknown command: {data}")

    except WebSocketDisconnect:
        websocket_manager.disconnect(user_id)

@router.get("/unread", response_model=list)
def get_unread_notifications(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
    skip: int = 0,
    limit: int = 10
):
    """Fetch unread notifications for the current user."""
    return fetch_unread_notifications(db, current_user.id, skip, limit)

# Function to send a notification to a user via WebSocket
async def send_notification_to_user(user_id: int, notification_data: dict):
    """Send a real-time notification to the user."""
    websocket = websocket_manager.get(user_id)
    if websocket:
        await websocket.send_json(notification_data)
    else:
        # If the user is offline, store the notification in the database
        new_notification = NotificationDB(user_id=user_id, **notification_data)
        db.add(new_notification)
        db.commit()
