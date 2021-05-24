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


@login_required
def dashboard(request):
    """
    User dashboard
    """
    #Get logged in User
    loggedin_user = request.user

    #Get available wallets

    #Check if business wallet exist
    try:
        business_wallet = BusinessWallet.objects.get(user=loggedin_user)
    except BusinessWallet.DoesNotExist:
        business_wallet = None

    #Check for outgoing transactions
    try:
        transactions1 = Transaction.objects.filter(sender=loggedin_user)
    except Transaction.DoesNotExist:
        transactions1 = None

    #Check for incoming transactions
    try:
        transactions2 = Transaction.objects.filter(reciever=loggedin_user)
    except Transaction.DoesNotExist:
        transactions2 = None

    #Set transactions into a sorted form

    if transactions1 is not None and transactions2 is not None:

        transactions = [transaction for transaction in transactions1]

        for transaction in transactions2:
            transactions.append(transaction)

        def key(tran):
            """
            Returns sorting key
            """
            return tran.date

        transactions.sort(key=key, reverse=True)

    elif transactions1 is not None and transactions2 is None:
        
        transactions = [transaction for transaction in transactions1]

        def key(tran):
            """
            Returns sorting key
            """
            return tran.date

        transactions.sort(key=key, reverse=True)

    elif transactions1 is None and transactions2 is not None:

        transactions = [transaction for transaction in transactions2]

        def key(tran):
            """
            Returns sorting key
            """
            return tran.date

        transactions.sort(key=key, reverse=True)

    #Remove duplicates using set function
    t = set()
    for i in transactions:
        t.add(i)

    transactions = list(t)

    def key(tran):
            """
            Returns sorting key
            """
            return tran.date

    transactions.sort(key=key, reverse=True)

    transactions = transactions[0:10] if len(transactions) >= 10 else transactions

    """
    Wallet status availability codes

    00 = No wallet
    01 = All wallets
    02 = Individual wallet 
    03 = Individual wallet & Saving wallet
    04 = Individual wallet & Business wallet
    05 = Business wallet
    06 = Business wallet & Saving wallet 
    """

    """
    Cards and Banks availability status codes

    00 = No card or bank
    01 = All exists
    02 = Only cards
    03 = Only banks
    """

    if business_wallet:
        contex = {
                "transactions" : transactions,
                "status": 1,
                "name" : loggedin_user.first_name + " " + loggedin_user.last_name,
                "business_wallet" : business_wallet
        }

        return render(request, "main/dashboard.html", contex)
    else:

        contex = {
            "status" : 0,
            "name" : loggedin_user.first_name + " " + loggedin_user.last_name
        }

        return render(request, "main/dashboard.html", contex)
