from django.shortcuts import render

def terms(request):
    """
    Terms and Services Page
    """
    return render(request, "main/terms.html")