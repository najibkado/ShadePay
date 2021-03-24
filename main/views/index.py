from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect
from main.utils import get_geol, get_client
from geopy.geocoders import Nominatim
from main.email import EmailSender

def index(request):
    """
    Index page
    """
    return render(request, "main/index.html")
