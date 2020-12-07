from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("about", views.about, name="about"),
    path("fees", views.fees, name="fees"),
    path("how", views.how, name="how"),
    path("contact", views.contact, name="contact"),
    path("privacy", views.privacy, name="privacy"),
    path("terms", views.terms, name="terms"),
    path("protection", views.protection, name="protection"),
    path("overview", views.overview, name="overview"),
    path("construction", views.construction, name="construction")
]