import threading
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from main.models import Recipt
from django.db import IntegrityError
import decimal


class EmailThread(threading.Thread):
    """
    Email Thread Class:
    This is to speed the process of sending email to users
    The thread will be used so as to not use network thread
    """

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        """
        Execute the message
        """
        self.email.send(fail_silently=False)

class EmailSender:
    """
    This module let you send email to users
    """
    def __init__(self, subject, reciever, body):
        self.subject = subject
        self.reciever = reciever
        self.body = body
        self.email = "services@shadepay.com"


    def email_sender(self):

        # subject = 'ShadePay Account Activation'
        # body = 'Hello ' + new_user.username + ', Please click on the link below to verify your account.\n'+verification_url+'\n' + '\n' + '\n'+'Thankyou for choosing ShadePay'
        # sender_email = 'services@shadepay.com'
        self.subject = "Transaction Alert"

        context = {
            "sender": self.body['sender'],
            "reciever": self.body['reciever'],
            "trx_id": self.body['trx_id'],
            "trx_date": self.body['trx_date'],
            "amount": self.body['amount'],
            "charges": self.body['charges'],
            "reciever_wallet": self.body['reciever_wallet'],
            "recieve_amount": self.body['recieve_amount'],
            "status": self.body['status'],
            "email_for": self.body['email_for']
        }

        body = render_to_string('main/email/send.html', context)
        
        new_email = EmailMessage(
            self.subject,
            body,
            self.email,
            [self.reciever],
        )
        new_email.content_subtype = 'html'

        try:
            generate_recipt = Recipt(
                sender = context['sender'],
                reciever = context['reciever'],
                trx_id = context['trx_id'],
                trx_date = context['trx_date'],
                amount = decimal.Decimal(context['amount']),
                charges = decimal.Decimal(context['charges']),
                reciever_wallet = context['reciever_wallet'],
                reciever_amount = context['recieve_amount'],
                status = context['status'],
                email_for = context['email_for'],
                channel = "",
                card = "",
                mobile = "",
                trx_ref = ""
            )
            generate_recipt.save()
        except IntegrityError:
            pass

        EmailThread(new_email).start()


    def email_reciever(self):


        self.subject = "Transaction Alert"

        context = {
            "sender": self.body['sender'],
            "reciever": self.body['reciever'],
            "trx_id": self.body['trx_id'],
            "trx_date": self.body['trx_date'],
            "amount": self.body['amount'],
            "charges": self.body['charges'],
            "reciever_wallet": self.body['reciever_wallet'],
            "recieve_amount": self.body['recieve_amount'],
            "status": self.body['status'],
            "email_for": self.body['email_for']
        }

        body = render_to_string('main/email/recieve.html', context)
        
        new_email = EmailMessage(
            self.subject,
            body,
            self.email,
            [self.reciever],
        )
        new_email.content_subtype = 'html'

        try:
            generate_recipt = Recipt(
                sender = context['sender'],
                reciever = context['reciever'],
                trx_id = context['trx_id'],
                trx_date = context['trx_date'],
                amount = decimal.Decimal(context['amount']),
                charges = decimal.Decimal(context['charges']),
                reciever_wallet = context['reciever_wallet'],
                reciever_amount = context['recieve_amount'],
                status = context['status'],
                email_for = context['email_for'],
                channel = "",
                card = "",
                mobile = "",
                trx_ref = ""
            )
            generate_recipt.save()
        except IntegrityError:
            pass

        EmailThread(new_email).start()

    def email_top_up(self):

        self.subject = "Topup Alert"

        context = {
            "channel": self.body['channel'],
            "card": self.body['card'],
            "mobile": self.body['mobile'],
            "trx_ref": self.body['trx_ref'],
            "trx_date": self.body['trx_date'],
            "amount": self.body['amount'],
            "reciever_wallet": self.body['reciever_wallet'],
            "recieve_amount": self.body['recieve_amount'],
            "status": self.body['status'],
            "email_for": self.body['email_for']
        }

        body = render_to_string('main/email/deposit.html', context)
        
        new_email = EmailMessage(
            self.subject,
            body,
            self.email,
            [self.reciever],
        )
        new_email.content_subtype = 'html'

        try:
            generate_recipt = Recipt(
                sender = "",
                reciever = "",
                trx_id = "",
                trx_date = context['trx_date'],
                amount = decimal.Decimal(context['amount']),
                charges = 0,
                reciever_wallet = context['reciever_wallet'],
                reciever_amount = context['recieve_amount'],
                status = context['status'],
                email_for = context['email_for'],
                channel = context['channel'],
                card = context['card'],
                mobile = context['mobile'],
                trx_ref = context['trx_ref']
            )
            generate_recipt.save()
        except IntegrityError:
            pass

        EmailThread(new_email).start()

    def email_request(self):

        self.subject = "Request Alert"

        context = {
            "sender": self.body['sender'],
            "reciever": self.body['reciever'],
            "trx_date": self.body['trx_date'],
            "amount": self.body['amount'],
            "reciever_wallet": self.body['reciever_wallet'],
            "recieve_amount": self.body['recieve_amount'],
            "email_for": self.body['email_for']
        }

        body = render_to_string('main/email/request.html', context)
        
        new_email = EmailMessage(
            self.subject,
            body,
            self.email,
            [self.reciever],
        )
        new_email.content_subtype = 'html'

        try:
            generate_recipt = Recipt(
                sender = context['sender'],
                reciever = context['reciever'],
                trx_id = "",
                trx_date = context['trx_date'],
                amount = decimal.Decimal(context['amount']),
                charges = 0,
                reciever_wallet = context['reciever_wallet'],
                reciever_amount = context['recieve_amount'],
                status = "",
                email_for = context['email_for'],
                channel = "",
                card = "",
                mobile = "",
                trx_ref = ""
            )
            generate_recipt.save()
        except IntegrityError:
            pass

        EmailThread(new_email).start()

