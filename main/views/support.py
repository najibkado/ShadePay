from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db import IntegrityError
from django.core.mail import EmailMessage
from django.urls import reverse
from main.models import User, BusinessWallet, Card, Bank, AdditionalInformation, Developer, Transaction, DeveloperInformation, Logs
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
from main.utils import get_internal_tc
import decimal


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

        # #Get business wallet shipping information

        try:
            shipping = transaction.sender_business_wallet.user.profile.get().shipping_address
            state = transaction.sender_business_wallet.user.profile.get().state
            country = transaction.sender_business_wallet.user.profile.get().country
        except:
            shipping = transaction.reciever_business_wallet.user.profile.get().shipping_address
            state = transaction.reciever_business_wallet.user.profile.get().state
            country = transaction.reciever_business_wallet.user.profile.get().country

        if transaction.transaction_code == 9 or transaction.transaction_code == 25:
            toRecieve = get_internal_tc(transaction.amount)
        else:
            toRecieve = None


        #To do for withdraw
        return JsonResponse({
            "message": "success",
            "toRecieve": transaction.amount - toRecieve if toRecieve else transaction.amount,
            "transaction": transaction.serialize(),
            "shipping": {
                "shipping": shipping,
                "state": state,
                "country": country
            }
        })

    else:

        return JsonResponse({
            "message": "failed"
        })

def wallet_name(request, wallet_type):

    addr = request.GET["addr"]

    if wallet_type == 3:
        try:
            wallet = BusinessWallet.objects.get(address=addr)
            try:
                dev = Developer.objects.get(wallet=wallet)
                try:
                    info = DeveloperInformation.objects.get(developer=dev)
                except DeveloperInformation.DoesNotExist:
                    wallet = None
                return JsonResponse({"name": info.business_name })
            except Developer.DoesNotExist:
                wallet = None
        except BusinessWallet.DoesNotExist:
            wallet = None
    else:
        wallet = None

    if wallet is not None:
        name = wallet.user.first_name + " " + wallet.user.last_name
    else:
        name = "Unverified, Please write a correct recipient address"

    return JsonResponse({"name": name})
