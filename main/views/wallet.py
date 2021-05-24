from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from main.models import AdditionalInformation, BusinessWallet, Developer, DeveloperInformation
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
import jwt 
from django.conf import settings
import hashlib
from django.db import IntegrityError 
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from main.utils import get_domain

"""
Wallet Codes
------------
001 = Individual Wallet
002 = Saving Wallet
003 = Business Wallet
004 = Fund Me Wallet
005 = Hand in Hand Wallet
"""

"""
API Auth Codes
--------------
1 = Internal operations
2 = External operations
"""

@login_required
def create_business_wallet(request):
    loggedin_user = request.user

    domain = get_domain(request)

    if request.method == "GET":
        try:
            wallet = BusinessWallet.objects.get(user = loggedin_user)
        except BusinessWallet.DoesNotExist:
            wallet = None

        try:
            info = AdditionalInformation.objects.get(user = loggedin_user)
        except AdditionalInformation.DoesNotExist:
            messages.error(request, "Information does not exist, please try creating a new wallet")
            return HttpResponseRedirect(reverse("main:dashboard"))

        if info.is_business:
            pass
        else:
            #Create new wallet without filling business information if user is not a business owner
            try:
                nwallet = BusinessWallet(
                            user = loggedin_user,
                            address = loggedin_user.username + ".sbw",
                            link = domain + f"/pay/{loggedin_user.username}.sbw",
                            balance = 0.00
                        )
                nwallet.save()
            except IntegrityError:
                messages.error(request, "Unable to create your wallet at the moment, please try again later")
                return HttpResponseRedirect(reverse("main:dashboard"))

            api_key_generator_string = f"{nwallet.user.username} {nwallet.address}"
            api_key_generator = hashlib.sha256()
            api_key_generator.update(bytes(api_key_generator_string, encoding='utf-8'))
            api_key = api_key_generator.hexdigest()
            encoded = jwt.encode({"code": 2,"username": nwallet.user.username,"api_key": api_key}, settings.SECRET_KEY, algorithm="HS256")

            dev_profile = Developer(
                api_key = api_key,
                secrete_key = encoded,
                wallet = nwallet,
            )
            dev_profile.save()

            dev_information  = DeveloperInformation(
                developer = dev_profile,
                business_name = loggedin_user.first_name + " " + loggedin_user.last_name,
                business_address = info.shipping_address,
                business_phone = info.mobile,
                business_email = loggedin_user.email,
                business_nature = "Not a business"
            )
            dev_information.save()
            messages.success(request, "Wallet successfully created")
            return HttpResponseRedirect(reverse("main:dashboard"))



        if wallet is not None:
            try:
                developer = Developer.objects.get(wallet=wallet)
            except Developer.DoesNotExist:
                developer = None

            if developer is not None:
                try:
                    developer_information = DeveloperInformation.objects.get(developer=developer)
                except DeveloperInformation.DoesNotExist:
                    developer_information = None
                messages.info(request, "Business wallet exist.")
                return HttpResponseRedirect(reverse("main:dashboard"))

        return render(request, "main/developerInfo.html")

    if request.method == "POST":
        
        b_name = request.POST['b-name']
        b_email = request.POST['b-email']
        b_phone = request.POST['b-phone']
        b_addr = request.POST['b-addr']
        b_nature = request.POST['b-nature']
        b_agreement = request.POST.get('agree')

        try:
            validate_email(b_email)
        except ValidationError:
            messages.error(request, "Please use a valid email address")
            return HttpResponseRedirect(reverse("main:create-business-wallet"))

        if b_name is "" or b_email is "" or b_phone is "" or b_addr is "":
            messages.warning(request, "Fields can't be empty, Please fill the fields and try again")
            return HttpResponseRedirect(reverse("main:create-business-wallet"))


        business_wallet_address = b_name
        business_wallet_address.strip()
        business_wallet_address = business_wallet_address.replace(" ", "")

        if b_agreement is None:
            messages.warning(request, "You have to read and agree to our terms of services")
            return HttpResponseRedirect(reverse("main:create-business-wallet"))

        try:
            business_wallet = BusinessWallet.objects.get(user=loggedin_user)
            messages.warning(request, "You can't have multiple business wallets!")
            #TODO: Check existance of Developer details and Developer Information
        except BusinessWallet.DoesNotExist:

            try:
                wallet = BusinessWallet(
                        user = loggedin_user,
                        address = business_wallet_address + ".sbw",
                        link = domain + f"/pay/{business_wallet_address}.sbw",
                        balance = 0.00
                    )
                wallet.save()
            except IntegrityError:
                messages.error(request, "Unabble to create business wallet, Please try again later")
                return HttpResponseRedirect(reverse("main:create-business-wallet"))

            api_key_generator_string = f"{wallet.user.username} {wallet.address}"
            api_key_generator = hashlib.sha256()
            api_key_generator.update(bytes(api_key_generator_string, encoding='utf-8'))
            api_key = api_key_generator.hexdigest()
            encoded = jwt.encode({"code": 2,"username": wallet.user.username,"api_key": api_key}, settings.SECRET_KEY, algorithm="HS256")

            dev_profile = Developer(
                api_key = api_key,
                secrete_key = encoded,
                wallet = wallet,
            )
            dev_profile.save()

            dev_information  = DeveloperInformation(
                developer = dev_profile,
                business_name = b_name,
                business_address = b_addr,
                business_phone = b_phone,
                business_email = b_email,
                business_nature = b_nature
            )
            dev_information.save()
            messages.success(request, "Business wallet successfully created")
            return HttpResponseRedirect(reverse("main:dashboard"))

        #TODO: Card Last Four Check



