from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type
from django.contrib.sites.shortcuts import get_current_site
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.gis.geoip2 import GeoIP2
import decimal


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    
    def _make_hash_value(self, user, timestamp):
        return (text_type(user.is_active) + text_type(user.pk) + text_type(timestamp))

email_token_generator = EmailVerificationTokenGenerator()

def get_domain(request):
    return "https://" + get_current_site(request).domain

def validate(e):
    try:
        validate_email(e)
        return True
    except ValidationError:
        return False

def get_ip(req):
    
    try:
        x_http = req.META.get('HTTP_X_FORWARDER_FOR') 
        j = req.META.get('HTTP_X_REAL_IP')

        if j:
            ip = j
        elif x_http:
            ip = x_http.split(",")[0]
        else:
            ip = req.META.get('REMOTE_ADDR')

    except:
        ip = ""

    return ip


def get_client(req):

    try:
        u_agent = req.META.get('HTTP_USER_AGENT')

        if u_agent:
            return u_agent
        else:
            u_agent = ""

    except:
        u_agent = ""

    return u_agent

def get_geol(ip):
    g = GeoIP2()

    try:
        lon, lat = g.lon_lat(ip)
    except:
        lon, lat = "", ""

    try:
        city = g.city(ip)
    except:
        city = ""

    try:
        country = g.country(ip)
    except:
        country = ""

    return lon, lat, city, country


def get_cot(amount):
    """
    Returns the cost of transaction = 1.25% of the amount
    """
    cot = (amount / 100) * decimal.Decimal(1.25)

    return cot


def get_tc(amount):
    """
    Returns the transaction charges = NGN 20
    """
    return 20


def get_internal_tc(amount):
    """
    Returns the transaction charges for internal transactions = 1.25% + NGN 20
    """

    cot = (amount / 100) * decimal.Decimal(1.25)

    tc = cot + 20

    return decimal.Decimal(3500) if tc >= decimal.Decimal(3500) else tc




