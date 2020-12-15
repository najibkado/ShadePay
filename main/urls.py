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
    path("construction", views.construction, name="construction"),
    path("register", views.register, name="register"),
    path("login", views.login_view, name="login"),
    path("recover_password", views.recover, name="recover"),
    path("verify/<str:uuid>/<str:token>", views.verify, name="verify"),
    path("password-reset/<str:uuid>/<str:token>", views.password_reset, name="password-reset"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("logout", views.logout_view, name="logout"),
    path("input-validator", views.input_validator, name="input-validator"),
    path("<str:notfound>", views.notfound, name="notfound")
]