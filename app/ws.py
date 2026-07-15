"""In-process WebSocket connection registry for real-time notifications."""
import logging
from typing import Dict

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Tracks one live socket per user and delivers messages to it."""

    def __init__(self) -> None:
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int) -> None:
        """Accept the socket and register it as the user's current connection."""
        await websocket.accept()
        self.active_connections[user_id] = websocket

    async def disconnect(self, user_id: int, websocket: WebSocket = None) -> None:
        """Unregister the user's socket.

        Only removes the registry entry when it still points at ``websocket`` (when
        given), so a stale tab disconnecting cannot evict a newer live connection
        that replaced it.
        """
        current = self.active_connections.get(user_id)
        if current is None:
            return
        if websocket is not None and current is not websocket:
            return
        self.active_connections.pop(user_id, None)
        try:
            await current.close()
        except Exception as e:
            logger.debug(f"Error closing WebSocket for user {user_id}: {e}")

    async def send_message(self, user_id: int, message: str) -> None:
        """Send text to the user's socket; drop the connection on failure."""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(message)
            except Exception as e:
                logger.warning(f"Error sending to user {user_id}: {e}")
                await self.disconnect(user_id)

    async def broadcast(self, message: str) -> None:
        """Send text to every connected user, skipping failed sockets."""
        for user_id, websocket in list(self.active_connections.items()):
            try:
                await websocket.send_text(message)
            except Exception as e:
                logger.warning(f"Error broadcasting to user {user_id}: {e}")


websocket_manager = WebSocketManager()
