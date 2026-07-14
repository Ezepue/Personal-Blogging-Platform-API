import logging
from fastapi import WebSocket
from typing import Dict

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        # Maps user_id to WebSocket
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """Accept the WebSocket connection and store it."""
        await websocket.accept()
        self.active_connections[user_id] = websocket

    async def disconnect(self, user_id: int):
        """Remove the connection and close the socket (awaits the close coroutine)."""
        websocket = self.active_connections.pop(user_id, None)
        if websocket is not None:
            try:
                await websocket.close()
            except Exception as e:
                logger.debug(f"Error closing WebSocket for user {user_id}: {e}")

    async def send_message(self, user_id: int, message: str):
        """Send a message to a specific user via WebSocket."""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(message)
            except Exception as e:
                logger.warning(f"Error sending message to user {user_id}: {e}")
                await self.disconnect(user_id)

    async def broadcast(self, message: str):
        """Broadcast a message to all active users."""
        for user_id, websocket in list(self.active_connections.items()):
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.warning(f"Error broadcasting to user {user_id}: {e}")

# Create a global instance for managing WebSocket connections
websocket_manager = WebSocketManager()
