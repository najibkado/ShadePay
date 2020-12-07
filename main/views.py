from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    """
    Index page
    """
    return render(request, "main/index.html")

def construction(request):
    """
    Site under construction page
    """
    return render(request, "main/construction.html")

def about(request):
    """
    About us page
    """
    return render(request, "main/about.html")

def fees(request):
    """
    Fees and pricing page
    """
    return render(request, "main/fees.html")

def how(request):
    """
    How it works page
    """
    return render(request, "main/how.html")

def contact(request):
    """
    Contact page
    """
    return render(request, "main/contact.html")

def privacy(request):
    """
    Privacy policy page
    """
    return render(request, "main/privacy.html")

def terms(request):
    """
    Terms and Services Page
    """
    return render(request, "main/terms.html")

def protection(request):
    """
    Customer protection policy page
    """
    return render(request, "main/protection.html")

def overview(request):
    """
    Developer overview page
    """
    return render(request, "main/overview.html")