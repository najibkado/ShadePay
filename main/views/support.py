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


@csrf_exempt
def input_validator(request):
    """
    Username and Email validator when registering a user
    It returns a JSON response
    """
    if request.method == "POST":

        #Load json data
        data = json.loads(request.body)

        #Get data type
        input_type = str(data.get("type")).lower()     

        #Check if data type is username
        if input_type == "username":

            username = data.get("username")

            if username.isalnum():

                if User.objects.filter(username=username).exists():
                    return JsonResponse({
                        "message": "Invalid username"
                        })
                else:
                    return JsonResponse({
                        "message":"Valid username"
                    })
            else:

                return JsonResponse({
                    "message": "Invalid username"
                })
            
        
        #Check if data type is email
        if input_type == "email":
            
            email = data.get("email")

            try:

                User.objects.get(email=email)
                
                return JsonResponse({
                    "message": "Invalid email"
                })      
                
            except User.DoesNotExist:

                return JsonResponse({
                    "message": "Valid email"
                })

    #Exit
    return JsonResponse({
        "message": "Invalid username"
    })

def transaction_details(request, id):
    """
    This returns transaction details
    """
    try:
        transaction = Transaction.objects.get(pk=id)
    except Transaction.DoesNotExist:
        transaction = None


    if transaction is not None:

        return JsonResponse({
            "message": "success",
            "transaction": transaction.serialize()
        })

    else:

        return JsonResponse({
            "message": "failed"
        })
