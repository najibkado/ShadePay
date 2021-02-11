import requests
import hashlib
from decouple import config
from Crypto.Cipher import AES

class Transaction:

    """
    This class initiates and makes a transaction
    """

    def __init__(self, sender, reciever, transaction_code, amount, sender_individual_wallet = "", sender_saving_wallet = "",
                sender_business_wallet = "", reciever_individual_wallet ="", reciever_saving_wallet = "", reciever_business_wallet = "", 
                sender_card = "", sender_bank = "", reciever_bank = "", currency = "NGN", status_code = "", status = "initiated", come_back_url="",
                sender_card_expiry="", sender_card_cvv=""):

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

    def process_card(self):
        """
        This process payments and return completion url or status if there's a failure
        """
        context = {
            "id": config("MERCHANT_ID"),
            "description": "payment for goods",
            "amount": self.amount,
            "fee": 0,
            "currency": "556",
            "returnUrl": self.come_back_url,
            "secretKey": config("MERCHENT_KEY"),
            "scheme":"",
            "vendorId": "",
            "parameter":"",
            "count":0
        }

        headers = {
            "Content-Type": "application/json",
            "Vary": "Accept"
        }

        response = requests.post("https://test.payarena.com/Aggregator", headers=headers, data=context)

        if response.status_code == 200:
            res = response.json()
            
            print(res.id)

            sha_1 = hashlib.sha1()
            sha_1.update(res.id)
            sha_string = sha_1.hexdigest()

            transaction_data = {
                "secretKey": config("MERCHENT_KEY"),
                "scheme": "mastercard",
                "cardNumber": self.sender_card,
                "expiry": self.sender_card_expiry,
                "cvv": self.sender_card_cvv,
                "cardholder": "",
                "mobile": "",
                "pin": ""
            }

            key = sha_string[0:16]

            encrypt_obj = AES.new(key, AES.MODE_CBC, key)

            encrypted_data = encrypt_obj.encrypt(transaction_data)

            redirect_url = f"https://test.payarena.com/Home/TransactionPost/{res.id}/{transaction_data.secretKey}/{encrypted_data}"

            return redirect_url

        else:
            print(response.status_code, response.json(), sep="------------", end="\n")


    def send_internal_indiv_to_indiv(self):
        """
        Transaction Code 01 = Send Internal With Individual Wallet  -- Individual Wallet to Individual Wallet
        """
        pass

    def request_internal_indiv_to_indiv(self):
        """
        02 = Request Internal with Individual Wallet  -- Individual Wallet to Individual Wallet
        """
        pass

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
        pass

    def deposit_with_card_to_savin(self):
        """
        06 = Deposit To Saving Wallet  -- Card to Saving Wallet
        """
        pass

    def deposit_with_card_to_biz(self):
        """
        07 = Deposit To Business Wallet  -- Card to Business Wallet
        """
        pass

    def send_indiv_to_biz(self):
         """
         08 = Pay With Individual Wallet  -- Individual Wallet to Business Wallet
         """
         pass

    def send_biz_to_biz(self):
        """
        09 = Pay With Business Wallet  -- Business Wallet to Business Wallet
        """
        pass

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
        pass

    def send_biz_to_savin(self):
        """
        14 = Pay With Business Wallet2  -- Business Wallet to Saving Wallet
        """
        pass

    def send_biz_to_indiv(self):
        """
        15 = Pay With Business Wallet3  -- Business Wallet to Individual Wallet
        """
        pass

    def request_indiv_to_biz(self):
        """
        16 = Request Internal with Individual Wallet  -- Individual Wallet to Business Wallet
        """
        pass

    def request_biz_to_biz(self):
        """
        17 = Request Internal with Business Wallet  -- Business Wallet to Business Wallet
        """
        pass

    def request_biz_to_indiv(self):
        """
        18 = Request Internal with Business Wallet  -- Business Wallet to Individual Wallet
        """
        pass
    