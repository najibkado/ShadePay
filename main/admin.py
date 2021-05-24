from django.contrib import admin
from .models import BusinessWallet, Card, Bank, User, Transaction, ProcessCardRequest, Developer, AdditionalInformation
from .models import DeveloperInformation, ProcessPayattitudeRequest, Logs, CheckoutLog, ApprovedUnprocessedCardRequest, ApprovedUnprocessedCardlessRequest
from .models import Recipt
# Register your models here.


admin.site.register(BusinessWallet)
admin.site.register(Card)
admin.site.register(Bank)
admin.site.register(User)
admin.site.register(Transaction)
admin.site.register(ProcessCardRequest)
admin.site.register(Developer)
admin.site.register(DeveloperInformation)
admin.site.register(AdditionalInformation)
admin.site.register(ProcessPayattitudeRequest)
admin.site.register(Logs)
admin.site.register(CheckoutLog)
admin.site.register(ApprovedUnprocessedCardRequest)
admin.site.register(ApprovedUnprocessedCardlessRequest)
admin.site.register(Recipt)