from django.shortcuts import render

def construction(request):
    """
    Site under construction page
    """
    return render(request, "main/construction.html")