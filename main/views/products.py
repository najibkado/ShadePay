from django.shortcuts import render

def products_view(request, id):
    return render(request, "main/products.html", {
        "id": id
    })