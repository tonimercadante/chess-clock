from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

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
    rating, created = Ratings.objects.get_or_create(
        user=user,
        type=clock.type,
        defaults={}
    )

    queue = f'mm:{clock.type.name}:{clock.start_time}:{clock.incremental_time}'
    
    opponent_id = redis_client.eval(
        MATCHMAKING_LUA,
        1,
        queue,
        str(user.id),
        str(rating.rating),
        str(100)  # rating range
    )
    
    if opponent_id:
        opponent = User.objects.get(id=opponent_id)
        game = Games.objects.create(
            player_white=opponent,
            player_black=user,
            started_at=timezone.now(),
            clock=clock,
        )

        channel_layer = get_channel_layer()
        payload = {"type": "match_found", "game_id": str(game.id)}

        async_to_sync(channel_layer.group_send)(f"queue_{user.id}", payload)
        async_to_sync(channel_layer.group_send)(f"queue_{opponent_id}", payload)

        return JsonResponse({"status": "matched"})

    return JsonResponse({"status": "queued"})


@login_required
def game(request: HttpRequest, game_id: int) -> HttpResponse:
    user = request.user
    context = {
            'username': user.username
    }
    return render(request, "games/game.html", context)

    # return HttpResponse('match %s' % game_id)


