from channels.generic.websocket import AsyncWebsocketConsumer


class GameConsumer(AsyncWebsocketConsumer):
	async def connect(self) -> None:
		await self.accept()

	async def disconnect(self, code: int) -> None:
		pass

	async def receive(self, text_data: str | None = None, bytes_data: bytes | None = None) -> None:
		pass
