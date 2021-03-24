from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from main.models import BusinessWallet, DeveloperInformation, Developer, ProcessCardRequest, ProcessPayattitudeRequest, Transaction, Recipt

# Create your views here.

@login_required
def index(request):
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

    return render(request, "shadeboard/index.html", {
        "balance": wallet.balance,
        "address": wallet.address,
        "business_name": dev_info.business_name,
        "business_address": dev_info.business_address,
        "business_contact": dev_info.business_email + " | " + dev_info.business_phone

    })

@login_required
def admin(request):
    loggedin_user = request.user

    if loggedin_user.is_staff:
        return render(request, "shadeboard/admin/admin.html")

@login_required
def card_requests(request):
    loggedin_user = request.user

    all_requests = ProcessCardRequest.objects.all()
    all_requests = reversed(all_requests)

    if loggedin_user.is_staff:
        return render(request, "shadeboard/admin/card_requests.html", {
            "all_requests": all_requests
        })

@login_required
def cardless_requests(request):
    loggedin_user = request.user

    if loggedin_user.is_staff:

        all_requests = ProcessPayattitudeRequest.objects.all()
        all_requests = reversed(all_requests)

        return render(request, "shadeboard/admin/cardless_requests.html", {
             "all_requests": all_requests
        })


@login_required
def card_request(request, id):
    loggedin_user = request.user

    if loggedin_user.is_staff:

        try:
            transaction = ProcessCardRequest.objects.get(pk=id)
        except ProcessCardRequest.DoesNotExist:
            pass

        return render(request, "shadeboard/admin/request_details.html", {
            "transaction": transaction
        })

@login_required
def cardless_request(request, id):
    loggedin_user = request.user

    if loggedin_user.is_staff:

        try:
            transaction = ProcessPayattitudeRequest.objects.get(pk=id)
        except ProcessCardRequest.DoesNotExist:
            pass

        return render(request, "shadeboard/admin/request_details.html", {
            "transaction": transaction
        })

@login_required
def recipts(request):
    loggedin_user = request.user

    if loggedin_user.is_staff:

        try:
            recipts = Recipt.objects.all()
        except Recipt.DoesNotExist:
            pass

        recipts = reversed(recipts)

        return render(request, "shadeboard/admin/recipts.html", {
            "recipts": recipts
        })

@login_required
def recipt(request, id):
    loggedin_user = request.user

    if loggedin_user.is_staff:

        try:
            recipt = Recipt.objects.get(pk=id)
        except Recipt.DoesNotExist:
            recipt = ""

        return render(request, "shadeboard/admin/recipt.html", {
            "recipt": recipt
        })

@login_required
def card_request_reference(request, id):
    loggedin_user = request.user

    if loggedin_user.is_staff:

        try:
            transaction = ProcessCardRequest.objects.get(pk=id)
        except ProcessCardRequest.DoesNotExist:
            pass

        try:
            s_transaction = Transaction.objects.get(reference=transaction.reference)
        except Transaction.DoesNotExist:
            s_transaction = {

            }

        return render(request, "shadeboard/admin/reference.html", {
            "transaction": transaction,
            "s_transaction": s_transaction
        })

@login_required
def cardless_request_reference(request, id):
    loggedin_user = request.user

    if loggedin_user.is_staff:

        try:
            transaction = ProcessPayattitudeRequest.objects.get(pk=id)
        except ProcessCardRequest.DoesNotExist:
            pass

        try:
            s_transaction = Transaction.objects.get(reference=transaction.reference)
        except Transaction.DoesNotExist:
            s_transaction = {
                
            }

        return render(request, "shadeboard/admin/reference.html", {
            "transaction": transaction,
            "s_transaction": s_transaction
        })