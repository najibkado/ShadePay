from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

@login_required
def payment_view(request, wallet):
    return HttpResponse(f"Hello There {wallet}")