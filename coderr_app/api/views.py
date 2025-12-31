from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView, CreateAPIView, ListCreateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from coderr_app.models import Offer
from .serializers import OrderCreateSerializer, OfferListSerializer, OfferSerializer
from .permissions import IsBusinessUserOrOwnerOrReadOnly


class OfferListCreateView(ModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly, IsBusinessUserOrOwnerOrReadOnly]
    queryset = Offer.objects.prefetch_related("details")
    
    def get_serializer_class(self):
        if self.action == "create":
            return OfferSerializer
        return OfferListSerializer


class OrderCreateView(CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        
        return Response( OrderSerializer(order).data, status=status.HTTP_201_CREATED)

