from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db import IntegrityError
from django.core.mail import EmailMessage
from django.urls import reverse
from main.models import User, BusinessWallet, Card, Bank, AdditionalInformation, Developer, Transaction, Logs, ProcessCardRequest, ProcessPayattitudeRequest, ApprovedUnprocessedCardRequest
from main.models import MissingWalletTransactionRequest, ApprovedUnprocessedCardlessRequest, MissingWalletCardlessTransactionRequest
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
import requests
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.contrib.sites.shortcuts import get_current_site
from main.transaction import Transaction as NewTransaction
import asyncio
from main.utils import get_domain
from django.contrib import messages
from decimal import Decimal
from api.models import MerchantRequest
from main.email import EmailSender

"""
Transaction Codes
03 = Pay With Card  -- Card to Business Wallet
07 = Deposit To Business Wallet  -- Card to Business Wallet
09 = Pay With Business Wallet  -- Business Wallet to Business Wallet
10 = Pay Business Wallet -- Merchant Shadepayment
11 = Withdraw From Business Wallet  -- Business wallet to Bank
17 = Request Internal with Business Wallet  -- Business Wallet to Business Wallet
21 = Deposit To Business Wallet -- Payattitude
25 = Pay Business wallet -- Merchant recieve with card

"""

"""
Transaction Status Codes
01 = Success
02 = Canceled 
03 = Refund
04 = Hold
05 = Review
06 = Initiated
"""

"""
Test Account

User -------- Pass

najibkado   12345678      All Wallets
najib       12345678      All Wallets
najibkado1  123456      Individual Wallet
najib1      12345678     Individual wallet and Saving wallet
najib12     12345678    Individual wallet and Business wallet
najib2      12345678    Business wallet
najib21     12345678    Business wallet and Saving wallet
"""

@login_required
def transactions(request):
    """
    Returns all transactions paginated
    """

    loggedin_user = request.user


    #Check if business wallet exist
    try:
        business_wallet = BusinessWallet.objects.get(user=loggedin_user)
    except BusinessWallet.DoesNotExist:
        business_wallet = None

    if business_wallet:
        status = 1
    else:
        status = 0

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

    t = set()
    for i in transactions:
        t.add(i)

    transactions = list(t)

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

        #if requested page exceeds number of pages
        if page <= paginated_transactions.num_pages:

            transactions_page = paginated_transactions.page(page)

        else:

            transactions_page = paginated_transactions.page(paginated_transactions.num_pages)

    return render(request, "main/transactions.html", {
        "transactions" : transactions_page,
        "status": status
    })

@login_required
def update_transaction(request, id, rtype):
    """
    Return Transactions code denoted as rtype
    Where id is the request unique identifier
    1 -> cardtopup
    2 -> cardlesstopup
    """

    def get_status(ref):
        response = requests.get(f"https://test.payarena.com/Status/{ref}")
        if response.status_code == 200:
            response = response.json()
            if response['Status'] == "Approved" or response['Status'] == "approved" or response['Status'] == "APPROVED":
                return True

            else:
                return False

        else:
            return False

    
    if rtype == 1:
        try:
            card_topup_request = ProcessCardRequest.objects.get(pk=id)
        except ProcessCardRequest.DoesNotExist:
            messages.error(request, "Transaction does not exist")
            return HttpResponseRedirect(reverse("main:error"))

        status = get_status(card_topup_request.reference)

        if status == True:
            card_topup_request.is_successful = True
            card_topup_request.save()

        else:
            card_topup_request.is_successful = False
            card_topup_request.save()

        if card_topup_request.is_successful:
            if card_topup_request.transaction_code == 7:
                transaction_obj = NewTransaction(
                    sender = card_topup_request.user,
                    reciever = card_topup_request.user,
                    transaction_code = 7,
                    amount = card_topup_request.amount,
                    sender_card = card_topup_request.card_first_six + "XXXX" + card_topup_request.card_last_four,
                    status_code = 1,
                    ref = card_topup_request.reference,
                    status = "Approved",
                    reciever_business_wallet = card_topup_request.business_wallet,
                )
                trx_data = transaction_obj.deposit_with_card_to_biz()
                if trx_data:
                    try:
                        wallet = BusinessWallet.objects.get(user = card_topup_request.user)
                        wallet.balance = wallet.balance + transaction_obj.amount
                        wallet.save()

                        #Send Email Notification to sender for credit
                        sender_email_body = {
                            "channel": "Card Topup",
                            "card": transaction_obj.sender_card,
                            "mobile": "",
                            "trx_ref": trx_data.reference,
                            "trx_date": trx_data.date,
                            "amount": trx_data.amount,
                            "reciever_wallet": trx_data.reciever_business_wallet.address,
                            "recieve_amount": trx_data.amount,
                            "status": "successful",
                            "email_for": transaction_obj.reciever.first_name + " " + transaction_obj.reciever.last_name
                        }

                        n = EmailSender(
                            "Transaction Alert",
                            transaction_obj.reciever.email,
                            sender_email_body
                        )

                        n.email_top_up()
                        
                        return HttpResponseRedirect(reverse("main:success"))
                    except BusinessWallet.DoesNotExist:
                        #Save approved and missing wallet transactions
                        missing_wallet_transaction = MissingWalletTransactionRequest(
                            procecc= card_topup_request
                        )
                        missing_wallet_transaction.save()
                        messages.error(request, "Unable to find receiving wallet, Please contact us")
                        return HttpResponseRedirect(reverse("main:error"))
                else:
                    #Save approved and unstored transactions for later process
                    transaction = ApprovedUnprocessedCardRequest(
                        process = card_topup_request
                    )
                    transaction.save()
                    messages.error(request, "Unable to process your transaction at the moment")
                    return HttpResponseRedirect(reverse("main:error"))

        else:
            messages.error(request, "Unable to verify your transaction")
            return HttpResponseRedirect(reverse("main:error"))

    if rtype == 2:
        
        try:
            cardless_topup_request = ProcessPayattitudeRequest.objects.get(pk=id)
        except ProcessCardRequest.DoesNotExist:
            messages.error(request, "Transaction does not exist")
            return HttpResponseRedirect(reverse("main:error"))

        status = get_status(cardless_topup_request.reference)

        if status == True:
            cardless_topup_request.is_successful = True
            cardless_topup_request.save()
        else:
            cardless_topup_request.is_successful = False
            cardless_topup_request.save()

        if cardless_topup_request.is_successful:
            
            if cardless_topup_request.transaction_code == 21:
                transaction_obj = NewTransaction(
                    sender=cardless_topup_request.user,
                    reciever=cardless_topup_request.user,
                    transaction_code=cardless_topup_request.transaction_code,
                    amount=cardless_topup_request.amount,
                    reciever_business_wallet=cardless_topup_request.business_wallet,
                    phone=cardless_topup_request.mobile,
                    status=cardless_topup_request.status,
                    status_code=1,
                    ref=cardless_topup_request.reference        
                )
                trx_data = transaction_obj.deposit_pat_to_biz()
                if trx_data:
                    try:
                        wallet = BusinessWallet.objects.get(user=cardless_topup_request.user)
                        wallet.balance = wallet.balance + transaction_obj.amount
                        wallet.save()

                        #Send Email Notification to sender for credit
                        sender_email_body = {
                            "channel": "Cardless Topup",
                            "card": "",
                            "mobile": trx_data.mobile,
                            "trx_ref": trx_data.reference,
                            "trx_date": trx_data.date,
                            "amount": trx_data.amount,
                            "reciever_wallet": trx_data.reciever_business_wallet.address,
                            "recieve_amount": trx_data.amount,
                            "status": "successful",
                            "email_for": transaction_obj.reciever.first_name + " " + transaction_obj.reciever.last_name
                        }

                        n = EmailSender(
                            "Transaction Alert",
                            transaction_obj.reciever.email,
                            sender_email_body
                        )

                        n.email_top_up()


                        return HttpResponseRedirect(reverse("main:success"))
                    except BusinessWallet.DoesNotExist:
                        missing_wallet_transaction = MissingWalletCardlessTransactionRequest(
                            process=cardless_topup_request
                        )
                        missing_wallet_transaction.save()
                        messages.error(request, "Unable to find receiving wallet")
                        return HttpResponseRedirect(reverse("main:error"))
                else:
                    unpocesses_cardless_transaction = ApprovedUnprocessedCardlessRequest(
                        process=cardless_topup_request
                    )
                    unpocesses_cardless_transaction.save()
                    messages.error(request, "Unable to process your transaction at the moment")
                    return HttpResponseRedirect(reverse("main:error"))

        else:
            messages.error(request, "Unable to verify your transaction")
            return HttpResponseRedirect(reverse("main:error"))

    if rtype == 3:
        try:
            card_topup_request = ProcessCardRequest.objects.get(pk=id)
        except ProcessCardRequest.DoesNotExist:
            messages.error(request, "Transaction does not exist")
            return HttpResponseRedirect(reverse("main:error"))

        try:
            merchant_request = MerchantRequest.objects.get(pk=card_topup_request.merchant_request.id)
        except MerchantRequest.DoesNotExist:
            messages.error(request, "Transaction does not exist")
            return HttpResponseRedirect(reverse("main:error"))

        status = get_status(card_topup_request.reference)

        if status == True:
            card_topup_request.is_successful = True
            card_topup_request.save()
            merchant_request.approved = True
            merchant_request.save()

        else:
            card_topup_request.is_successful = False
            card_topup_request.save()

        if card_topup_request.is_successful: 
            if card_topup_request.transaction_code == 25:
                transaction_obj = NewTransaction(
                    sender = card_topup_request.user,
                    reciever = card_topup_request.user,
                    transaction_code = 25,
                    amount = card_topup_request.amount,
                    sender_card = card_topup_request.card_first_six + "XXXX" + card_topup_request.card_last_four,
                    status_code = 1,
                    ref = card_topup_request.reference,
                    status = "Approved",
                    reciever_business_wallet = card_topup_request.business_wallet,
                )
                trx_data = transaction_obj.deposit_with_card_to_biz_mer()
                if trx_data:
                    try:
                        wallet = BusinessWallet.objects.get(user = card_topup_request.user)
                        wallet.balance = wallet.balance + (transaction_obj.amount - trx_data.transaction_charges)
                        wallet.save()
                        merchant_request.status = "success"
                        merchant_request.save()

                        #Send Email Notification to sender for credit
                        sender_email_body = {
                            "channel": "Merchant Payment",
                            "card": transaction_obj.sender_card,
                            "mobile": "",
                            "trx_ref": trx_data.reference,
                            "trx_date": trx_data.date,
                            "amount": trx_data.amount,
                            "reciever_wallet": trx_data.reciever_business_wallet.address,
                            "recieve_amount": trx_data.amount - trx_data.transaction_charges,
                            "status": "successful",
                            "email_for": transaction_obj.reciever.first_name + " " + transaction_obj.reciever.last_name
                        }

                        n = EmailSender(
                            "Transaction Alert",
                            transaction_obj.reciever.email,
                            sender_email_body
                        )

                        n.email_top_up()

                        #TODO: Handle redirection to merchant return URL
                        data = {
                            "transaction_id": merchant_request.id,
                            "successful": merchant_request.approved,
                            "status": merchant_request.status
                        }
                        response = requests.post(merchant_request.returnUrl, data=data)
                        return HttpResponseRedirect(merchant_request.returnUrl)
                    except BusinessWallet.DoesNotExist:
                        #Save approved and missing wallet transactions
                        missing_wallet_transaction = MissingWalletTransactionRequest(
                            procecc= card_topup_request
                        )
                        missing_wallet_transaction.save()
                        data = {
                            "transaction_id": merchant_request.id,
                            "successful": merchant_request.approved,
                            "status": merchant_request.status,
                            "error_message": "Unable to identify recieving wallet, please contact help"
                        }
                        response = requests.post(merchant_request.returnUrl, data=data)
                        return HttpResponseRedirect(merchant_request.returnUrl)
                else:
                    #Save approved and unstored transactions for later process
                    transaction = ApprovedUnprocessedCardRequest(
                        process = card_topup_request
                    )
                    transaction.save()
                    data = {
                            "transaction_id": merchant_request.id,
                            "successful": merchant_request.approved,
                            "status": merchant_request.status,
                            "error_message": "Unable to process payment at the moment, please contact help"
                        }
                    response = requests.post(merchant_request.returnUrl, data=data)
                    return HttpResponseRedirect(merchant_request.returnUrl)

        else:
            data = {
                    "transaction_id": merchant_request.id,
                    "unsuccessful": merchant_request.approved,
                    "status": merchant_request.status
                    }
            response = requests.post(merchant_request.returnUrl, data=data)
            return HttpResponseRedirect(merchant_request.returnUrl)

@login_required
def topUp(request):

    loggedin_user = request.user

    if request.method == "POST":
        
        amount = request.POST["amount"]
        wallet = request.POST["deposit-wallet"]
        card_scheme = request.POST["card-type"].lower()
        card_number = request.POST["card-number"]
        exp_month = request.POST["month"]
        exp_year = request.POST["year"]
        cvv = request.POST["cvv"]

       #get wallet to deposit money into
        #Then we try to create a new card process 
        if int(wallet) == 2:
            try:
                wallet = BusinessWallet.objects.get(user=request.user)
            except BusinessWallet.DoesNotExist:
                return HttpResponseRedirect(reverse("main:error"))

            try:
                new_request = ProcessCardRequest(
                    user = request.user,
                    amount = Decimal(amount),
                    card_first_six = card_number[0:7],
                    card_last_four = card_number[-4:-1],
                    card_type = card_scheme,
                    business_wallet = wallet,
                    transaction_code = 7,
                    reference = ""
                )
                new_request.save()
            except IntegrityError:
                return HttpResponseRedirect(reverse("main:error"))
        
        exp = exp_month + "/" + exp_year
        domain = get_domain(request)
        returnUrl = domain + f"/topup/return/{new_request.id}"

        if Logs.objects.filter(user=request.user).exists():
            logs = Logs.objects.filter(user=request.user).last()
            description = "IP: " + logs.ip_address + "  " + " Location: " + logs.login_location
        else:
            description = "IP: " + "unknown" + "  " + " Location: " + "unknown"

        #Start Transaction Process
        transaction_object = NewTransaction(
            sender=request.user,
            reciever=request.user,
            transaction_code=5,
            amount=Decimal(amount),
            description=description,
            come_back_url=returnUrl,
            sender_card=card_number,
            sender_card_expiry=exp,
            sender_card_cvv=cvv,
            scheme=card_scheme,
            process_card_id=new_request.id
        )

        transaction_url = transaction_object.process_card()

        if transaction_url != None:
            return HttpResponseRedirect(transaction_url)
        else:
            return HttpResponseRedirect(reverse("main:error"))

@csrf_exempt
def returnTopUpUrl(request, id):

    if request.method == "GET":
        try:
            requested_card_process = ProcessCardRequest.objects.get(pk=id)
        except ProcessCardRequest.DoesNotExist:
            messages.error(request, "Transaction does not exist.")
            return HttpResponseRedirect(reverse("main:error"))

        if requested_card_process.transaction_code == 25:
            #TODO: Review the implementation
            merchant_request = requested_card_process.merchant_request
            merchant_request.status = "failed"
            merchant_request.save()
            #TODO: Handle redirection to merchant return URL
            data = {
                "transaction_id": merchant_request.id,
                "unsuccessful": merchant_request.approved,
                "status": merchant_request.status
            }
            response = requests.post(merchant_request.returnUrl, data=data)
            return HttpResponseRedirect(merchant_request.returnUrl)
        else:
            messages.error(request, "Unable to process your transaction at the moment")
            return HttpResponseRedirect(reverse("main:error"))
    
    if request.method == "POST":

        status = request.POST['status']
        approved = request.POST['approved']
        trxID = request.POST['trxId']

        try:
            requested_card_process = ProcessCardRequest.objects.get(pk=id)
        except ProcessCardRequest.DoesNotExist:
            messages.error(request, "Transaction does not exist.")
            return HttpResponseRedirect(reverse("main:error"))

        rawdata = {}

        for key, value in request.POST.items():
            rawdata[key] = value

        requested_card_process.raw_data = rawdata
        requested_card_process.save()
        
        if int(requested_card_process.reference) == int(trxID):
            if approved == "true":
                requested_card_process.is_successful = True
                requested_card_process.status = status
                requested_card_process.save()
                if requested_card_process.transaction_code == 25:
                    #Update for merchant transaction
                    return HttpResponseRedirect(reverse("main:update_transaction", args=(requested_card_process.id, 3, )))
                else:
                    #Update for card top up
                    return HttpResponseRedirect(reverse("main:update_transaction", args=(requested_card_process.id, 1, )))
            else:
                requested_card_process.status = status
                requested_card_process.save()
                return HttpResponseRedirect(reverse("main:error"))

        messages.error(request, "Unable to match transaction reference")
        return HttpResponseRedirect(reverse("main:error"))

@login_required
def transaction_error(request):
    return render(request, "main/transaction_error.html")

@login_required
def transaction_success(request):
    return render(request, "main/transaction_success.html")

@login_required
def cardless(request):
    """
    This function process payattitude topup
    """
    loggedin_user = request.user

    if request.method == "GET":

        #Check if business wallet exist
        try:
            business_wallet = BusinessWallet.objects.get(user=loggedin_user)
        except BusinessWallet.DoesNotExist:
            business_wallet = None

        if business_wallet is not None:
            status = 1
        else:
            status = 0

        return render(request, "main/payattitude.html", {
            "status" : status
        })

    if request.method == "POST":
        amount = request.POST['amount']
        wallet = request.POST['wallet']
        mobile = request.POST['mobile']

        domain = get_domain(request)

        if int(wallet) == 3:
            try:
                wallet = BusinessWallet.objects.get(user=loggedin_user)
            except BusinessWallet.DoesNotExist:
                return HttpResponseRedirect(reverse("main:error"))

            try:
                new_request = ProcessPayattitudeRequest(
                    user = loggedin_user,
                    amount = Decimal(amount),
                    mobile = mobile,
                    business_wallet = wallet,
                    transaction_code = 21,
                    status = "",
                    reference = ""
                )
                new_request.save()
            except IntegrityError:
                return HttpResponseRedirect(reverse("main:error"))

            returnUrl =  domain + f"/cardless/return/{new_request.id}"

        if Logs.objects.filter(user=request.user).exists():
            logs = Logs.objects.filter(user=request.user).last()
            description = "IP: " + logs.ip_address + "  " + " Location: " + logs.login_location
        else:
            description = "IP: " + "unknown" + "  " + " Location: " + "unknown"

        #Start Transaction Process
        transaction_object = NewTransaction(
            sender=request.user,
            reciever=request.user,
            transaction_code=21,
            amount=Decimal(amount),
            description=description,
            come_back_url=returnUrl,
            process_payattitude_id=new_request.id,
            phone = mobile
        )

        transaction_url = transaction_object.process_payattitude()

        if transaction_url != None:
            return HttpResponseRedirect(transaction_url)
        else:
            return HttpResponseRedirect(reverse("main:error"))

@csrf_exempt
def returnCardlessUrl(request, id):
    if request.method == "GET":
        messages.error(request, "Unable to process your transaction at the moment")
        return HttpResponseRedirect(reverse("main:error"))

    if request.method == "POST":
        status = request.POST['status']
        approved = request.POST['approved']
        trxID = request.POST['trxId']

        try:
            requested_cardless_process = ProcessPayattitudeRequest.objects.get(pk=id)
        except ProcessPayattitudeRequest.DoesNotExist:
            messages.error(request, "Transaction does not exist.")
            return HttpResponseRedirect(reverse("main:error"))

        rawdata = {}

        for key, value in request.POST.items():
            rawdata[key] = value

        requested_cardless_process.raw_data = rawdata
        requested_cardless_process.save()

        if int(requested_cardless_process.reference) == int(trxID):
            if approved == "true":
                requested_cardless_process.is_successful = True
                requested_cardless_process.status = status
                requested_cardless_process.save()
                #Update for cardless top up
                return HttpResponseRedirect(reverse("main:update_transaction", args=(requested_cardless_process.id, 2, )))
            else:
                requested_cardless_process.status = status
                requested_cardless_process.save()
                return HttpResponseRedirect(reverse("main:error"))

        messages.error(request, "Unable to match transaction reference")
        return HttpResponseRedirect(reverse("main:error"))

@login_required
def send(request):

    loggedin_user = request.user
    
    if request.method == "POST":

        recipient_wallet_address = request.POST['recipient-wallet-address']
        amount = request.POST['send-amount']

        amount = Decimal(amount)

        #Identifies the wallets sending 
        #1 = Individual, 2 = Business, 3 = Saving for both sender and reciever
        transaction_codes = {
            "sender": 0,
            "reciever": 0
        }

        try:
            sender_wallet = BusinessWallet.objects.get(user=loggedin_user)
            transaction_codes['sender'] = 2
        except BusinessWallet.DoesNotExist:
            messages.error(request, "Please select a wallet to debit")
            return HttpResponseRedirect(reverse("main:dashboard"))


        if sender_wallet.balance <= 0:
            messages.error(request, "Insufficient balance")
            return HttpResponseRedirect(reverse("main:dashboard"))

        if sender_wallet.balance < amount:
            messages.error(request, "Insufficient balance")
            return HttpResponseRedirect(reverse("main:dashboard"))

        if amount <= 100:
            messages.error(request, "Minimum amount is NGN 100")
            return HttpResponseRedirect(reverse("main:dashboard"))

        try:
            recipient_wallet = BusinessWallet.objects.get(address=recipient_wallet_address)
            transaction_codes['reciever'] = 2
        except BusinessWallet.DoesNotExist:
            messages.error(request, "Please enter a valid recipient wallet address")
            return HttpResponseRedirect(reverse("main:dashboard"))

        
        if transaction_codes['sender'] == 2 and transaction_codes['reciever'] == 2:
            transaction_code = 9
            send_transaction = NewTransaction(
                sender=sender_wallet.user,
                reciever=recipient_wallet.user,
                transaction_code=transaction_code,
                amount=amount,
                sender_business_wallet=sender_wallet,
                reciever_business_wallet=recipient_wallet,
                status_code=1,
                status="success"
            )
            trx_data = send_transaction.send_biz_to_biz()
            if trx_data:
                try:
                    wallet = BusinessWallet.objects.get(user=sender_wallet.user)
                    wallet.balance = wallet.balance - send_transaction.amount
                    wallet.save()
                except BusinessWallet.DoesNotExist:
                    #Handle Failed Debits
                    pass

                try:
                    wallet_to_recieve = BusinessWallet.objects.get(user=recipient_wallet.user)
                    wallet_to_recieve.balance = wallet_to_recieve.balance + (send_transaction.amount - trx_data.transaction_charges)
                    wallet_to_recieve.save()
                except BusinessWallet.DoesNotExist:
                    #Handle Failed Credits
                    pass

                #Send Email Notification to sender for debit
                sender_email_body = {
                    "sender": send_transaction.sender.first_name + " " + send_transaction.sender.last_name,
                    "reciever": send_transaction.reciever.first_name + " " + send_transaction.reciever.last_name,
                    "trx_id": trx_data.id,
                    "trx_date": trx_data.date,
                    "amount": send_transaction.amount,
                    "charges": trx_data.transaction_charges,
                    "reciever_wallet": recipient_wallet.address,
                    "recieve_amount": trx_data.amount - trx_data.transaction_charges,
                    "status": "successful",
                    "email_for": send_transaction.sender.first_name + " " + send_transaction.sender.last_name
                }

                n = EmailSender(
                    "Transaction Alert",
                    send_transaction.sender.email,
                    sender_email_body
                )

                n.email_sender()

                #Send Email Notification to reciever for alert
                reciever_email_body = {
                    "sender": send_transaction.sender.first_name + " " + send_transaction.sender.last_name,
                    "reciever": send_transaction.reciever.first_name + " " + send_transaction.reciever.last_name,
                    "trx_id": trx_data.id,
                    "trx_date": trx_data.date,
                    "amount": send_transaction.amount,
                    "charges": trx_data.transaction_charges,
                    "reciever_wallet": recipient_wallet.address,
                    "recieve_amount": trx_data.amount - trx_data.transaction_charges,
                    "status": "Successful",
                    "email_for": send_transaction.reciever.first_name + " " + send_transaction.reciever.last_name
                }

                j = EmailSender(
                    "Transaction Alert",
                    send_transaction.reciever.email,
                    reciever_email_body
                )

                j.email_reciever()
                
                messages.success(request, "Funds sent successfully")
                return HttpResponseRedirect(reverse("main:success"))
            else:
                messages.error(request, "Transaction Failed, Try again later")
                return HttpResponseRedirect(reverse("main:error"))


@login_required
def request_funds(request):

    loggedin_user = request.user
    
    if request.method == "POST":
        recipient = request.POST['request-recipient-wallet-address']
        amount = request.POST['request-amount']

        request_codes = {
            'sender': 0,
            'reciever': 0
        }

        #Check wallet type and try to get wallet
        try:
            recipient_wallet = BusinessWallet.objects.get(address=recipient)
            request_codes['reciever'] = 2
        except BusinessWallet.DoesNotExist:
            messages.error(request, "Please enter a valid recipient wallet")
            return HttpResponseRedirect(reverse("main:dashboard"))

        #Check wallet Existance
        if int(amount) >= 100:
            pass
        else:
            messages.error(request, "Minimum amount is NGN 100")
            return HttpResponseRedirect(reverse("main:dashboard"))

        #Sender wallet is business wallet
        try:
            sender_wallet = BusinessWallet.objects.get(user=loggedin_user)
            request_codes['sender'] = 2
        except BusinessWallet.DoesNotExist:
            messages.error(request, "Unable to get sending wallet, Please try again later")
            return HttpResponseRedirect(reverse("main:dashboard"))

        if request_codes['sender'] == 0 or request_codes['reciever'] == 0:
            messages.error(request, "Please enter a valid wallet address")
            return HttpResponseRedirect(reverse("main:dashboard"))

        elif request_codes['sender'] == 2 and request_codes['reciever'] == 2:
            transaction_code = 17
            send_request = NewTransaction(
                sender=loggedin_user,
                reciever=recipient_wallet.user,
                transaction_code=transaction_code,
                amount=Decimal(amount),
                sender_business_wallet=sender_wallet,
                reciever_business_wallet=recipient_wallet,
                status_code=1,
                status="Success"
            )
            request_data = send_request.request_biz_to_biz()
            if request_data:
                #Send email to request reciever 
                request_email_body = {
                    "sender": send_request.sender.first_name + " " + send_request.sender.last_name,
                    "reciever": send_request.reciever.first_name + " " + send_request.reciever.last_name,
                    "trx_date": request_data.date,
                    "amount": request_data.amount,
                    "reciever_wallet": sender_wallet.address,
                    "recieve_amount": request_data.amount,
                    "email_for": send_request.reciever.first_name + " " + send_request.reciever.last_name
                }

                n = EmailSender(
                    "Request Alert",
                    send_request.reciever.email,
                    request_email_body
                )

                n.email_request()
                messages.success(request, "Fund Request Sent Successfully")
                return HttpResponseRedirect(reverse("main:dashboard"))
            else:
                messages.error(request, "Unable to send your request at the moment, try again later")
                return HttpResponseRedirect(reverse("main:dashboard"))


        

        

        

