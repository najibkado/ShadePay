from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    pass

class AdditionalInformation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="profile")
    BVN = models.IntegerField(unique=True)
    DOB = models.CharField(max_length=255)
    mobile = models.CharField(max_length=255)
    is_verified = models.BooleanField(default=False)
    billing_address = models.CharField(max_length=255)
    shipping_address = models.CharField(max_length=255) 
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255, default='Nigeria')
    is_deleted = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now=True)

class Logs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="logs")
    ip_address = models.GenericIPAddressField()
    login_location = models.CharField(max_length=255)
    login_device = models.CharField(max_length=255)


class IndividualWallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wallet")
    address = models.CharField(max_length=255, unique=True)
    link = models.CharField(max_length=255)
    balance = models.DecimalField(max_digits=255, decimal_places=3)
    date_updated = models.DateTimeField(auto_now=True)

class SavingWallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="savings_wallet")
    address = models.CharField(max_length=255, unique=True)
    link = models.CharField(max_length=255)
    balance = models.DecimalField(max_digits=255, decimal_places=3)
    date_updated = models.DateTimeField(auto_now=True)
    date_due = models.DateField(auto_now=False)

class BusinessWallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="business_wallet")
    address = models.CharField(max_length=255, unique=True)
    link = models.CharField(max_length=255)
    balance = models.DecimalField(max_digits=255, decimal_places=3)
    date_updated = models.DateTimeField(auto_now=True)


class Developer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="developer_details")
    api_key = models.CharField(max_length=255, unique=True)
    wallet = models.ForeignKey(BusinessWallet, on_delete=models.CASCADE, related_name="developer_wallet_details")
    date_registered = models.DateTimeField(auto_now=True)

class Card(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="card_details")
    card_type = models.CharField(max_length=255)
    card_num = models.IntegerField()
    card_cvv = models.IntegerField()
    card_exp_date = models.DateField()
    date_added = models.DateTimeField(auto_now=True)

class Bank(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bank_details")
    bank = models.CharField(max_length=255, blank=True)
    bank_code = models.IntegerField()
    dob = models.DateField()
    date_added = models.DateTimeField(auto_now=True)

class Transaction(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender_transactions")
    reciever = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reciever_transactions")
    transaction_code = models.IntegerField()
    amount = models.DecimalField(max_digits=255, decimal_places=2)
    sender_individual_wallet = models.ForeignKey(IndividualWallet, null=True, blank=True, on_delete=models.CASCADE, related_name="source_individual_wallet")
    sender_saving_wallet = models.ForeignKey(SavingWallet, null=True, blank=True, on_delete=models.CASCADE, related_name="source_saving_wallet")
    sender_business_wallet = models.ForeignKey(BusinessWallet, null=True, blank=True, on_delete=models.CASCADE, related_name="source_business_wallet")
    reciever_individual_wallet = models.ForeignKey(IndividualWallet, null=True, blank=True, on_delete=models.CASCADE, related_name="destination_individual_wallet")
    reciever_saving_wallet = models.ForeignKey(SavingWallet, null=True, blank=True, on_delete=models.CASCADE, related_name="destination_saving_wallet")
    reciever_business_wallet = models.ForeignKey(BusinessWallet, null=True, blank=True, on_delete=models.CASCADE, related_name="destination_business_wallet")
    sender_card = models.ForeignKey(Card, on_delete=models.CASCADE, null=True, blank=True, related_name="source_card")
    sender_bank = models.ForeignKey(Bank, on_delete=models.CASCADE, null=True, blank=True, related_name="source_bank")
    reciever_bank = models.ForeignKey(Bank, on_delete=models.CASCADE, null=True, blank=True, related_name="destination_bank")
    currency = models.CharField(max_length=255)
    status_code = models.IntegerField()
    status = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now=True)

    def serialize(self):
        """
        Returns serializable transaction data
        """
        return {
            "transaction_id" : self.id,
            "sender_id" : self.sender.id,
            "sender" : self.sender.first_name + " " + self.sender.last_name,
            "reciever" : self.reciever.first_name + " " + self.reciever.last_name,
            "status_code" : self.status_code,
            "amount" : self.amount,
            "currency" : self.currency,
            "date" : self.date,
            "status" : self.status
        }

class ContactUs(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    message = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now=True)

class Argument(models.Model):
    pass