from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from api.serializers.merchant_serializer import MerchantRequestSerializer
from rest_framework.response import Response
from rest_framework import status
from main.utils import get_domain

class Merchant_View(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MerchantRequestSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            domain = get_domain(request)
            domain = domain + f"/merchant/c/checkout/{serializer.data['id']}"
            return Response({"url": domain}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
