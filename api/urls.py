from django.urls import path, include
from api.views import index, merchant
app_name = "api"
urlpatterns = [
    path('', index.index, name="index"),
    path('merchant/request', merchant.Merchant_View.as_view())
]