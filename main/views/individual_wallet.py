from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from main.models import IndividualWallet, SavingWallet, BusinessWallet


@login_required
def individual_wallet(request):
    loggedin_user = request.user 

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

    try:
        wallet = IndividualWallet.objects.get(user=loggedin_user)
    except IndividualWallet.DoesNotExist:
        pass

    return render(request, "main/individual_wallet.html", {
        "address": wallet.address,
        "name": loggedin_user.first_name + " " + loggedin_user.last_name,
        "balance": wallet.balance,
        "status": status
    })