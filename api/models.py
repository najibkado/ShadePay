from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import HStoreField

# Create your models here.
class MerchantRequest(models.Model):
    wallet = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=255, decimal_places=2)
    description = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    approved = models.BooleanField(default=False)
    returnUrl = models.URLField()
    ip = models.GenericIPAddressField()
    isProcessed = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now=True)

class ShadepayRequest(models.Model):
    wallet = models.CharField(max_length=255)
    amount = models.CharField(max_length=255)
    products = models.CharField(max_length=255)
    products_description = models.CharField(max_length=255)
    quantity = models.IntegerField()
    status = models.CharField(max_length=255)
    isProcessed = models.BooleanField(default=False)
    approved = models.BooleanField(default=False)
    returnUrl = models.URLField()
    date = models.DateTimeField(auto_now=True)
