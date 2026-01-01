from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from coderr_app.models import Offer, Review, OfferDetail
from .serializers import BaseInfoSerialiser, OfferDetailSerializer, OrderCreateSerializer, OfferListSerializer, OfferSerializer, OrderSerializer, OrderStatusUpdateSerializer, ReviewCreateSerializer, ReviewSerializer, OfferDetailOrderSerializer
from .permissions import IsBusinessUserOrOwnerOrReadOnly, IsCustomerReviewer, IsReviewOwnerOrReadOnly


class OfferListCreateView(ModelViewSet):
    queryset = Offer.objects.prefetch_related('details')
    
    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        if self.action == 'retrieve':
            return [IsAuthenticated()]
        if self.action == 'create':
            return [IsAuthenticated(), IsBusinessUserOrOwnerOrReadOnly()]
        if self.action in ['partial_update', 'destroy']:
            return [IsAuthenticated(), IsBusinessUserOrOwnerOrReadOnly()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OfferListSerializer
        if self.action == 'retrieve':
            return OfferDetailSerializer
        if self.action == 'create':
            return OfferSerializer
        return OfferDetailSerializer


class OfferDetailView(RetrieveAPIView):
    serializer_class = OfferDetailOrderSerializer
    permission_classes  = [IsAuthenticated]
    queryset = OfferDetail.objects.all()
    

class OrderViewSet(ModelViewSet):
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {'request': self.request}

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        if self.action == 'partial_update':
            return OrderStatusUpdateSerializer
        return OrderSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        
        return Response( OrderSerializer(order).data, status=status.HTTP_201_CREATED)

class OrderCountView(APIView):
    pass


class CompletedOrderCountView(APIView):
    pass

class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    permission_classes = [IsCustomerReviewer, IsReviewOwnerOrReadOnly, IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return ReviewCreateSerializer
        return ReviewSerializer

class BaseInfoView(APIView):
    permission_classes = [AllowAny]
    serializer_class = BaseInfoSerialiser
    
