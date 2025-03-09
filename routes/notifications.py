from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from database import get_db
from utils.auth_helpers import get_current_user
from utils.notification_helpers import fetch_unread_notifications
from websocket_manager import websocket_manager
from models.user import UserDB

router = APIRouter()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket_manager.connect(websocket, user_id)
    try:
        while True:
            await websocket.receive_text()  # Keep the connection open
    except WebSocketDisconnect:
        websocket_manager.disconnect(user_id)

@router.get("/unread", response_model=list)
def get_unread_notifications(db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    return fetch_unread_notifications(db, current_user.id)
