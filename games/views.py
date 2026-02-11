from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from games.models import Clocks


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

    return HttpResponse("ok")
