from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db import IntegrityError
from django.core.mail import EmailMessage
from django.urls import reverse
from main.models import User, IndividualWallet, SavingWallet, BusinessWallet, Card, Bank, AdditionalInformation, Developer, Transaction, Logs
from main.utils import email_token_generator
from django.contrib.auth import authenticate, login, logout
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required
from django.core.validators import validate_email
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import threading
import json
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator



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


def register(request):
    """
    Registration module
    """
    #Handle GET request
    if request.method == "GET":
        return render(request, "main/register.html")
    
    #Handle POST request
    if request.method == "POST":

        #Collect User Data
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        username = request.POST["username"]
        password = request.POST["password"]
        re_password = request.POST["re_password"]

        #Verify User Data
        if first_name == "" or last_name == "" or email == "" or username == "" or password == "" or re_password == "":
            return render(request, "main/register.html", {
                "message": "Fields can't be empty!"
            })

        #Verify User Password
        if password != re_password:
            return render(request, "main/register.html", {
                "message": "Password did not match!"
            })

        #Verify Password Length
        if len(password) < 6:
            return render(request, "main/register.html", {
                "message": "Passowrd too short!"
            })

        #Ensure User Email Does not Exist
        if User.objects.filter(email=email).exists():

            return render(request, "main/register.html", {
                "message": "Unable to create your account. Try again later!"
            })

        elif User.objects.filter(username=username).exists():
            
            return render(request, "main/register.html", {
                "message": "Unable to create your account. Try again later!"
            })

        else:
            #Create New User
            try:
                new_user = User.objects.create_user(
                    first_name = first_name,
                    last_name = last_name,
                    username = username,
                    email = email,
                    password = password
                )
                new_user.save()
            except IntegrityError:
                return render(request, "main/register.html", {
                    "message": "Unable to create your account. Try again later!"
                })

            #Generate verification link
            uuid = urlsafe_base64_encode(force_bytes(new_user.pk))
            token = email_token_generator.make_token(new_user)
            domain = get_current_site(request).domain
            verification_link = reverse('verify', kwargs = {'uuid' : uuid, 'token' : token})
            verification_url = 'https://' + domain + verification_link

            #Send User Email Verification Mail
            subject = 'ShadePay Account Activation'
            body = 'Hello ' + new_user.username + ', Please click on the link below to verify your account.\n' + verification_url + '\n' + '\n' + '\n' + 'Thankyou for choosing ShadePay'
            sender_email = 'services@shadepay.com'
            
            new_email = EmailMessage(
                subject,
                body,
                sender_email,
                [email],
            )

            EmailThread(new_email).start()
            
            #Login User
            login(request, new_user)

            #Redirect User To Dashboard

            return HttpResponseRedirect(reverse("dashboard"))

def verify(request, uuid, token):
    """
    Email verification module
    """

    #Verify user email
    try:
        id = force_text(urlsafe_base64_decode(uuid))
        user = User.objects.get(pk=id)

        if user.is_active:
            return HttpResponseRedirect(reverse('login'))

        else:
            user.is_active = True
            user.save()

            return HttpResponseRedirect(reverse('login'))

    except User.DoesNotExist: #Will be able crash the system if it gets a different exception
        return render(request, "main/register.html", {
            "message": "User not found, register as a new user please"
        })
    

def login_view(request):
    """
    Login module
    """

    if request.method == "GET":
        return render(request, "main/login.html")

    if request.method == "POST":
        
        #Get user data
        username = request.POST["username"]
        password = request.POST["password"]

        #Verify user data
        if username == "" or password == "":

            #Return an error message if not verified
            return render(request, "main/login.html", {
                "message": "Fields can't be empty!"
            })

         #Authenticate user
        authenticated_user = authenticate(request, username=username, password=password)

        #Verify authenticated user
        if authenticated_user is not None:
            
            #login user
            login(request, authenticated_user)

            #Redirect user to dashboard
            return HttpResponseRedirect(reverse("dashboard"))

        else:

            #Return an error message if not verified
            return render(request, "main/login.html", {
                "message": "Invalid user credentials!"
            })
            
@login_required
def logout_view(request):
    """
    Logout Module
    """
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def recover(request):
    """
    Recover password page. This loads the forget.html page
    And generates a reset password link and send to user email
    """
    if request.method == "GET":
        return render(request, "main/forget.html")

    if request.method == "POST":
        
        #Get user email
        email = request.POST["email"]

        #Validate email
        if not validate_email(email):
            
            #Check user existance
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return render(request, "main/forget.html", {
                    "message": "Recovery link has been sent to your email "
                })

            #Generate verification link
            uuid = urlsafe_base64_encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)
            domain = get_current_site(request).domain
            reset_link = reverse('password-reset', kwargs = {'uuid' : uuid, 'token' : token})
            reset_url = 'https://' + domain + reset_link

            #Send User Email Verification Mail
            subject = 'Password reset'
            body = 'Hello ' + user.username + '\n Please click on the link below to reset your password.\n' + reset_url + '\n' + '\n' + '\n' + 'Thankyou for choosing ShadePay'
            sender_email = 'services@shadepay.com'
            
            reset_email = EmailMessage(
                subject,
                body,
                sender_email,
                [email],
            )

            EmailThread(reset_email).start()

            return render(request, "main/forget.html", {
                "message": "Email sent successfully"
            })

        else:

            return render(request, "main/forget.html", {
                "message": "Enter a valid email!"
            })

def password_reset(request, uuid, token):
    """
    Reset password page
    """
    if request.method == "GET":

        #Check if token has been used
        try:

            id = force_text(urlsafe_base64_decode(uuid))
            user = User.objects.get(pk=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return render(request, "main/forget.html", {
                    "message": "Invalid link. Request new link!"
                })

        except User.DoesNotExist: #Will be able crash the system if it gets a different exception
            return render(request, "main/forget.html", {
                "message": "Something went wrong. Try again!"
            })

        #return reset page
        return render(request, "main/reset.html", {
            "uuid": uuid,
            "token": token
        })
         
    if request.method == "POST":

        #Get user new password
        password = request.POST["password"]
        repassword = request.POST["repassword"]

        #Confirm password
        if password == repassword:
            pass
        else:
            return render(request, "main/reset.html", {
                "uuid": uuid,
                "token": token,
                "message": "Passwords does not match!"
            })

        #Confirm password length
        if len(password) < 6:
            return render(request, "main/reset.html", {
                "uuid": uuid,
                "token": token,
                "message": "Passwords too short!"
            })
        
        #Get user 
        try:

            id = force_text(urlsafe_base64_decode(uuid))
            user = User.objects.get(pk=id)

            #Change password
            user.set_password(password)

            user.save()

            return render(request, "main/login.html", {
                "message": "Password reset successful. Login now!"
            })

        except User.DoesNotExist: #Will be able crash the system if it gets a different exception
            return render(request, "main/reset.html", {
                "message": "Unable to reset your password. Try again!"
            })
