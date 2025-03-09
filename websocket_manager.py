from fastapi import WebSocket

class WebSocketManager:
    def __init__(self):
        self.active_connections = {}  # Maps user_id to WebSocket

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_message(self, user_id: int, message: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

websocket_manager = WebSocketManager()
