from rest_framework import serializers
from api.models import ShadepayRequest

class ShadepayRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShadepayRequest
        fields = [
            'id',
            'wallet',
            'amount',
            'quantity',
            'products',
            'products_description',
            'status',
            'returnUrl'
        ]
