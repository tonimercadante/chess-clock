from channels.generic.websocket import AsyncWebsocketConsumer

class QueueConsumer(AsyncWebsocketConsumer):
    # async def connect(self) -> None:
    #     return await super().connect()


    async def connect(self) -> None:
        await self.connect()

    async def disconnect(self, code: int) -> None:
        # return await super().disconnect(code)
        pass


    async def receive(self, text_data: str | None = None, bytes_data: bytes | None = None) -> None:
        pass
        # return await super().receive(text_data, bytes_data)




