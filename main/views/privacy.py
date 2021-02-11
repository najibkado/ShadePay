from django.shortcuts import render

def privacy(request):
    """
    Privacy policy page
    """
    return render(request, "main/privacy.html")