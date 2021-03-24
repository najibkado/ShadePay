from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from main.models import AdditionalInformation, IndividualWallet, BusinessWallet, SavingWallet
from main.utils import validate
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse

@login_required
def profile_view(request):
    loggedin_user = request.user 

    #Geting Initials to display
    initials = loggedin_user.first_name[0].upper() if len(loggedin_user.first_name) > 0 else loggedin_user.username[0].upper()
    initials = initials + loggedin_user.last_name[0].upper() if len(loggedin_user.last_name) > 0 else initials

    #Get name to display
    name = loggedin_user.first_name + " " + loggedin_user.last_name
    username = loggedin_user.username
    email = loggedin_user.email
    activation_status = "Active" if loggedin_user.is_active else "Deactivated"

    #Get user additional informantion
    try:
        additional_information = AdditionalInformation.objects.get(user=loggedin_user)
    except AdditionalInformation.DoesNotExist:
        additional_information = None

    if additional_information is not None:
        address = additional_information.shipping_address
        mobile = additional_information.mobile
        billing_address = additional_information.billing_address
        nin = additional_information.nin
        is_nin_verified = "Verified" if additional_information.is_verified else "Not Verified"
    else:
        address = ""
        mobile = ""
        billing_address = ""
        nin = ""
        is_nin_verified = ""

    #Get user individual wallet if available
    try:
        individual_wallet = IndividualWallet.objects.get(user=loggedin_user)
        individual_wallet = individual_wallet.address
    except IndividualWallet.DoesNotExist:
        individual_wallet = None

    #Get user business wallet if available
    try:
        business_wallet = BusinessWallet.objects.get(user=loggedin_user)
        business_wallet = business_wallet.address
    except BusinessWallet.DoesNotExist:
        business_wallet = None

    #Get user saving wallet
    try:
        saving_wallet = SavingWallet.objects.get(user=loggedin_user)
        saving_wallet = saving_wallet.address
    except SavingWallet.DoesNotExist:
        saving_wallet = None

    #Check wallet exixtance status
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

    return render(request, "main/profile.html", {
        "initials": initials,
        "name": name,
        "username": username,
        "address": address,
        "individual_wallet": individual_wallet,
        "business_wallet": business_wallet,
        "saving_wallet": saving_wallet,
        "mobile": mobile,
        "email": email,
        "billing_address": billing_address,
        "activation_status": activation_status,
        "nin": nin,
        "is_nin_verified": is_nin_verified,
        "status": status
    })

@login_required
def update_profile(request, id):
    loggedin_user= request.user

    if request.method == "GET":
        if id == "1":
            try:
                info = AdditionalInformation.objects.get(user=loggedin_user)
            except AdditionalInformation.DoesNotExist:
                info = None

            if info is not None:
                context = {
                    "id": id,
                    "email": loggedin_user.email,
                    "mobile": info.mobile
                }
            else:
                context = {
                    "id": id,
                    "email": loggedin_user.email
                }

        elif id == "2":
            try:
                info = AdditionalInformation.objects.get(user=loggedin_user)
            except AdditionalInformation.DoesNotExist:
                info = None

            if info is not None:
                context = {
                    "id": id,
                    "billing": info.billing_address,
                    "shipping": info.shipping_address
                }
            else:
                return HttpResponseRedirect(reverse("additional_information"))

        elif id == "3":
            try:
                info = AdditionalInformation.objects.get(user=loggedin_user)
            except AdditionalInformation.DoesNotExist:
                info = None

            if info is not None:
                context = {
                    "id": id,
                    "nin": info.nin
                }
            else:
                return HttpResponseRedirect(reverse("additional_information"))

        else:
            return HttpResponseRedirect(reverse("profile"))

        return render(request, "main/update_profile.html", context)

    if request.method == "POST":

        #Check if user want to update contact details
        if id == "1":
            
            phone = request.POST['phone']
            email = request.POST['email']

            if validate(email):

                loggedin_user.email = email
                loggedin_user.save()

                try:
                    info = AdditionalInformation.objects.get(user=loggedin_user)
                    info.mobile = phone
                    info.save()
                except AdditionalInformation.DoesNotExist:
                    return HttpResponseRedirect(reverse("additional_information"))

            else:
                messages.error(request, "Please enter a valid email")
                return HttpResponseRedirect(reverse("update-profile", args=(id, )))

            messages.success(request, "Contact updated successfully")
            return HttpResponseRedirect(reverse("profile"))

        if id == "2":

            billing = request.POST['billing']
            shipping = request.POST['shipping']

            if billing == "" or shipping == "":
                messages.error(request, "Please enter a correct address")
                return HttpResponseRedirect(reverse("update-profile", args=(id, )))

            try:
                info = AdditionalInformation.objects.get(user=loggedin_user)
                info.billing_address = billing
                info.shipping_address = shipping
                info.save()
            except AdditionalInformation.DoesNotExist:
                return HttpResponseRedirect(reverse("additional_information"))

            messages.success(request, "Billing information updated successfully")
            return HttpResponseRedirect(reverse("profile"))

        if id == "3":

            nin = request.POST['nin']

            if nin == "":
                messages.error(request, "Please enter a National ID Number")
                return HttpResponseRedirect(reverse("update-profile", args=(id, )))

            try:
                info = AdditionalInformation.objects.get(user=loggedin_user)
                info.nin = nin
                info.save()
            except AdditionalInformation.DoesNotExist:
                return HttpResponseRedirect(reverse("additional_information"))

            messages.success(request, "National ID updated successfully")
            return HttpResponseRedirect(reverse("profile"))


@login_required
def deactivate_account(request):
    loggedin_user = request.user

    if request.method == "POST":
        username = request.POST['username']

        if loggedin_user.username == username:

            try:
                info = AdditionalInformation.objects.get(user=loggedin_user)
                info.is_deleted = True
                info.save()
            except AdditionalInformation.DoesNotExist:
                pass

            loggedin_user.is_active = False
            loggedin_user.save()

            return HttpResponseRedirect(reverse("index"))







