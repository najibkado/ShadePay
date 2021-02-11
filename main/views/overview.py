from django.shortcuts import render

def overview(request):
    """
    Developer overview page
    """
    return render(request, "main/overview.html")