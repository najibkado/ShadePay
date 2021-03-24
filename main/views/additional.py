from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from main.models import AdditionalInformation
from django.urls import reverse
from django.contrib import messages

@login_required
def additional_information(request):

    #TODO: Add validation, and NIN verification

    loggedin_user = request.user

    if request.method ==  "GET":
        return render(request, "main/additional_information.html")

    if request.method == "POST":
        
        nin = request.POST["nin"]
        phone = request.POST["phone"]
        billing = request.POST["billing-addr"]
        shipping = request.POST["shipping-addr"]
        state = request.POST["state"]
        country = request.POST["country"]
        agree = request.POST.get("agree")

        if agree is not None:
            pass
        else:
            messages.error(request, "You have to read and agree to our terms of services, before you can get a wallet")
            return HttpResponseRedirect(reverse("additional_information"))

        try:
            information = AdditionalInformation.objects.get(user=loggedin_user)
            return HttpResponseRedirect(reverse("new-wallet"))
        except AdditionalInformation.DoesNotExist:
            information = AdditionalInformation(
                user = loggedin_user,
                nin = nin,
                accepted_terms = False if agree == None else True,
                mobile = phone,
                billing_address = billing,
                shipping_address = shipping,
                state = state,
                country = country,
            )
            information.save()
            return HttpResponseRedirect(reverse("new-wallet"))
        