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


@login_required
def dashboard(request):
    """
    User dashboard
    """
    #Get logged in User
    loggedin_user = request.user

    #Get available wallets

    #Check if individual wallet exist
    try:
        individual_wallet = IndividualWallet.objects.get(user=loggedin_user)
    except IndividualWallet.DoesNotExist:
        individual_wallet = None

    #Check if saving wallet exist
    try:
        saving_wallet = SavingWallet.objects.get(user=loggedin_user)
    except SavingWallet.DoesNotExist:
        saving_wallet = None

    #Check if business wallet exist
    try:
        business_wallet = BusinessWallet.objects.get(user=loggedin_user)
    except BusinessWallet.DoesNotExist:
        business_wallet = None

    #Check if banks exist
    try:
        banks = Bank.objects.filter(user=loggedin_user)
    except Bank.DoesNotExist:
        banks = None

    #Check if cards exist
    try:
        cards = Card.objects.filter(user=loggedin_user)
    except Card.DoesNotExist:
        cards = None

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

    #What to do if user has all wallets and a status of 01
    if individual_wallet is not None and saving_wallet is not None and business_wallet is not None:

        if cards is not None and banks is not None:

            contex = {
                "transactions" : transactions,
                "cardsAndBanksStatus" : 1,
                "cards" : cards,
                "banks" : banks,
                "status": 1,
                "name" : loggedin_user.first_name + " " + loggedin_user.last_name,
                "individual_wallet" : individual_wallet,
                "saving_wallet" : saving_wallet,
                "business_wallet" : business_wallet
            }

        elif cards is not None and banks is None:

            contex = {
                "transactions" : transactions,
                "cardsAndBanksStatus" : 2,
                "cards" : cards,
                "status": 1,
                "name" : loggedin_user.first_name + " " + loggedin_user.last_name,
                "individual_wallet" : individual_wallet,
                "saving_wallet" : saving_wallet,
                "business_wallet" : business_wallet
            }

        elif cards is None and banks is not None:

            contex = {
                "transactions" : transactions,
                "cardsAndBanksStatus" : 3,
                "banks" : banks,
                "status": 1,
                "name" : loggedin_user.first_name + " " + loggedin_user.last_name,
                "individual_wallet" : individual_wallet,
                "saving_wallet" : saving_wallet,
                "business_wallet" : business_wallet
            }

        else:

            contex = {
                "transactions" : transactions,
                "cardsAndBanksStatus" : 0,
                "status": 1,
                "name" : loggedin_user.first_name + " " + loggedin_user.last_name,
                "individual_wallet" : individual_wallet,
                "saving_wallet" : saving_wallet,
                "business_wallet" : business_wallet
            }

        return render(request, "main/dashboard.html", contex)

    #What to do if user has only individual wallet and a status of 02
    elif individual_wallet is not None and saving_wallet is None and business_wallet is None:

        if cards is not None and banks is not None:

            contex = {
                "transactions" : transactions,
                "cardsAndBanksStatus" : 1,
                "cards" : cards,
                "banks" : banks,
                "status" : 2,
                "name" : loggedin_user.first_name + " " + loggedin_user.last_name,
                "individual_wallet" : individual_wallet
            }

        elif cards is not None and banks is None:

            contex = {
                "transactions" : transactions,
                "cardsAndBanksStatus" : 2,
                "cards" : cards,
                "status" : 2,
                "name" : loggedin_user.first_name + " " + loggedin_user.last_name,
                "individual_wallet" : individual_wallet
            }

        elif cards is None and banks is not None:

            contex = {
                "transactions" : transactions,
                "cardsAndBanksStatus" : 3,
                "banks" : banks,
                "status" : 2,
                "name" : loggedin_user.first_name + " " + loggedin_user.last_name,
                "individual_wallet" : individual_wallet
            }

        else:

            contex = {
                "transactions" : transactions,
                "cardsAndBanksStatus" : 0,
                "status" : 2,
                "name" : loggedin_user.first_name + " " + loggedin_user.last_name,
                "individual_wallet" : individual_wallet
            }

        return render(request, "main/dashboard.html", contex)
    
    #What to do if user has individual wallet and saving wallet with a status of 03
    elif individual_wallet is not None and saving_wallet is not None and business_wallet is None:

        if cards is not None and banks is not None:

            contex = {
                "transactions" : transactions,
                "cardsAndBanksStatus" : 1,
                "cards" : cards,
                "banks" : banks,
                "status" : 3,
                "name" : loggedin_user.first_name + " " + loggedin_user.last_name,
                "individual_wallet" : individual_wallet,
                "saving_wallet" : saving_wallet
            }

        elif cards is not None and banks is None:

            contex = {
                "transactions" : transactions,
                "cardsAndBanksStatus" : 2,
                "cards" : cards,
                "status" : 3,
                "name" : loggedin_user.first_name + " " + loggedin_user.last_name,
                "individual_wallet" : individual_wallet,
                "saving_wallet" : saving_wallet
            }

        elif cards is None and banks is not None:

            contex = {
                "transactions" : transactions,
                "cardsAndBanksStatus" : 3,
                "banks" : banks,
                "status" : 3,
                "name" : loggedin_user.first_name + " " + loggedin_user.last_name,
                "individual_wallet" : individual_wallet,
                "saving_wallet" : saving_wallet
            }

        else:

            contex = {
                "transactions" : transactions,
                "cardsAndBanksStatus" : 0,
                "status" : 3,
                "name" : loggedin_user.first_name + " " + loggedin_user.last_name,
                "individual_wallet" : individual_wallet,
                "saving_wallet" : saving_wallet
            }

        return render(request, "main/dashboard.html", contex)

    #What to do if user has individual wallet and business wallet with a status of 04
    elif individual_wallet is not None and saving_wallet is None and business_wallet is not None:

        if cards is not None and banks is not None:

            contex = {
                "transactions" : transactions,
                "cardsAndBanksStatus" : 1,
                "cards" : cards,
                "banks" : banks,
                "status" : 4,
                "name" : loggedin_user.first_name + " " + loggedin_user.last_name,
                "individual_wallet" : individual_wallet,
                "business_wallet" : business_wallet
            }

        elif cards is not None and banks is None:

            contex = {
                "transactions" : transactions,
                "cardsAndBanksStatus" : 2,
                "cards" : cards,
                "status" : 4,
                "name" : loggedin_user.first_name + " " + loggedin_user.last_name,
                "individual_wallet" : individual_wallet,
                "business_wallet" : business_wallet
            }


        elif cards is None and banks is not None:
            
            contex = {
                "transactions" : transactions,
                "cardsAndBanksStatus" : 3,
                "banks" : banks,
                "status" : 4,
                "name" : loggedin_user.first_name + " " + loggedin_user.last_name,
                "individual_wallet" : individual_wallet,
                "business_wallet" : business_wallet
            }


        else:

            contex = {
                "transactions" : transactions,
                "cardsAndBanksStatus" : 0,
                "status" : 4,
                "name" : loggedin_user.first_name + " " + loggedin_user.last_name,
                "individual_wallet" : individual_wallet,
                "business_wallet" : business_wallet
            }

        return render(request, "main/dashboard.html", contex)

    #What to do if user has only business wallet and a status of 05
    elif business_wallet is not None and saving_wallet is None and individual_wallet is None:

        if cards is not None and banks is not None:

            contex = {
                "transactions" : transactions,
                "cardsAndBanksStatus" : 1,
                "cards" : cards,
                "banks" : banks,
                "status" : 5,
                "name" : loggedin_user.first_name + " " + loggedin_user.last_name,
                "business_wallet" : business_wallet
            }

        elif cards is not None and banks is None:

            contex = {
                "transactions" : transactions,
                "cardsAndBanksStatus" : 2,
                "cards" : cards,
                "status" : 5,
                "name" : loggedin_user.first_name + " " + loggedin_user.last_name,
                "business_wallet" : business_wallet
            }

        elif cards is None and banks is not None:
            
            contex = {
                "transactions" : transactions,
                "cardsAndBanksStatus" : 3,
                "banks" : banks,
                "status" : 5,
                "name" : loggedin_user.first_name + " " + loggedin_user.last_name,
                "business_wallet" : business_wallet
            }

        else:

            contex = {
                "transactions" : transactions,
                "cardsAndBanksStatus" : 0,
                "status" : 5,
                "name" : loggedin_user.first_name + " " + loggedin_user.last_name,
                "business_wallet" : business_wallet
            }

        return render(request, "main/dashboard.html", contex)

 #What to do if user has business wallet and saving wallet with a status of 06
    elif business_wallet is not None and saving_wallet is not None and individual_wallet is None:

        if cards is not None and banks is not None:
            
            contex = {
                "transactions" : transactions,
                "cardsAndBanksStatus" : 1,
                "cards" : cards,
                "banks" : banks,
                "status" : 6,
                "name" : loggedin_user.first_name + " " + loggedin_user.last_name,
                "business_wallet" : business_wallet,
                "saving_wallet" : saving_wallet
            }

        elif cards is not None and banks is None:
            
            contex = {
                "transactions" : transactions,
                "cardsAndBanksStatus" : 2,
                "cards" : cards,
                "status" : 6,
                "name" : loggedin_user.first_name + " " + loggedin_user.last_name,
                "business_wallet" : business_wallet,
                "saving_wallet" : saving_wallet
            }

        elif cards is None and banks is not None:
            
            contex = {
                "transactions" : transactions,
                "cardsAndBanksStatus" : 3,
                "banks" : banks,
                "status" : 6,
                "name" : loggedin_user.first_name + " " + loggedin_user.last_name,
                "business_wallet" : business_wallet,
                "saving_wallet" : saving_wallet
            }

        else:
            
            contex = {
                "transactions" : transactions,
                "cardsAndBanksStatus" : 0,
                "status" : 6,
                "name" : loggedin_user.first_name + " " + loggedin_user.last_name,
                "business_wallet" : business_wallet,
                "saving_wallet" : saving_wallet
            }

        return render(request, "main/dashboard.html", contex)

    #What to do if user has no wallet and a status of 00
    else:

        contex = {
            "cardsAndBanksStatus" : 0,
            "status" : 0,
            "name" : loggedin_user.first_name + " " + loggedin_user.last_name
        }

        return render(request, "main/dashboard.html", contex)
