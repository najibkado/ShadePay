from django.shortcuts import render

def about(request):
    """
    About us page
    """
    return render(request, "main/about.html")