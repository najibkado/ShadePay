from django.shortcuts import render

def usage_view(request, id):
    return render(request, "main/usage.html", {
        "id": id
    })