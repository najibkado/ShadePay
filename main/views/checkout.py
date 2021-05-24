from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from main.models import BusinessWallet, Developer, DeveloperInformation, ProcessCardRequest, CheckoutLog
from api.models import MerchantRequest, ShadepayRequest
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.db import IntegrityError
from main.utils import get_domain
from main.transaction import Transaction as NewTransaction
from main.utils import get_client, get_ip, get_geol
from geopy.geocoders import Nominatim
import requests
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, authenticate, logout
import decimal
from main.email import EmailSender


geolocator = Nominatim(user_agent="shadepay")

def card_checkout(request, id):
    if request.method == "GET":
        try:
            merchant_request = MerchantRequest.objects.get(pk=id)
        except MerchantRequest.DoesNotExist:
            return HttpResponseRedirect(reverse("main:error"))

        try:
            wallet = BusinessWallet.objects.get(address=merchant_request.wallet)
        except BusinessWallet.DoesNotExist:
            data = {
                "request_id": merchant_request.id,
                "error": "invalid merchant wallet address"
            }
            response = requests.post(merchant_request.returnUrl, data=data)
            return HttpResponseRedirect(merchant_request.returnUrl)

        try: 
            developer = Developer.objects.get(wallet=wallet)
        except Developer.DoesNotExist:
            return HttpResponseRedirect(reverse("main:error"))

        try:
            developer_info = DeveloperInformation.objects.get(developer=developer)
        except DeveloperInformation.DoesNotExist:
            return HttpResponseRedirect(reverse("main:error"))   

        if merchant_request.isProcessed:
            return HttpResponseRedirect(reverse("main:notfound", args=("finished transaction", ))) 

        return render(request, "main/card_checkout.html", {
            "merchant": developer_info.business_name,
            "reqid": id,
            "tr_request": merchant_request
        })

    if request.method == "POST":

        card = request.POST['card-num']
        month = request.POST['exp-month']
        year = request.POST['exp-year']
        cvv = request.POST['cvv']

        if len(card) == 16:
            if card.isalnum:
                pass
            else:
                messages.error(request, "Please Enter a valid card details") 
                return HttpResponseRedirect(reverse("main:card_checkout", args=(id, )))
        else:
           messages.error(request, "Please Enter a valid card details") 
           return HttpResponseRedirect(reverse("main:card_checkout", args=(id, )))
            
        if month.isalnum:
            if int(month) > 31 or int(month) < 1:
                messages.error(request, "Please Enter a valid card details") 
                return HttpResponseRedirect(reverse("main:card_checkout", args=(id, )))
            else:
                pass
        else:
           messages.error(request, "Please Enter a valid card details") 
           return HttpResponseRedirect(reverse("main:card_checkout", args=(id, )))

        if len(year) == 4:
            if year.isalnum:
                year = year[2:]
            else:
                messages.error(request, "Please Enter a valid card details") 
                return HttpResponseRedirect(reverse("main:card_checkout", args=(id, )))
        else:
           messages.error(request, "Please Enter a valid card details") 
           return HttpResponseRedirect(reverse("main:card_checkout", args=(id, )))

        if cvv.isalnum:
            pass
        else:
           messages.error(request, "Please Enter a valid card details") 
           return HttpResponseRedirect(reverse("main:card_checkout", args=(id, )))


        try:
            merchant_request = MerchantRequest.objects.get(pk=id)
        except MerchantRequest.DoesNotExist:
            return HttpResponseRedirect(reverse("main:error"))

        try:
            wallet = BusinessWallet.objects.get(address=merchant_request.wallet)
        except BusinessWallet.DoesNotExist:
            return HttpResponseRedirect(reverse("main:error"))

        try: 
            developer = Developer.objects.get(wallet=wallet)
        except Developer.DoesNotExist:
            return HttpResponseRedirect(reverse("main:error"))

        try:
            developer_info = DeveloperInformation.objects.get(developer=developer)
        except DeveloperInformation.DoesNotExist:
            return HttpResponseRedirect(reverse("main:error"))   


        try:
            new_request = ProcessCardRequest(
                user = wallet.user,
                amount = merchant_request.amount,
                card_first_six = card[0:7],
                card_last_four = card[-4:0],
                card_type = 'visa',
                business_wallet = wallet,
                transaction_code = 25,
                reference = "",
                merchant_request = merchant_request
            )
            new_request.save()
        except IntegrityError:
            #TODO: Return Merchant Error
            print("Error processing your transaction")
            return HttpResponseRedirect("error")

        exp = month + "/" + year
        domain = get_domain(request)
        returnUrl = domain + f"/topup/return/{new_request.id}"

        ip = get_ip(request)
        lon, lat, city, country = get_geol(ip)
        client = get_client(request)

        try:
            location = geolocator.geocode(city)
        except:
            location = "unknown"

        try:
            checkout_log = CheckoutLog(
                merchant=new_request.business_wallet,
                ip_address=ip,
                checkout_location=location,
                lon=lon,
                lat=lat,
                client_device=client
            )
            checkout_log.save()
        except IntegrityError:
            checkout_log = CheckoutLog(
                merchant=new_request.business_wallet,
                ip_address="unknown",
                checkout_location="unknown",
                lon="unknown",
                lat="unknown",
                client_device=client
            )
            checkout_log.save()


        description = "IP: " + checkout_log.ip_address + "  " + " Location: " + checkout_log.checkout_location

        #Start Transaction Process
        transaction_object = NewTransaction(
            sender=new_request.user,
            reciever=new_request.user,
            transaction_code=25,
            amount=new_request.amount,
            description=description,
            come_back_url=returnUrl,
            sender_card=card,
            sender_card_expiry=exp,
            sender_card_cvv=cvv,
            scheme=new_request.card_type,
            process_card_id=new_request.id
        )

        transaction_url = transaction_object.process_card()

        merchant_request.isProcessed = True
        merchant_request.save()

        if transaction_url != None:
            return HttpResponseRedirect(transaction_url)
        else:
            return HttpResponseRedirect(reverse("main:error"))

def shadepay_checkout(request, id):
    
    if request.method == "GET":

        if request.user.is_authenticated:
            logout(request)

        try:
            shadepay_request = ShadepayRequest.objects.get(pk=id)
        except ShadepayRequest.DoesNotExist:
            messages.error(request, "Invalid request")
            return HttpResponseRedirect(reverse("main:error"))

        try:
            wallet = BusinessWallet.objects.get(address=shadepay_request.wallet)
        except BusinessWallet.DoesNotExist:
            data = {
                "request_id": shadepay_request.id,
                "unsuccessful": True,
                "error": "invalid merchant wallet address"
            }
            requests.post(shadepay_request.returnUrl, data=data)
            return HttpResponseRedirect(shadepay_request.returnUrl)

        if shadepay_request.isProcessed:
            messages.error(request, "Finished transaction")
            return HttpResponseRedirect(reverse("main:notfound", args=("finished transaction", ))) 

        return render(request, "main/shadepay_checkout.html", {
            "r": shadepay_request.id
        })

    
    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
            
        if user:
            login(request, user)
            return HttpResponseRedirect(reverse("main:confirm-shadepayment", args=(id, )))

        else:
            messages.error(request, "Invalid user details")
            return HttpResponseRedirect(reverse("main:shadepay_checkout", args=(id, )))


@login_required
def confirm_shadepayment(request, id):

    loggedin_user = request.user
    
    if request.method == "GET":

        try:
            shadepay_request = ShadepayRequest.objects.get(pk=id)
        except ShadepayRequest.DoesNotExist:
            pass

        try:
            wallet = BusinessWallet.objects.get(address=shadepay_request.wallet)
        except BusinessWallet.DoesNotExist:
            data = {
                "request_id": shadepay_request.id,
                "unsuccessful": True,
                "error": "invalid merchant wallet address"
            }
            response = requests.post(shadepay_request.returnUrl, data=data)
            return HttpResponseRedirect(shadepay_request.returnUrl)

        try: 
            developer = Developer.objects.get(wallet=wallet)
        except Developer.DoesNotExist:
            return HttpResponseRedirect(reverse("main:error"))

        try:
            developer_info = DeveloperInformation.objects.get(developer=developer)
        except DeveloperInformation.DoesNotExist:
            return HttpResponseRedirect(reverse("main:error"))  

        if shadepay_request.isProcessed:
            messages.error(request, "Finished transaction")
            return HttpResponseRedirect(reverse("main:notfound", args=("finished transaction", ))) 

        return render(request, "main/confirm_payment.html", {
            "merchant": developer_info,
            "payment": shadepay_request,
            "buyer": loggedin_user
        })

    if request.method == "POST":

        try:
            shadepay_request = ShadepayRequest.objects.get(pk=id)
        except ShadepayRequest.DoesNotExist:
            pass

        try:
            wallet = BusinessWallet.objects.get(address=shadepay_request.wallet)
        except BusinessWallet.DoesNotExist:
            data = {
                "request_id": shadepay_request.id,
                "unsuccessful": True,
                "error": "invalid merchant wallet address"
            }
            response = requests.post(shadepay_request.returnUrl, data=data)
            return HttpResponseRedirect(shadepay_request.returnUrl)

        try:
            buyer_wallet = BusinessWallet.objects.get(user=loggedin_user)
        except BusinessWallet.DoesNotExist:
            data = {
                "request_id": shadepay_request.id,
                "error": "Unable to process transaction"
            }
            response = requests.post(shadepay_request.returnUrl, data=data)
            return HttpResponseRedirect(shadepay_request.returnUrl)

        if buyer_wallet.balance >= decimal.Decimal(shadepay_request.amount):
            

            #Start Transaction Process
            transaction_object = NewTransaction(
                sender=loggedin_user,
                reciever=wallet.user,
                transaction_code=10,
                amount=decimal.Decimal(shadepay_request.amount),
                description=shadepay_request.products_description,
                sender_business_wallet=buyer_wallet,
                reciever_business_wallet=wallet,
                come_back_url=shadepay_request.returnUrl,
                status_code=1,
                status="success",
                ref=shadepay_request.id
            )

            trxObj = transaction_object.send_biz_to_biz()

            if trxObj:
                
                #Debit and update buyer
                buyer_wallet.balance = buyer_wallet.balance - transaction_object.amount
                buyer_wallet.save()

                #Credit and update seller
                wallet.balance = wallet.balance + (transaction_object.amount - trxObj.transaction_charges)
                wallet.save()

                shadepay_request.isProcessed = True
                shadepay_request.save()

                #Email both parties
                #Send Email Notification to sender for debit
                sender_email_body = {
                    "sender": transaction_object.sender.first_name + " " + transaction_object.sender.last_name,
                    "reciever": transaction_object.reciever.first_name + " " + transaction_object.reciever.last_name,
                    "trx_id": trxObj.id,
                    "trx_date": trxObj.date,
                    "amount": transaction_object.amount,
                    "charges": trxObj.transaction_charges,
                    "reciever_wallet": wallet.address,
                    "recieve_amount": trxObj.amount - trxObj.transaction_charges,
                    "status": "successful",
                    "email_for": transaction_object.sender.first_name + " " + transaction_object.sender.last_name
                }

                n = EmailSender(
                    "Payment Alert",
                    transaction_object.sender.email,
                    sender_email_body
                )

                n.email_sender()

                #Send Email Notification to reciever for alert
                reciever_email_body = {
                    "sender": transaction_object.sender.first_name + " " + transaction_object.sender.last_name,
                    "reciever": transaction_object.reciever.first_name + " " + transaction_object.reciever.last_name,
                    "trx_id": trxObj.id,
                    "trx_date": trxObj.date,
                    "amount": transaction_object.amount,
                    "charges": trxObj.transaction_charges,
                    "reciever_wallet": wallet.address,
                    "recieve_amount": trxObj.amount - trxObj.transaction_charges,
                    "status": "Successful",
                    "email_for": transaction_object.reciever.first_name + " " + transaction_object.reciever.last_name
                }

                j = EmailSender(
                    "Payment Alert",
                    transaction_object.reciever.email,
                    reciever_email_body
                )

                j.email_reciever()

                data = {
                "transaction_id": trxObj.id,
                "request_id": shadepay_request.id,
                "successful": True,
                "message": "Transaction successful"
                }

                requests.post(shadepay_request.returnUrl, data=data)

                return HttpResponseRedirect(shadepay_request.returnUrl)

            else:

                shadepay_request.isProcessed = True
                shadepay_request.save()

                data = {
                "request_id": shadepay_request.id,
                "unsuccessful": True,
                "error": "Unable to process your payment, wrong client input"
                }
                response = requests.post(shadepay_request.returnUrl, data=data)
                return HttpResponseRedirect(shadepay_request.returnUrl)

        else:

            shadepay_request.isProcessed = True
            shadepay_request.save()

            data = {
                "request_id": shadepay_request.id,
                "unsuccessful": True,
                "error": "Customer has insufficient balance"
            }
            response = requests.post(shadepay_request.returnUrl, data=data)
            return HttpResponseRedirect(shadepay_request.returnUrl)


#To be deleted
#Done for test purposes, however test server is down.
#Try again later and get rid of this code below!
@csrf_exempt
def test(request):
    
    if request.method == "GET":
        return HttpResponse("Hello there")

    if request.method == "POST":

        for key, value in request.POST.items():
            print(key, value, sep="---->")

        return HttpResponse("Hello There")


    