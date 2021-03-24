from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from main.models import IndividualWallet, AdditionalInformation, BusinessWallet, SavingWallet, Developer, DeveloperInformation
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
def create_wallet(request):

    loggedin_user = request.user

    if request.method == "GET":
        try:
            info = AdditionalInformation.objects.get(user = loggedin_user)
            if loggedin_user.is_active:
                
                #Check for Individual Wallet
                try:
                    individual_wallet = IndividualWallet.objects.get(user=loggedin_user)
                except IndividualWallet.DoesNotExist:
                    individual_wallet = None

                #Check for Saving Wallet
                try:
                    saving_wallet = SavingWallet.objects.get(user=loggedin_user)
                except SavingWallet.DoesNotExist:
                    saving_wallet = None

                #Check for Business Wallet
                try:
                    business_wallet = BusinessWallet.objects.get(user=loggedin_user)
                except BusinessWallet.DoesNotExist:
                    business_wallet = None

                #Check for availability
                if individual_wallet is not None and saving_wallet is not None and business_wallet is not None:
                    status = 1
                elif individual_wallet is not None and saving_wallet is None and business_wallet is None:
                    status = 2
                elif individual_wallet is not None and saving_wallet is not None and business_wallet is None:
                    status = 3
                elif individual_wallet is not None and business_wallet is not None and saving_wallet is None:
                    status = 4
                elif business_wallet is not None and saving_wallet is None and individual_wallet is None:
                    status = 5
                elif business_wallet is not None and saving_wallet is not None and individual_wallet is None:
                    status = 6
                else:
                    status = 0
                    
            else:
                messages.info(request, "Verify your email address please")
                return HttpResponseRedirect(reverse("unverified"))
        except AdditionalInformation.DoesNotExist:
            messages.warning(request, 'Additional Information required before you can create a wallet ')
            return HttpResponseRedirect(reverse("additional_information"))

        return render(request, "main/new_wallet.html", {"status": status})

    if request.method == "POST":
        
        wallet_type = request.POST["wallet-type"]

        try:
            info = AdditionalInformation.objects.get(user = loggedin_user)
            if loggedin_user.is_active:
                pass
            else:
                return HttpResponseRedirect(reverse("unverified"))
        except AdditionalInformation.DoesNotExist:
            return HttpResponseRedirect(reverse("additional_information"))

        domain = get_domain(request)

        if wallet_type == "001":
            
            try:
                wallet = IndividualWallet.objects.get(user = loggedin_user)
                messages.warning(request, "You cannot create individual wallet twice")
                return HttpResponseRedirect(reverse("dashboard"))
            except IndividualWallet.DoesNotExist:
                try:
                    wallet = IndividualWallet(
                        user = loggedin_user,
                        address = loggedin_user.username + ".siw",
                        link = domain + f"/pay/{loggedin_user.username}.siw",
                        balance = 0.00,
                    )
                    wallet.save()
                except IntegrityError:
                    messages.error(request, "Unable to create individual wallet, Please try again later")
                    return HttpResponseRedirect(reverse("dashboard"))
                messages.success(request, "Individual wallet created successfully")
                return HttpResponseRedirect(reverse("dashboard"))

        elif wallet_type == "002":
            
            try:
                wallet = SavingWallet.objects.get(user = loggedin_user)
                messages.warning(request, "You cannot create saving wallet twice")
                return HttpResponseRedirect(reverse("dashboard"))
            except SavingWallet.DoesNotExist:
                try:
                    wallet = SavingWallet(
                        user = loggedin_user,
                        address = loggedin_user.username + ".ssw",
                        link = domain + f"/pay/{loggedin_user.username}.ssw",
                        balance = 0.00,
                    )
                    wallet.save()
                except IntegrityError:
                    messages.error(request, "Unable to create saving wallet, Please try again later")
                    return HttpResponseRedirect(reverse("dashboard"))
                messages.success(request, "Saving wallet created successfully")
                return HttpResponseRedirect(reverse("dashboard"))

        elif wallet_type == "003":
            
           return HttpResponseRedirect(reverse("create-business-wallet"))

@login_required
def create_business_wallet(request):
    loggedin_user = request.user

    domain = get_domain(request)

    if request.method == "GET":
        try:
            wallet = BusinessWallet.objects.get(user = loggedin_user)
        except BusinessWallet.DoesNotExist:
            wallet = None

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
                return HttpResponseRedirect(reverse("dashboard"))

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
            return HttpResponseRedirect(reverse("create-business-wallet"))

        if b_name is "" or b_email is "" or b_phone is "" or b_addr is "":
            messages.warning(request, "Fields can't be empty, Please fill the fields and try again")
            return HttpResponseRedirect(reverse("create-business-wallet"))


        business_wallet_address = b_name
        business_wallet_address.strip()
        business_wallet_address = business_wallet_address.replace(" ", "")

        if b_agreement is None:
            messages.warning(request, "You have to read and agree to our terms of services")
            return HttpResponseRedirect(reverse("create-business-wallet"))

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
                return HttpResponseRedirect(reverse("create-business-wallet"))

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
            return HttpResponseRedirect(reverse("dashboard"))

        #TODO: Card Last Four Check

def wallets_view(request):
    """
    This returns the page that displays information about wallets
    """
    return render(request, "main/wallets.html")



