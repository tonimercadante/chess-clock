from channels.generic.websocket import AsyncWebsocketConsumer
import json


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self) -> None:
        self.game_id = self.scope["url_route"]["kwargs"]["game_id"]
        self.group_name = f"game_{self.game_id}"

        print(self.game_id)
        await self.accept()

    async def disconnect(self, code: int) -> None:
        pass

    async def receive(
        self, text_data: str | None = None, bytes_data: bytes | None = None
    ) -> None:
        print(text_data, 'message')
        await self.channel_layer.group_send(self.group_name, {
            "type": "clock_update",
            "turn": 'placeholder',
            "white_time_ms": 1,
            "black_time_ms": 2,
        })
        

    async def clock_update(self, event):
        await self.send(text_data=json.dumps({
            "turn": event["turn"],
            "white_time_ms": event["white_time_ms"],
            "black_time_ms": event["black_time_ms"],
        }))
