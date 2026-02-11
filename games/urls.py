from django.urls import path

from . import views

app_name = "games"
urlpatterns = [
    path("", views.index, name="index"),
    path("lobby", views.LobbyView.as_view(), name="lobby"),
    path("new", views.new, name="new")
]

