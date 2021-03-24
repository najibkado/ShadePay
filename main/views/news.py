from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from main.models import NewsletterRegister
from django.db import IntegrityError

def newsletter(request):
    if request.method == "POST":

        email = request.POST['email']

        def validate(e):
            try:
                validate_email(e)
                return True
            except ValidationError:
                return False

        if validate(email):
            try:
                newsletter_register = NewsletterRegister(
                    email = email
                )
                newsletter_register.save()
            except:
                messages.error(request, "Unable to register your email to our news letter, Please try again.")
                return HttpResponseRedirect(reverse("index"))
            
            messages.success(request, "You have successfully subscribed to our newsletter.")
            return HttpResponseRedirect(reverse("index"))
        else:
            messages.error(request, "Please enter a valid email")
            return HttpResponseRedirect(reverse("index"))