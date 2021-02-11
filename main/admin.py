from django.contrib import admin
from .models import IndividualWallet, BusinessWallet, SavingWallet, Card, Bank, User, Transaction

# Register your models here.


admin.site.register(IndividualWallet)
admin.site.register(BusinessWallet)
admin.site.register(SavingWallet)
admin.site.register(Card)
admin.site.register(Bank)
admin.site.register(User)
admin.site.register(Transaction)