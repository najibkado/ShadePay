from django.shortcuts import render

def protection(request):
    """
    Customer protection policy page
    """
    return render(request, "main/protection.html")