from django.db import models
from django.contrib.auth.models import AbstractUser
from api.models import MerchantRequest

# Create your models here.
class User(AbstractUser):
    pass

class AdditionalInformation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="profile")
    accepted_terms = models.BooleanField(default=True)
    mobile = models.CharField(max_length=255)
    is_business = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=True)
    shipping_address = models.CharField(max_length=255) 
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255, default='Nigeria')
    is_deleted = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now=True)

class Logs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="logs")
    ip_address = models.CharField(max_length=255)
    login_location = models.CharField(max_length=255)
    lon = models.CharField(max_length=255)
    lat = models.CharField(max_length=255)
    login_device = models.CharField(max_length=255)
    date = models.DateField(auto_now=True)

class BusinessWallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="business_wallet")
    address = models.CharField(max_length=255, unique=True)
    link = models.CharField(max_length=255)
    balance = models.DecimalField(max_digits=255, decimal_places=2)
    date_updated = models.DateTimeField(auto_now=True)

class CheckoutLog(models.Model):
    merchant = models.ForeignKey(BusinessWallet, on_delete=models.CASCADE, related_name="business_logs")
    ip_address = models.CharField(max_length=255)
    checkout_location = models.CharField(max_length=255)
    lon = models.CharField(max_length=255)
    lat = models.CharField(max_length=255)
    client_device = models.CharField(max_length=255)
    date = models.DateField(auto_now=True)

class Developer(models.Model):
    api_key = models.CharField(max_length=255, unique=True)
    secrete_key = models.CharField(max_length=255)
    wallet = models.ForeignKey(BusinessWallet, on_delete=models.CASCADE, related_name="developer_wallet_details")
    date_registered = models.DateTimeField(auto_now=True)

class DeveloperInformation(models.Model):
    developer = models.ForeignKey(Developer, on_delete=models.CASCADE, related_name="developer_details")
    business_name = models.CharField(max_length=255)
    business_address = models.CharField(max_length=255)
    business_phone = models.CharField(max_length=255)
    business_email = models.CharField(max_length=255)
    business_nature = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now=True)

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

class ProcessCardRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="topup_request")
    amount = models.DecimalField(max_digits=255, decimal_places=2)
    card_first_six = models.CharField(max_length=255)
    card_last_four = models.CharField(max_length=255)
    card_type = models.CharField(max_length=255)
    business_wallet = models.ForeignKey(BusinessWallet, null=True, blank=True, on_delete=models.CASCADE, related_name="topup_request_business_walet")
    is_successful = models.BooleanField(default=False)
    status = models.CharField(max_length=255)
    reference = models.CharField(max_length=255)
    transaction_code = models.IntegerField()
    raw_data = models.CharField(max_length=255)
    merchant_request = models.ForeignKey(MerchantRequest, null=True, blank=True, on_delete=models.CASCADE, related_name="merchant_card_request")
    date = models.DateTimeField(auto_now=True)

class ApprovedUnprocessedCardRequest(models.Model):
    process = models.ForeignKey(ProcessCardRequest, on_delete=models.CASCADE, related_name="unprocessed_transaction")
    date = models.DateTimeField(auto_now=True)

class MissingWalletTransactionRequest(models.Model):
    process = models.ForeignKey(ProcessCardRequest, on_delete=models.CASCADE, related_name="missing_wallet_card_process")
    date = models.DateTimeField(auto_now=True)

class ProcessPayattitudeRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payattitude_request")
    amount = models.DecimalField(max_digits=255, decimal_places=2)
    mobile = models.CharField(max_length=255)
    business_wallet = models.ForeignKey(BusinessWallet, null=True, blank=True, on_delete=models.CASCADE, related_name="payattitude_request_business_walet")
    is_successful = models.BooleanField(default=False)
    status = models.CharField(max_length=255)
    reference = models.CharField(max_length=255)
    raw_data = models.CharField(max_length=255)
    transaction_code = models.IntegerField()
    date = models.DateTimeField(auto_now=True)

class ApprovedUnprocessedCardlessRequest(models.Model):
    process = models.ForeignKey(ProcessPayattitudeRequest, on_delete=models.CASCADE, related_name="unprocessed_cardless_transaction")
    date = models.DateTimeField(auto_now=True)

class MissingWalletCardlessTransactionRequest(models.Model):
    process = models.ForeignKey(ProcessPayattitudeRequest, on_delete=models.CASCADE, related_name="missing_wallet_cardless_process")
    date = models.DateTimeField(auto_now=True)

class Transaction(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sender_transactions")
    reciever = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reciever_transactions")
    transaction_code = models.IntegerField()
    amount = models.DecimalField(max_digits=255, decimal_places=2)
    rate_of_cost_of_transaction = models.CharField(max_length=255)
    cost_of_transaction = models.DecimalField(max_digits=255, decimal_places=2)
    rate_of_transaction_charges = models.CharField(max_length=255, default="1.25% + 20 : Max 3500")
    transaction_charges = models.DecimalField(max_digits=255, decimal_places=2)
    sender_business_wallet = models.ForeignKey(BusinessWallet, null=True, blank=True, on_delete=models.CASCADE, related_name="source_business_wallet")
    reciever_business_wallet = models.ForeignKey(BusinessWallet, null=True, blank=True, on_delete=models.CASCADE, related_name="destination_business_wallet")
    sender_card = models.ForeignKey(Card, on_delete=models.CASCADE, null=True, blank=True, related_name="source_card")
    sender_bank = models.ForeignKey(Bank, on_delete=models.CASCADE, null=True, blank=True, related_name="source_bank")
    reciever_bank = models.ForeignKey(Bank, on_delete=models.CASCADE, null=True, blank=True, related_name="destination_bank")
    currency = models.CharField(max_length=255)
    mobile = models.CharField(max_length=255)
    status_code = models.IntegerField()
    reference = models.CharField(max_length=255)
    status = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
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
            "desc" : self.description,
            "code" : self.transaction_code,
            "status" : self.status,
            "reference": self.reference,
            "transaction_charges": self.transaction_charges,
            "sender_business_wallet": self.sender_business_wallet.address if self.sender_business_wallet else "",
            "reciever_business_wallet": self.reciever_business_wallet.address if self.reciever_business_wallet else "",
        }

class ContactUs(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    message = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now=True)

class NewsletterRegister(models.Model):
    email = models.EmailField()
    is_unsubscribed = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now=True)

class Argument(models.Model):
    pass

class Recipt(models.Model):
    sender = models.CharField(max_length=255)
    reciever = models.CharField(max_length=255)
    trx_id = models.CharField(max_length=255)
    trx_date = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=255, decimal_places=2)
    charges = models.DecimalField(max_digits=255, decimal_places=2)
    reciever_wallet = models.CharField(max_length=255)
    reciever_amount = models.DecimalField(max_digits=255, decimal_places=2)
    status = models.CharField(max_length=255)
    email_for = models.CharField(max_length=255)
    channel = models.CharField(max_length=255)
    card = models.CharField(max_length=255)
    mobile = models.CharField(max_length=255)
    trx_ref = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)