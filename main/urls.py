from django.urls import path
from main.views import transactions, dashboard, support, auth, index, construction, about, fees, how, contact, privacy, terms, protection, overview, notfound

urlpatterns = [
    path("", index.index, name="index"),
    path("about", about.about, name="about"),
    path("fees", fees.fees, name="fees"),
    path("how", how.how, name="how"),
    path("contact", contact.contact, name="contact"),
    path("privacy", privacy.privacy, name="privacy"),
    path("terms", terms.terms, name="terms"),
    path("protection", protection.protection, name="protection"),
    path("overview", overview.overview, name="overview"),
    path("construction", construction.construction, name="construction"),
    path("register", auth.register, name="register"),
    path("login", auth.login_view, name="login"),
    path("recover_password", auth.recover, name="recover"),
    path("verify/<str:uuid>/<str:token>", auth.verify, name="verify"),
    path("password-reset/<str:uuid>/<str:token>", auth.password_reset, name="password-reset"),
    path("dashboard", dashboard.dashboard, name="dashboard"),
    path("transactions", transactions.transactions, name="transactions"),
    path("logout", auth.logout_view, name="logout"),
    path("input-validator", support.input_validator, name="input-validator"),
    path("transaction_details/<int:id>", support.transaction_details, name="transaction_details"),
    path("<str:notfound>", notfound.notfound, name="notfound")
]