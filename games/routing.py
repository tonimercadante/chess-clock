from django.urls import re_path

from .consumers import QueueConsumer, GameConsumer


websocket_urlpatterns = [
    re_path(r"ws/queue/$", QueueConsumer.as_asgi()),
    re_path(r"ws/game/(?P<game_id>\w+)/$", GameConsumer.as_asgi()),
]
