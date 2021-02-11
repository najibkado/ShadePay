from django.urls import path, include
from api.views import index

urlpatterns = [
    path('', index.index, name="index"),
]