from django.shortcuts import render

def notfound(request, notfound):
    """
    Error 404! page
    """
    return render(request, "main/error.html")
