from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

import time

from games.models import Clocks, Games, Ratings
from games.redis_connection import MATCHMAKING_LUA, redis_client

from django.contrib.auth import get_user_model

User = get_user_model()


# Create your views here.
def index(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Hi game")


class LobbyView(LoginRequiredMixin, generic.TemplateView):
    template_name = "games/lobby.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["username"] = self.request.user.get_username()
        context["clocks"] = Clocks.objects.all()
        return context


@login_required
def new(request: HttpRequest) -> HttpResponse:
    user = request.user
    clock_type = request.POST["clock"]

    clock = Clocks.objects.get(id=clock_type)
    rating, _ = Ratings.objects.get_or_create(user=user, type=clock.type, defaults={})

    queue = f"mm:{clock.type.name}:{clock.start_time}:{clock.incremental_time}"

    opponent_id = redis_client.eval(
        MATCHMAKING_LUA,
        1,
        queue,
        str(user.id),
        str(rating.rating),
        str(100),  # rating range
    )

    if opponent_id:
        opponent = User.objects.get(id=opponent_id)
        game = Games.objects.create(
            player_white=opponent,
            player_black=user,
            started_at=timezone.now(),
            clock=clock,
        )

        start_ms = clock.start_time
        increment_ms = clock.incremental_time
        now_ms = int(time.time() * 1000)

        state_key = f"game:{game.id}:state"
        pipe = redis_client.pipeline()
        pipe.hset(
            state_key,
            mapping={
                "status": "active",
                "turn": "white",
                "move_count": 0,
                "white_time_ms": start_ms,
                "black_time_ms": start_ms,
                "increment_ms": increment_ms,
                "white_player_id": str(opponent_id),
                "black_player_id": str(user.id),
                "last_move_at": now_ms,
            },
        )

        pipe.expire(state_key, 86400)
        pipe.execute()

        channel_layer = get_channel_layer()
        payload = {"type": "match_found", "game_id": str(game.id)}

        async_to_sync(channel_layer.group_send)(f"queue_{user.id}", payload)
        async_to_sync(channel_layer.group_send)(f"queue_{opponent_id}", payload)

        return JsonResponse({"status": "matched"})

    return JsonResponse({"status": "queued"})


@login_required
def game(request: HttpRequest, game_id: int) -> HttpResponse:
    game = get_object_or_404(Games, pk=game_id)
    user = request.user

    if user == game.player_white:
        player_color = "white"
    else:
        player_color = "black"

    context = {
        "game_id": game.id,
        "white_nickname": game.player_white.username,
        "black_nickname": game.player_black.username,
        "start_time_ms": game.clock.start_time,
        "start_time_minutes": game.clock.start_time // 60000,
        "incremental_time_ms": game.clock.incremental_time,
        "player_color": player_color,
    }

    return render(request, "games/game.html", context)
