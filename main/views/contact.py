from django.shortcuts import render
from main.models import ContactUs
from django.db import IntegrityError
from django.core.mail import EmailMessage
import threading
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect

class EmailThread(threading.Thread):
    """
    Email Thread Class:
    This is to speed the process of sending email to users
    The thread will be used so as to not use network thread
    """

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        """
        Execute the message
        """
        self.email.send(fail_silently=False)

def contact(request):
    """
    Contact page
    """

    if request.method == "POST":
        
        first_name = request.POST["first-name"]
        last_name = request.POST["last-name"]
        phone = request.POST["phone"]
        email = request.POST["email"]
        message = request.POST["msg"]

        print(first_name)

        if "@" in email and "." in email:
            try:
                new_contact = ContactUs(
                    first_name = first_name,
                    last_name = last_name,
                    phone = phone,
                    email = email,
                    message = message
                )

                new_contact.save()

            except IntegrityError:

                messages.error(request, "failed to send your please try again")
                return HttpResponseRedirect(reverse("main:contact"))

            
            #Send User Email Verification Mail
            subject = 'ShadePay Contact Services'
            body = 'Your message has been recieved! \nYou will get a response from one of our team members shortly! \n\nKind regards\nShadePay Team'
            sender_email = 'services@shadepay.com'
            
            new_email = EmailMessage(
                subject,
                body,
                sender_email,
                [email],
            )

            EmailThread(new_email).start()

            messages.success(request, "Your message has been sent successfully")
            return HttpResponseRedirect(reverse("main:contact"))

           

    return render(request, "main/contact.html")