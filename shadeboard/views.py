from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from main.models import BusinessWallet, DeveloperInformation, Developer, ProcessCardRequest, ProcessPayattitudeRequest, Transaction, Recipt
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse

# Create your views here.

@login_required
def index(request):
    loggedin_user = request.user 
    try:
        wallet = BusinessWallet.objects.get(user=loggedin_user)
    except:
        return render(request, "shadeboard/index.html", {
        "balance": "Please Create a wallet to see balance",
        "address": "Please Create a wallet to see wallet address",
        "business_name": "Please Create a wallet to see business name",
        "business_address": "Please Create a wallet to see business address",
        "business_contact": "Please Create a wallet to see business contact"
        })
    
    try:
        dev = Developer.objects.get(wallet=wallet)
    except Developer.DoesNotExist:
        pass

    try: 
        dev_info = DeveloperInformation.objects.get(developer=dev)
    except DeveloperInformation.DoesNotExist:
        pass

    return render(request, "shadeboard/index.html", {
        "balance": wallet.balance,
        "address": wallet.address,
        "business_name": dev_info.business_name,
        "business_address": dev_info.business_address,
        "business_contact": dev_info.business_email + " | " + dev_info.business_phone,
        "int_key": dev.api_key,
        "payment_link": wallet.link
    })

@login_required
def apidetails(request):
    loggedin_user = request.user 
    try:
        wallet = BusinessWallet.objects.get(user=loggedin_user)
    except:
        pass
    
    try:
        dev = Developer.objects.get(wallet=wallet)
    except Developer.DoesNotExist:
        pass

    try: 
        dev_info = DeveloperInformation.objects.get(developer=dev)
    except DeveloperInformation.DoesNotExist:
        pass

    return render(request, "shadeboard/apidetails.html", {
        "dev": dev
    })


@login_required
def business_information(request):
    loggedin_user = request.user

    if request.method == "GET":
        dev_info = loggedin_user.business_wallet.get().developer_wallet_details.get().developer_details.get()
        biz_status = "Registered as a business" if loggedin_user.profile.get().is_business else "Not registered as a business, you can change to business any time you wish."

        return render(request, "shadeboard/business_information.html", {
            "details": dev_info,
            "biz_status": biz_status
        })

    if request.method == "POST":

        business_name = request.POST['business_name']
        business_phone = request.POST['business_phone']
        business_email = request.POST['business_email']
        business_status = request.POST['business_status']
        business_address = request.POST['business_address']
        business_nature = request.POST['business_nature']

        if business_name == "" or business_phone == "" or business_email == "" or business_status == "" or business_address == "" or business_nature == "":
            messages.error(request, "Please fill in the information to update")
            return HttpResponseRedirect(reverse("shadeboard:business-information"))

        dev_info = loggedin_user.business_wallet.get().developer_wallet_details.get().developer_details.get()

        dev_info.business_name = business_name
        dev_info.business_phone = business_phone
        dev_info.business_address = business_address
        dev_info.business_email = business_email
        dev_info.business_nature = business_nature
        dev_info.save()

        add_info = loggedin_user.profile.get()
        add_info.is_business = True if bool(business_status) else False
        add_info.save()

        return HttpResponseRedirect(reverse("shadeboard:business-information"))