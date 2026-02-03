from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

# Create your views here.
def index(request: HttpRequest) -> HttpResponse: 
    return HttpResponse("Hi game")

def lobby(request: HttpResponse) -> HttpResponse:
    return HttpResponse("Lobby")
