from django.db.models import Q
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.generics import RetrieveAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from coderr_app.models import Offer, Review, OfferDetail, Order
from .serializers import BaseInfoSerialiser, OfferDetailSerializer, OrderCreateSerializer, OfferListSerializer, OfferSerializer, OrderSerializer, OrderStatusUpdateSerializer, ReviewCreateSerializer, ReviewSerializer, OfferDetailOrderSerializer
from .permissions import IsAdminOrStaff, IsBusinessOrCustomerUser, IsBusinessUserOrOwnerOrReadOnly, IsBusinessUserOrder, IsCustomerReviewer, IsReviewOwnerOrReadOnly


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
    
    def get_queryset(self):
        user  = self.request.user
        return Order.objects.filter(Q(customer_user=user) | Q(business_user=user))
    

    def get_serializer_context(self):
        return {'request': self.request}
    
    def get_permissions(self):
        if self.action == 'list':
            return [IsBusinessOrCustomerUser()]
        if self.action == 'retrieve':
            return [IsAuthenticated(), IsBusinessUserOrOwnerOrReadOnly()]
        if self.action == 'create':
            return [IsAuthenticated(), IsCustomerReviewer()]
        if self.action == 'partial_update':
            return [IsAuthenticated(), IsBusinessUserOrder(), IsBusinessOrCustomerUser()]
        if self.action == 'destroy':
            return [IsAuthenticated(), IsAdminOrStaff()]
        return [IsBusinessOrCustomerUser()]

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
    
    def partial_update(self, request, *args, **kwargs):
        order = self.get_object()
        user = request.user
        if user != order.business_user:
            return Response({'detail':'Yopu dont have permission to perform this action'}, status=status.HTTP_403_FORBIDDEN)
        serialiser = self.get_serializer(order, data = request.data)
        serialiser.is_valid(raise_exception=True)
        data = serialiser.save()
        return Response( OrderSerializer(data).data, status=status.HTTP_200_OK)
    

class OrderCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        user = get_object_or_404(User, id=business_user_id)

        if not hasattr(user, 'profile') or user.profile.type != 'business':
            return Response({'detail': 'The user is not found or is not a business user.'},status=status.HTTP_404_NOT_FOUND)
        
        count = Order.objects.filter( business_user=user, status='in_progress').count()

        return Response({'order-count': count}, status=status.HTTP_200_OK)


class CompletedOrderCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        user = get_object_or_404(User, id=business_user_id)

        if not hasattr(user, 'profile') or user.profile.type != 'business':
            return Response({'detail': 'The user is not found or is not a business user.'},status=status.HTTP_404_NOT_FOUND)
        
        count = Order.objects.filter( business_user=user, status='completed').count()

        return Response({'completed_order_count': count}, status=status.HTTP_200_OK)


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
    
