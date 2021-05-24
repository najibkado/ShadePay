from django.urls import path
from . import views
app_name = "shadeboard"
urlpatterns = [
    path('', views.index, name="index"),
    path('apidetails', views.apidetails, name="apidetails"),
    path('business-information', views.business_information, name="business-information")
]