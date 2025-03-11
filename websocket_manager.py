from fastapi import WebSocket
from typing import Dict

class WebSocketManager:
    def __init__(self):
        # Maps user_id to WebSocket
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        """Accept the WebSocket connection and store it."""
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        """Disconnect the WebSocket for the given user_id."""
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_message(self, user_id: int, message: str):
        """Send a message to a specific user via WebSocket."""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_text(message)
            except Exception as e:
                # Log the error and disconnect the user if there's an issue
                print(f"Error sending message to user {user_id}: {str(e)}")
                self.disconnect(user_id)

    async def broadcast(self, message: str):
        """Broadcast a message to all active users."""
        for websocket in self.active_connections.values():
            try:
                await websocket.send_text(message)
            except Exception as e:
                # Log and skip any failed connections
                print(f"Error broadcasting message: {str(e)}")

# Create a global instance for managing WebSocket connections
websocket_manager = WebSocketManager()
