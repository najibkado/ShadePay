from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

@login_required
def payment_view(request, wallet):
    return HttpResponseRedirect(reverse('main:index'))