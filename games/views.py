from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from typing import cast

from games.models import Clocks


# Create your views here.
def index(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Hi game")


@login_required
def lobby(request: HttpRequest) -> HttpResponse:
    username = request.user.username

    clocks = Clocks.objects.all()

    context = {"username": username, "clocks": clocks}
    return render(request, "games/index.html", context)


@login_required
def new(request: HttpRequest) -> HttpResponse:
    user = request.user
    clock_type = request.POST["clock"]

    return HttpResponse("ok")
