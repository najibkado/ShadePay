from django.shortcuts import render

def fees(request):
    """
    Fees and pricing page
    """
    return render(request, "main/fees.html")