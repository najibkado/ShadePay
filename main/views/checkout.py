from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from main.models import BusinessWallet, Developer, DeveloperInformation, ProcessCardRequest, CheckoutLog
from api.models import MerchantRequest
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.db import IntegrityError
from main.utils import get_domain
from main.transaction import Transaction as NewTransaction
from main.utils import get_client, get_ip, get_geol
from geopy.geocoders import Nominatim


geolocator = Nominatim(user_agent="shadepay")

def card_checkout(request, id):
    if request.method == "GET":
        try:
            merchant_request = MerchantRequest.objects.get(pk=id)
        except MerchantRequest.DoesNotExist:
            return HttpResponseRedirect(reverse("error"))

        try:
            wallet = BusinessWallet.objects.get(address=merchant_request.wallet)
        except BusinessWallet.DoesNotExist:
            return HttpResponseRedirect(reverse("error"))

        try: 
            developer = Developer.objects.get(wallet=wallet)
        except Developer.DoesNotExist:
            return HttpResponseRedirect(reverse("error"))

        try:
            developer_info = DeveloperInformation.objects.get(developer=developer)
        except DeveloperInformation.DoesNotExist:
            return HttpResponseRedirect(reverse("error"))   

        if merchant_request.isProcessed:
            return HttpResponseRedirect(reverse("notfound", args=("finished transaction", ))) 

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
                return HttpResponseRedirect(reverse("card_checkout", args=(id, )))
        else:
           messages.error(request, "Please Enter a valid card details") 
           return HttpResponseRedirect(reverse("card_checkout", args=(id, )))
            
        if month.isalnum:
            if int(month) > 31 or int(month) < 1:
                messages.error(request, "Please Enter a valid card details") 
                return HttpResponseRedirect(reverse("card_checkout", args=(id, )))
            else:
                pass
        else:
           messages.error(request, "Please Enter a valid card details") 
           return HttpResponseRedirect(reverse("card_checkout", args=(id, )))

        if len(year) == 4:
            if year.isalnum:
                year = year[2:]
            else:
                messages.error(request, "Please Enter a valid card details") 
                return HttpResponseRedirect(reverse("card_checkout", args=(id, )))
        else:
           messages.error(request, "Please Enter a valid card details") 
           return HttpResponseRedirect(reverse("card_checkout", args=(id, )))

        if cvv.isalnum:
            pass
        else:
           messages.error(request, "Please Enter a valid card details") 
           return HttpResponseRedirect(reverse("card_checkout", args=(id, )))


        try:
            merchant_request = MerchantRequest.objects.get(pk=id)
        except MerchantRequest.DoesNotExist:
            return HttpResponseRedirect(reverse("error"))

        try:
            wallet = BusinessWallet.objects.get(address=merchant_request.wallet)
        except BusinessWallet.DoesNotExist:
            return HttpResponseRedirect(reverse("error"))

        try: 
            developer = Developer.objects.get(wallet=wallet)
        except Developer.DoesNotExist:
            return HttpResponseRedirect(reverse("error"))

        try:
            developer_info = DeveloperInformation.objects.get(developer=developer)
        except DeveloperInformation.DoesNotExist:
            return HttpResponseRedirect(reverse("error"))   


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
            return HttpResponseRedirect(reverse("error"))

