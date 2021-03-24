from django.urls import path
from . import views
app_name = "shadeboard"
urlpatterns = [
    path('', views.index, name="index"),
    path('adminportal', views.admin, name="adminportal"),
    path('adminportal/card-requests', views.card_requests, name="card-requests"),
    path('adminportal/card-requests/<int:id>', views.card_request, name="card-request"),
    path('adminportal/card-requests/<int:id>/reference', views.card_request_reference, name="card-request-reference"),
    path('adminportal/cardless-requests', views.cardless_requests, name="cardless-requests"),
    path('adminportal/cardless-requests/<int:id>', views.cardless_request, name="cardless-request"),
    path('adminportal/cardless-requests/<int:id>/reference', views.cardless_request_reference, name="cardless-request-reference"),
    path('adminportal/recipts', views.recipts, name="recipts"),
    path('adminportal/recipts/<int:id>', views.recipt, name="recipt")
]