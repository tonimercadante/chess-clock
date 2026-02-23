from channels.generic.websocket import AsyncWebsocketConsumer
from games.redis_connection import redis_client
import json
import time


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self) -> None:
        self.game_id = self.scope["url_route"]["kwargs"]["game_id"]
        self.group_name = f"game_{self.game_id}"

        self.user = self.scope.get("user")
        if self.user is None or not self.user.is_authenticated:
            await self.close(code=4001)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        state = redis_client.hgetall(f"game:{self.game_id}:state")

        if state:
            white_time = int(state.get("white_time_ms"))
            black_time = int(state.get("black_time_ms"))

            if state.get("status") == "active":
                try:
                    elapsed = int(time.time() * 1000) - int(
                        state.get("last_move_at") or 0
                    )
                except Exception:
                    elapsed = 0
                if state.get("turn") == "white":
                    white_time = max(0, white_time - elapsed)
                else:
                    black_time = max(0, black_time - elapsed)

            await self.send(
                json.dumps(
                    {
                        "type": "state_sync",
                        "currentPlayer": state.get("turn"),
                        "times": {"white": white_time, "black": black_time},
                        "moveCount": int(state.get("move_count") or 0),
                    }
                )
            )

    async def disconnect(self, code: int) -> None:
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if text_data:
            data = json.loads(text_data)
            if data.get("type") == "move":
                await self.handle_move(data)

    async def handle_move(self, text_data):
        now_ms = int(time.time() * 1000)

        state_key = f"game:{self.game_id}:state"
        state = redis_client.hgetall(state_key)
        if not state or state.get("status") != "active":
            return

        current_turn = state.get("turn")
        expected_player = state.get(f"{current_turn}_player_id")
        if str(self.user.id) != expected_player:
            return

        elapsed = now_ms - int(state["last_move_at"])
        white_time = int(state["white_time_ms"])
        black_time = int(state["black_time_ms"])
        if current_turn == "white":
            white_time = max(0, white_time - elapsed)
            if white_time == 0:
                await self.end_game("black", "timeout")
                return
        else:
            black_time = max(0, black_time - elapsed)
            if black_time == 0:
                await self.end_game("white", "timeout")
                return

        increment_ms = int(state.get("increment_ms", 0))
        if current_turn == "white":
            white_time += increment_ms
        else:
            black_time += increment_ms

        next_turn = "black" if current_turn == "white" else "white"
        move_count = int(state["move_count"]) + 1

        pipe = redis_client.pipeline()
        pipe.hset(
            state_key,
            mapping={
                "turn": next_turn,
                "move_count": move_count,
                "white_time_ms": white_time,
                "black_time_ms": black_time,
                "last_move_at": now_ms,
            },
        )
        pipe.expire(state_key, 86400)
        pipe.execute()

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "game_move",
                "currentPlayer": next_turn,
                "times": {"white": white_time, "black": black_time},
                "moveCount": move_count,
            },
        )

    async def game_move(self, event):
        await self.send(json.dumps(event))

    async def game_over(self, event):
        await self.send(json.dumps(event))

    async def end_game(self, winner: str, reason: str) -> None:
        state_key = f"game:{self.game_id}:state"
        redis_client.hset(state_key, "status", "finished")
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "game_over",
                "winner": winner,
                "reason": reason,
            },
        )
