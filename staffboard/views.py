from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from main.models import BusinessWallet, DeveloperInformation, Developer, ProcessCardRequest, ProcessPayattitudeRequest, Transaction, Recipt
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse

# Create your views here.

def index(request):
    return render(request, 'staffboard/sam.html')

@login_required
def admin(request):
    loggedin_user = request.user

    if loggedin_user.is_staff:
        return render(request, "staffboard/admin/admin.html")

@login_required
def card_requests(request):
    loggedin_user = request.user

    all_requests = ProcessCardRequest.objects.all()
    all_requests = reversed(all_requests)

    if loggedin_user.is_staff:
        return render(request, "staffboard/admin/card_requests.html", {
            "all_requests": all_requests
        })

@login_required
def cardless_requests(request):
    loggedin_user = request.user

    if loggedin_user.is_staff:

        all_requests = ProcessPayattitudeRequest.objects.all()
        all_requests = reversed(all_requests)

        return render(request, "staffboard/admin/cardless_requests.html", {
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

        return render(request, "staffboard/admin/request_details.html", {
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

        return render(request, "staffboard/admin/request_details.html", {
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

        return render(request, "staffboard/admin/recipts.html", {
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

        return render(request, "staffboard/admin/recipt.html", {
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

        return render(request, "staffboard/admin/reference.html", {
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

        return render(request, "staffboard/admin/reference.html", {
            "transaction": transaction,
            "s_transaction": s_transaction
        })

