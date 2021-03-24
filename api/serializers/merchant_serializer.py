from rest_framework import serializers
from api.models import MerchantRequest

class MerchantRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MerchantRequest
        fields = [
            'id',
            'wallet',
            'amount',
            'description',
            'status',
            'approved',
            'ip',
            'returnUrl'
        ]