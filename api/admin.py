from django.contrib import admin
from api.models import MerchantRequest, ShadepayRequest

# Register your models here.
admin.site.register(MerchantRequest)
admin.site.register(ShadepayRequest)
