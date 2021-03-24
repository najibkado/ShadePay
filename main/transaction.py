import requests
import hashlib
from decouple import config
from Crypto.Cipher import AES
import asyncio
from .models import ProcessCardRequest, ProcessPayattitudeRequest, IndividualWallet, BusinessWallet, SavingWallet
from .models import Transaction as Trans
from django.http import HttpResponseRedirect
from django.urls import reverse
import json
import binascii
import decimal
from django.db import IntegrityError
from main.utils import get_internal_tc, get_cot

class Transaction:

    """
    This class initiates and makes a transaction
    """

    def __init__(self, sender, reciever, transaction_code, amount, description="", sender_individual_wallet = "", sender_saving_wallet = "",
                sender_business_wallet = "", reciever_individual_wallet ="", reciever_saving_wallet = "", reciever_business_wallet = "", 
                sender_card = "", sender_bank = "", reciever_bank = "", currency = "NGN", status_code = "", status = "initiated", 
                come_back_url="https://www.shadepay.com", ref="",
                sender_card_expiry="", sender_card_cvv="", scheme="mastercard", process_card_id="", phone="", process_payattitude_id=""):

        self.sender = sender
        self.reciever = reciever
        self.transaction_code = transaction_code
        self.amount = amount
        self.sender_individual_wallet = sender_individual_wallet
        self.sender_saving_wallet = sender_saving_wallet
        self.sender_business_wallet = sender_business_wallet
        self.reciever_individual_wallet = reciever_individual_wallet
        self.reciever_saving_wallet = reciever_saving_wallet
        self.reciever_business_wallet = reciever_business_wallet
        self.sender_card = sender_card
        self.sender_bank = sender_bank
        self.reciever_bank = reciever_bank
        self.currency = currency
        self.status_code = status_code
        self.status = status
        self.come_back_url = come_back_url
        self.sender_card_expiry = sender_card_expiry
        self.sender_card_cvv = sender_card_cvv
        self.scheme = scheme
        self.process_card_id = process_card_id
        self.mobile = phone
        self.process_payattitude_id = process_payattitude_id
        self.ref = ref
        self.description = description

    def process_payattitude(self):
        """
        This process payments and return completion url or status if there's a failure
        """
        context = {
            "id": config("MERCHANT_ID"),
            "description": self.description,
            "amount": self.amount,
            "fee": 0,
            "currency": "566",
            "returnUrl": self.come_back_url,
            "secretKey": config("MERCHENT_KEY"),
            "scheme":"PayAttitude",
            "vendorId": "",
            "parameter":"",
            "count":0
        }

        print(context.items())

        headers = {
            "Accept": "application/json"
        }

        response = requests.post("https://test.payarena.com/Aggregator", headers=headers, data=context)

        if response.status_code == 200:
            
            res = response.json()

            #Update request process
            try:
                requested_payattitude_process = ProcessPayattitudeRequest.objects.get(pk=self.process_payattitude_id)
            except ProcessCardRequest.DoesNotExist:
                return HttpResponseRedirect(reverse("notfound"))

            requested_payattitude_process.reference = res
            requested_payattitude_process.save()
            sec_key = config("MERCHENT_KEY")
            sha_1 = hashlib.sha1()
            sha_1.update(bytes(sec_key, "utf-8"))
            sha_string = sha_1.hexdigest()

            transaction_data = {
                "secretKey": config("MERCHENT_KEY"),
                "scheme": "PayAttitude",
                "cardNumber": "",
                "expiry": "",
                "cvv": "",
                "cardholder": "",
                "mobile": self.mobile,
                "pin": ""
            }

            # def padd(m):
            #     return m+chr(16-len(m)%16)*(16-len(m)%16)

            BS = 16
            pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
            unpad = lambda s : s[0:-ord(s[-1])]

            encoded_data = pad(json.dumps(transaction_data))
            key = sha_string[0:16]
            key = bytes(key, "utf-8")
            encrypt_obj = AES.new(key, AES.MODE_CBC, key)
            encrypted_data = encrypt_obj.encrypt(encoded_data)
            merchant_id = config("MERCHANT_ID")
            encrypted_data = binascii.hexlify(encrypted_data)
            encrypted_data = encrypted_data.decode()

            redirect_url = f"https://test.payarena.com/Home/TransactionPost/{res}?mid={merchant_id}&payload={encrypted_data}"
            
            return redirect_url

        else:
            return None

    def process_card(self):
        """
        This process payments and return completion url or status if there's a failure
        """
        context = {
            "id": config("MERCHANT_ID"),
            "description": self.description,
            "amount": self.amount,
            "fee": 0,
            "currency": "566",
            "returnUrl": self.come_back_url,
            "secretKey": config("MERCHENT_KEY"),
            "scheme":self.scheme,
            "vendorId": "",
            "parameter":"",
            "count":0
        }

        headers = {
            "Accept": "application/json"
        }

        response = requests.post("https://test.payarena.com/Aggregator", headers=headers, data=context)

        if response.status_code == 200:
            
            res = response.json()

            #Update request process
            try:
                requested_card_process = ProcessCardRequest.objects.get(pk=self.process_card_id)
            except ProcessCardRequest.DoesNotExist:
                return HttpResponseRedirect(reverse("notfound"))

            requested_card_process.reference = res
            requested_card_process.save()
            sec_key = config("MERCHENT_KEY")
            sha_1 = hashlib.sha1()
            sha_1.update(bytes(sec_key, "utf-8"))
            sha_string = sha_1.hexdigest()

            transaction_data = {
                "secretKey": config("MERCHENT_KEY"),
                "scheme": self.scheme,
                "cardNumber": self.sender_card,
                "expiry": self.sender_card_expiry,
                "cvv": self.sender_card_cvv,
                "cardholder": "",
                "mobile": "",
                "pin": ""
            }

            def padd(m):
                return m+chr(16-len(m)%16)*(16-len(m)%16)

            BS = 16
            pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
            unpad = lambda s : s[0:-ord(s[-1])]

            encoded_data = pad(json.dumps(transaction_data))
            key = sha_string[0:16]
            key = bytes(key, "utf-8")
            encrypt_obj = AES.new(key, AES.MODE_CBC, key)
            encrypted_data = encrypt_obj.encrypt(encoded_data)
            merchant_id = config("MERCHANT_ID")
            encrypted_data = binascii.hexlify(encrypted_data)
            encrypted_data = encrypted_data.decode()

            redirect_url = f"https://test.payarena.com/Home/TransactionPost/{res}?mid={merchant_id}&payload={encrypted_data}"
            
            return redirect_url

        else:
            return None


    def send_internal_indiv_to_indiv(self):
        """
        Transaction Code 01 = Send Internal With Individual Wallet  -- Individual Wallet to Individual Wallet
        """
        try:
            new_transaction = Trans(
                sender = self.sender,
                reciever = self.reciever,
                transaction_code = self.transaction_code,
                amount = self.amount,
                sender_individual_wallet = self.sender_individual_wallet,
                reciever_individual_wallet = self.reciever_individual_wallet,
                status_code = self.status_code,
                status = self.status,
                reference = self.ref,
                rate_of_cost_of_transaction = "0",
                cost_of_transaction = 0,
                rate_of_transaction_charges = 20,
                transaction_charges = get_internal_tc(self.amount)
            )
            new_transaction.save()
            return new_transaction
        except IntegrityError:
            return False

    def request_internal_indiv_to_indiv(self):
        """
        02 = Request Internal with Individual Wallet  -- Individual Wallet to Individual Wallet
        """
        try:
            new_request = Trans(
                sender = self.sender,
                reciever = self.reciever,
                transaction_code = self.transaction_code,
                amount = self.amount,
                sender_individual_wallet = self.sender_individual_wallet,
                reciever_individual_wallet = self.reciever_individual_wallet,
                status_code = self.status_code,
                status = self.status,
                reference = self.ref
            )
            new_request.save()
            return True
        except IntegrityError:
            return False

    def pay_with_card_to_biz(self):
        """
        03 = Pay With Card  -- Card to Business Wallet
        """
        pass

    
    def pay_with_bank_to_biz(self):
        """
        04 = Pay With Bank  -- Bank to Business Wallet
        """
        pass

    def deposit_with_card_to_indiv(self):
        """
        05 = Deposit To Individual Wallet   -- Card to Individual Wallet
        """

        try:
            new_transaction = Trans(
                sender = self.sender,
                reciever = self.reciever,
                transaction_code = self.transaction_code,
                amount = self.amount,
                reciever_individual_wallet = self.reciever_individual_wallet,
                currency = self.currency,
                status_code = self.status_code,
                status = self.status,
                reference = self.ref,
                rate_of_cost_of_transaction = "1.25%",
                cost_of_transaction = get_cot(self.amount),
                rate_of_transaction_charges = 0,
                transaction_charges = 0
            )
            new_transaction.save()
            return new_transaction
        except IntegrityError:
            return False


    def deposit_with_card_to_savin(self):
        """
        06 = Deposit To Saving Wallet  -- Card to Saving Wallet
        """

        try:
            new_transaction = Trans(
                sender = self.sender,
                reciever = self.reciever,
                transaction_code = self.transaction_code,
                amount = self.amount,
                reciever_saving_wallet = self.reciever_saving_wallet,
                currency = self.currency,
                status_code = self.status_code,
                status = self.status,
                reference = self.ref,
                rate_of_cost_of_transaction = "1.25%",
                cost_of_transaction = get_cot(self.amount),
                rate_of_transaction_charges = 0,
                transaction_charges = 0
            )
            new_transaction.save()
            return new_transaction
        except IntegrityError:
            return False


    def deposit_with_card_to_biz(self):
        """
        07 = Deposit To Business Wallet  -- Card to Business Wallet
        """

        try:
            new_transaction = Trans(
                sender = self.sender,
                reciever = self.reciever,
                transaction_code = self.transaction_code,
                amount = self.amount,
                reciever_business_wallet = self.reciever_business_wallet,
                currency = self.currency,
                status_code = self.status_code,
                status = self.status,
                reference = self.ref,
                rate_of_cost_of_transaction = "1.25%",
                cost_of_transaction = get_cot(self.amount),
                rate_of_transaction_charges = 0,
                transaction_charges = 0
            )
            new_transaction.save()
            return new_transaction
        except IntegrityError:
            return False

    
    def deposit_with_card_to_biz_mer(self):
        """
        ## = Deposit To Business Wallet  -- Card to Business Wallet Merchant Transaction
        """
        try:
            new_transaction = Trans(
                sender = self.sender,
                reciever = self.reciever,
                transaction_code = self.transaction_code,
                amount = self.amount,
                reciever_business_wallet = self.reciever_business_wallet,
                currency = self.currency,
                status_code = self.status_code,
                status = self.status,
                reference = self.ref,
                rate_of_cost_of_transaction = "1.25%",
                cost_of_transaction = get_cot(self.amount),
                rate_of_transaction_charges = 20,
                transaction_charges = get_internal_tc(self.amount)
            )
            new_transaction.save()
            return new_transaction
        except IntegrityError:
            return False


    def send_indiv_to_biz(self):        
        """
        08 = Pay With Individual Wallet  -- Individual Wallet to Business Wallet
        """
        try:
            new_transaction = Trans(
                sender = self.sender,
                reciever = self.reciever,
                transaction_code = self.transaction_code,
                amount = self.amount,
                sender_individual_wallet = self.sender_individual_wallet,
                reciever_business_wallet = self.reciever_business_wallet,
                status_code = self.status_code,
                status = self.status,
                reference = self.ref,
                rate_of_cost_of_transaction = "0",
                cost_of_transaction = 0,
                rate_of_transaction_charges = 20,
                transaction_charges = get_internal_tc(self.amount)
            )
            new_transaction.save()
            return new_transaction
        except IntegrityError:
            return False
 

    def send_biz_to_biz(self):
        """
        09 = Pay With Business Wallet  -- Business Wallet to Business Wallet
        """
        try:
            new_transaction = Trans(
                sender = self.sender,
                reciever = self.reciever,
                transaction_code = self.transaction_code,
                amount = self.amount,
                sender_business_wallet = self.sender_business_wallet,
                reciever_business_wallet = self.reciever_business_wallet,
                status_code = self.status_code,
                status = self.status,
                reference = self.ref,
                rate_of_cost_of_transaction = "0",
                cost_of_transaction = 0,
                rate_of_transaction_charges = 20,
                transaction_charges = get_internal_tc(self.amount)
            )
            new_transaction.save()
            return new_transaction
        except IntegrityError:
            return False

    def withdraw_from_savin(self):
        """
        10 = Withdraw From Saving Wallet  -- Saving wallet to Bank
        """
        pass

    def withdraw_from_biz(self):
        """
        11 = Withdraw From Business Wallet  -- Business wallet to Bank
        """
        pass

    def withdraw_from_indiv(self):
        """
        12 = Withdraw From Individual Wallet  -- Individual wallet to Bank
        """
        pass

    def send_indiv_to_savin(self):
        """
        13 = Pay With Individual Wallet2  -- Individual Wallet to Saving Wallet
        """
        try:
            new_transaction = Trans(
                sender = self.sender,
                reciever = self.reciever,
                transaction_code = self.transaction_code,
                amount = self.amount,
                sender_individual_wallet = self.sender_individual_wallet,
                reciever_saving_wallet = self.reciever_saving_wallet,
                status_code = self.status_code,
                status = self.status,
                reference = self.ref,
                rate_of_cost_of_transaction = "0",
                cost_of_transaction = 0,
                rate_of_transaction_charges = 20,
                transaction_charges = get_internal_tc(self.amount)
            )
            new_transaction.save()
            return new_transaction
        except IntegrityError:
            return False

    def send_biz_to_savin(self):
        """
        14 = Pay With Business Wallet2  -- Business Wallet to Saving Wallet
        """
        try:
            new_transaction = Trans(
                sender = self.sender,
                reciever = self.reciever,
                transaction_code = self.transaction_code,
                amount = self.amount,
                sender_business_wallet = self.sender_business_wallet,
                reciever_saving_wallet = self.reciever_saving_wallet,
                status_code = self.status_code,
                status = self.status,
                reference = self.ref,
                rate_of_cost_of_transaction = "0",
                cost_of_transaction = 0,
                rate_of_transaction_charges = 20,
                transaction_charges = get_internal_tc(self.amount)
            )
            new_transaction.save()
            return new_transaction
        except IntegrityError:
            return False

    def send_biz_to_indiv(self):
        """
        15 = Pay With Business Wallet3  -- Business Wallet to Individual Wallet
        """
        try:
            new_transaction = Trans(
                sender = self.sender,
                reciever = self.reciever,
                transaction_code = self.transaction_code,
                amount = self.amount,
                sender_business_wallet = self.sender_business_wallet,
                reciever_individual_wallet = self.reciever_individual_wallet,
                status_code = self.status_code,
                status = self.status,
                reference = self.ref,
                rate_of_cost_of_transaction = "0",
                cost_of_transaction = 0,
                rate_of_transaction_charges = 20,
                transaction_charges = get_internal_tc(self.amount)
            )
            new_transaction.save()
            return new_transaction
        except IntegrityError:
            return False

    def request_indiv_to_biz(self):
        """
        16 = Request Internal with Individual Wallet  -- Individual Wallet to Business Wallet
        """
        try:
            new_request = Trans(
                sender = self.sender,
                reciever = self.reciever,
                transaction_code = self.transaction_code,
                amount = self.amount,
                sender_individual_wallet = self.sender_individual_wallet,
                reciever_business_wallet = self.reciever_business_wallet,
                status_code = self.status_code,
                status = self.status,
                reference = self.ref
            )
            new_request.save()
            return True
        except IntegrityError:
            return False

    def request_biz_to_biz(self):
        """
        17 = Request Internal with Business Wallet  -- Business Wallet to Business Wallet
        """
        try:
            new_request = Trans(
                sender = self.sender,
                reciever = self.reciever,
                transaction_code = self.transaction_code,
                amount = self.amount,
                sender_business_wallet = self.sender_business_wallet,
                reciever_business_wallet = self.reciever_business_wallet,
                status_code = self.status_code,
                status = self.status,
                reference = self.ref
            )
            new_request.save()
            return True
        except IntegrityError:
            return False

    def request_biz_to_indiv(self):
        """
        18 = Request Internal with Business Wallet  -- Business Wallet to Individual Wallet
        """
        try:
            new_request = Trans(
                sender = self.sender,
                reciever = self.reciever,
                transaction_code = self.transaction_code,
                amount = self.amount,
                sender_business_wallet = self.sender_business_wallet,
                reciever_individual_wallet = self.reciever_individual_wallet,
                status_code = self.status_code,
                status = self.status,
                reference = self.ref
            )
            new_request.save()
            return True
        except IntegrityError:
            return False

    def deposit_pat_to_indiv(self):
        """
        19 = Deposit Cardless with PayAttitude  -- Cardless to Individual Wallet
        """

        try:
            new_transaction = Trans(
                sender = self.sender,
                reciever = self.reciever,
                transaction_code = self.transaction_code,
                amount = self.amount,
                reciever_individual_wallet = self.reciever_individual_wallet,
                mobile = self.mobile,
                status = self.status,
                status_code = self.status_code,
                reference = self.ref,
                rate_of_cost_of_transaction = "1.25%",
                cost_of_transaction = get_cot(self.amount),
                rate_of_transaction_charges = 0,
                transaction_charges = 0
            )
            new_transaction.save()
            return new_transaction
        except IntegrityError:
            return False

    def deposit_pat_to_savin(self):
        """
        20 = Deposit Cardless with PayAttitude  -- Cardless to Saving Wallet
        """

        try:
            new_transaction = Trans(
                sender = self.sender,
                reciever = self.reciever,
                transaction_code = self.transaction_code,
                amount = self.amount,
                reciever_saving_wallet = self.reciever_saving_wallet,
                mobile = self.mobile,
                status = self.status,
                status_code = self.status_code,
                reference = self.ref,
                rate_of_cost_of_transaction = "1.25%",
                cost_of_transaction = get_cot(self.amount),
                rate_of_transaction_charges = 0,
                transaction_charges = 0
            )
            new_transaction.save()
            return new_transaction
        except IntegrityError:
            return False

    def deposit_pat_to_biz(self):
        """
        21 = Deposit Cardless with PayAttitude  -- Cardless to Business Wallet
        """

        try:
            new_transaction = Trans(
                sender = self.sender,
                reciever = self.reciever,
                transaction_code = self.transaction_code,
                amount = self.amount,
                reciever_business_wallet = self.reciever_business_wallet,
                mobile = self.mobile,
                status = self.status,
                status_code = self.status_code,
                reference = self.ref,
                rate_of_cost_of_transaction = "1.25%",
                cost_of_transaction = get_cot(self.amount),
                rate_of_transaction_charges = 0,
                transaction_charges = 0
            )
            new_transaction.save()
            return new_transaction
        except IntegrityError:
            return False

    def send_savin_to_indiv(self):
        """
        22 = Send saving wallet -- saving wallet to individual wallet
        """
        try:
            new_transaction = Trans(
                sender = self.sender,
                reciever = self.reciever,
                transaction_code = self.transaction_code,
                amount = self.amount,
                sender_saving_wallet = self.sender_saving_wallet,
                reciever_individual_wallet = self.reciever_individual_wallet,
                status_code = self.status_code,
                status = self.status,
                reference = self.ref,
                rate_of_cost_of_transaction = "0",
                cost_of_transaction = 0,
                rate_of_transaction_charges = 20,
                transaction_charges = get_internal_tc(self.amount)
            )
            new_transaction.save()
            return new_transaction
        except IntegrityError:
            return False

    def send_savin_to_biz(self):
        """
        23 = Send saving wallet -- saving wallet to business wallet
        """
        try:
            new_transaction = Trans(
                sender = self.sender,
                reciever = self.reciever,
                transaction_code = self.transaction_code,
                amount = self.amount,
                sender_saving_wallet = self.sender_saving_wallet,
                reciever_business_wallet = self.reciever_business_wallet,
                status_code = self.status_code,
                status = self.status,
                reference = self.ref,
                rate_of_cost_of_transaction = "0",
                cost_of_transaction = 0,
                rate_of_transaction_charges = 20,
                transaction_charges = get_internal_tc(self.amount)
            )
            new_transaction.save()
            return new_transaction
        except IntegrityError:
            return False

    def send_savin_to_savin(self):
        """
        24 = Send saving wallet -- saving wallet to saving wallet
        """
        try:
            new_transaction = Trans(
                sender = self.sender,
                reciever = self.reciever,
                transaction_code = self.transaction_code,
                amount = self.amount,
                sender_saving_wallet = self.sender_saving_wallet,
                reciever_saving_wallet = self.reciever_saving_wallet,
                status_code = self.status_code,
                status = self.status,
                reference = self.ref,
                rate_of_cost_of_transaction = "0",
                cost_of_transaction = 0,
                rate_of_transaction_charges = 20,
                transaction_charges = get_internal_tc(self.amount)
            )
            new_transaction.save()
            return new_transaction
        except IntegrityError:
            return False

    def request_indiv_to_savin(self):
        """
        26 = Request Individual -- Request individual wallet to saving wallet
        """
        try:
            new_request = Trans(
                sender = self.sender,
                reciever = self.reciever,
                transaction_code = self.transaction_code,
                amount = self.amount,
                sender_individual_wallet = self.sender_individual_wallet,
                reciever_saving_wallet = self.reciever_saving_wallet,
                status_code = self.status_code,
                status = self.status,
                reference = self.ref
            )
            new_request.save()
            return True
        except IntegrityError:
            return False

    def request_biz_to_savin(self):
        """
        27 = Request Business -- Request Business wallet to saving wallet
        """
        try:
            new_request = Trans(
                sender = self.sender,
                reciever = self.reciever,
                transaction_code = self.transaction_code,
                amount = self.amount,
                sender_business_wallet = self.sender_business_wallet,
                reciever_saving_wallet = self.reciever_saving_wallet,
                status_code = self.status_code,
                status = self.status,
                reference = self.ref
            )
            new_request.save()
            return True
        except IntegrityError:
            return False

    def request_savin_to_indiv(self):
        """
        28 = Request Saving -- Request Saving wallet to individual wallet
        """
        try:
            new_request = Trans(
                sender = self.sender,
                reciever = self.reciever,
                transaction_code = self.transaction_code,
                amount = self.amount,
                sender_saving_wallet = self.sender_saving_wallet,
                reciever_individual_wallet = self.reciever_individual_wallet,
                status_code = self.status_code,
                status = self.status,
                reference = self.ref
            )
            new_request.save()
            return True
        except IntegrityError:
            return False

    def request_savin_to_biz(self):
        """
        29 = Request Saving -- Request Saving wallet to business wallet
        """
        try:
            new_request = Trans(
                sender = self.sender,
                reciever = self.reciever,
                transaction_code = self.transaction_code,
                amount = self.amount,
                sender_saving_wallet = self.sender_saving_wallet,
                reciever_business_wallet = self.reciever_business_wallet,
                status_code = self.status_code,
                status = self.status,
                reference = self.ref
            )
            new_request.save()
            return True
        except IntegrityError:
            return False

    def request_savin_to_savin(self):
        """
        29 = Request Saving -- Request Saving wallet to business wallet
        """
        try:
            new_request = Trans(
                sender = self.sender,
                reciever = self.reciever,
                transaction_code = self.transaction_code,
                amount = self.amount,
                sender_saving_wallet = self.sender_saving_wallet,
                reciever_saving_wallet = self.reciever_saving_wallet,
                status_code = self.status_code,
                status = self.status,
                reference = self.ref
            )
            new_request.save()
            return True
        except IntegrityError:
            return False





    