from django.shortcuts import render

def how(request):
    """
    How it works page
    """
    return render(request, "main/how.html")