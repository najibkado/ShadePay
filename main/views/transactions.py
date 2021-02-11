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

"""
Transaction Codes
01 = Send Internal With Individual Wallet  -- Individual Wallet to Individual Wallet
02 = Request Internal with Individual Wallet  -- Individual Wallet to Individual Wallet
03 = Pay With Card  -- Card to Business Wallet
04 = Pay With Bank  -- Bank to Business Wallet
05 = Deposit To Individual Wallet   -- Card to Individual Wallet
06 = Deposit To Saving Wallet  -- Card to Saving Wallet
07 = Deposit To Business Wallet  -- Card to Business Wallet
08 = Pay With Individual Wallet  -- Individual Wallet to Business Wallet
09 = Pay With Business Wallet  -- Business Wallet to Business Wallet
10 = Withdraw From Saving Wallet  -- Saving wallet to Bank
11 = Withdraw From Business Wallet  -- Business wallet to Bank
12 = Withdraw From Individual Wallet  -- Individual wallet to Bank
13 = Pay With Individual Wallet2  -- Individual Wallet to Saving Wallet
14 = Pay With Business Wallet2  -- Business Wallet to Saving Wallet
15 = Pay With Business Wallet3  -- Business Wallet to Individual Wallet
16 = Request Internal with Individual Wallet  -- Individual Wallet to Business Wallet
17 = Request Internal with Business Wallet  -- Business Wallet to Business Wallet
18 = Request Internal with Business Wallet  -- Business Wallet to Individual Wallet
"""

"""
Transaction Status Codes
01 = Success
02 = Canceled 
03 = Refund
04 = Hold
05 = Review
"""

"""
Test Account

User -------- Pass

najibkado   123456      All Wallets
najib       123456      All Wallets
najibkado1  123456      Individual Wallet
najib1      123456      Individual wallet and Saving wallet
"""

@login_required
def transactions(request):
    """
    Returns all transactions paginated
    """

    #Get user
    user = request.user

    #Get Transactions as a sender
    transaction1 = Transaction.objects.filter(sender=user)

    #Get Transactions as a reciever
    transaction2 = Transaction.objects.filter(reciever=user)

    #Join all transactions in transactions
    transactions = [transaction for transaction in transaction1]

    for i in transaction2:
        transactions.append(i)

    #Define key for sorting key 
    def key(transaction):
        """
        Returns sorting key
        """
        return transaction.date

    #Sort transactions based on most recent date
    transactions.sort(key=key, reverse=True)

    #Paginate transactions
    paginated_transactions = Paginator(transactions, 10)

    #get requested transaction page
    requested_transaction_page = request.GET.get("page")

    #Check if transaction page is first page
    if requested_transaction_page is None:

        transactions_page = paginated_transactions.page(1)

    else:

        page = int(requested_transaction_page)

        print(paginated_transactions.page_range)

        #if requested page exceeds number of pages
        if page <= paginated_transactions.num_pages:

            transactions_page = paginated_transactions.page(page)

        else:

            transactions_page = paginated_transactions.page(paginated_transactions.num_pages)

    return render(request, "main/transactions.html", {
        "transactions" : transactions_page
    })