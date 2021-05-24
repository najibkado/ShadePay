from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db import IntegrityError
from django.core.mail import EmailMessage
from django.urls import reverse
from main.models import User, BusinessWallet, Card, Bank, AdditionalInformation, Developer, Transaction, Logs
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
from django.contrib import messages
from main.utils import validate
from main.utils import get_geol, get_client, get_ip
from geopy.geocoders import Nominatim


geolocator = Nominatim(user_agent="shadepay")

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
            messages.error(request, "Fields can't be empty")
            return HttpResponseRedirect(reverse("main:register"))

        if validate(email):
            pass
        else:
            messages.error(request, "Please enter a correct email")
            return HttpResponseRedirect(reverse("main:register"))

        #Verify User Password
        if password != re_password:
            messages.error(request, "Passworrd did not match")
            return HttpResponseRedirect(reverse("main:register"))

        #Verify Password Length
        if len(password) < 6:
            messages.error(request, "Password too short")
            return HttpResponseRedirect(reverse("main:register"))

        #Ensure User Email Does not Exist
        if User.objects.filter(email=email).exists():

            messages.error(request, "Unable to create account, please try again")
            return HttpResponseRedirect(reverse("main:register"))

        elif User.objects.filter(username=username).exists():
            
            messages.error(request, "Unable to create account, please try again")
            return HttpResponseRedirect(reverse("main:register"))

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
                messages.error(request, "Unable to create account, please try again")
                return HttpResponseRedirect(reverse("main:register"))

            #Generate verification link
            uuid = urlsafe_base64_encode(force_bytes(new_user.pk))
            token = email_token_generator.make_token(new_user)
            domain = get_current_site(request).domain
            verification_link = reverse('main:verify', kwargs = {'uuid' : uuid, 'token' : token})
            verification_url = 'https://' + domain + verification_link

            #Send User Email Verification Mail
            subject = 'ShadePay Account Activation'
            body = 'Hello ' + new_user.username + ', Please click on the link below to verify your account.\n'+verification_url+'\n' + '\n' + '\n'+'Thankyou for choosing ShadePay'
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

            ip = get_ip(request)
            lon, lat, city, country = get_geol(ip)

            try:
                location = geolocator.geocode(city)
            except:
                location = "unknown"

            client=get_client(request)

            try:
                log = Logs(
                    user=new_user,
                    ip_address=ip,
                    login_location=location,
                    lon=lon,
                    lat=lat,
                    login_device=client
                )

                log.save()
            except IntegrityError:
                log = Logs(
                    user=new_user,
                    ip_address="unknown",
                    login_location="unknown",
                    lon="unknown",
                    lat="unknown",
                    login_device=client
                )
                log.save()

            #Redirect User To Dashboard

            return HttpResponseRedirect(reverse("main:dashboard"))

def verify(request, uuid, token):
    """
    Email verification module
    """

    #Verify user email
    try:
        id = force_text(urlsafe_base64_decode(uuid))
        user = User.objects.get(pk=id)

        if user.is_active:
            return HttpResponseRedirect(reverse('main:login'))

        else:
            user.is_active = True
            user.save()


            return HttpResponseRedirect(reverse('main:login'))

    except User.DoesNotExist: #Will be able crash the system if it gets a different exception
        messages.error(request, "User not found, register as a new user please")
        return HttpResponseRedirect(reverse("main:register"))

@login_required
def unverified(request):
    return render(request, "main/unverified.html")

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
            messages.error(request, "Enter username and password")
            return HttpResponseRedirect(reverse("main:login"))

         #Authenticate user
        authenticated_user = authenticate(request, username=username, password=password)

        #Verify authenticated user
        if authenticated_user is not None:
            
            #login user
            login(request, authenticated_user)

            #Log User Session
            ip = get_ip(request)
            lon, lat, city, country = get_geol(ip)

            try:
                location = geolocator.geocode(city)
            except:
                location = "unknown"

            client=get_client(request)

            try:
                log = Logs(
                    user=authenticated_user,
                    ip_address=ip,
                    login_location=location,
                    lon=lon,
                    lat=lat,
                    login_device=client
                )

                log.save()
            except IntegrityError:
                log = Logs(
                    user=authenticated_user,
                    ip_address="unknown",
                    login_location="unknown",
                    lon="unknown",
                    lat="unknown",
                    login_device=client
                )
                log.save()

            #Redirect user to dashboard
            return HttpResponseRedirect(reverse("main:dashboard"))

        else:

            #Return an error message if not verified
            messages.error(request, "Invalid user credentials")
            return HttpResponseRedirect(reverse("main:login"))
            
@login_required
def logout_view(request):
    """
    Logout Module
    """
    logout(request)
    return HttpResponseRedirect(reverse("main:index"))

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
                messages.success(request, "Recovery link has been sent to your email.")
                return HttpResponseRedirect(reverse("main:recover"))

            #Generate verification link
            uuid = urlsafe_base64_encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)
            domain = get_current_site(request).domain
            reset_link = reverse('main:password-reset', kwargs = {'uuid' : uuid, 'token' : token})
            reset_url = 'https://' + domain + reset_link

            #Send User Email Verification Mail
            subject = 'Password reset'
            body = 'Hello ' + user.username + '\nPlease click on the link below to reset your password.\n' + reset_url +'\n' + '\n' + '\n'+'Thankyou for choosing ShadePay'
            sender_email = 'services@shadepay.com'
            
            reset_email = EmailMessage(
                subject,
                body,
                sender_email,
                [email],
            )

            EmailThread(reset_email).start()

            messages.success(request, "Recovery link has been sent to your email.")
            return HttpResponseRedirect(reverse("main:recover"))

        else:

            messages.error(request, "Enter a valid email.")
            return HttpResponseRedirect(reverse("main:recover"))

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

            messages.success(request, "Password reset successful, Login")
            return HttpResponseRedirect(reverse("main:login"))

        except User.DoesNotExist: #Will be able crash the system if it gets a different exception
            messages.error(request, "Unable to reset your password, Get a recovery link again.")
            return HttpResponseRedirect(reverse("main:recover"))