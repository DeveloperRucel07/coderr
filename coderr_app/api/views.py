from django.db.models import Q, Count, Avg
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from auth_app.models import Profile
from coderr_app.models import Offer, Review, OfferDetail, Order
from .filters import OfferFilter
from .limit_paginations import OfferPagination
from .serializers import  OfferDetailSerializer, OfferUpdateSerializer, OrderCreateSerializer, OfferListSerializer, OfferSerializer, OrderSerializer, OrderStatusUpdateSerializer, ReviewSerializer, OfferDetailOrderSerializer
from .permissions import IsAdminOrStaff, IsBusinessOrCustomerUser, IsBusinessUserOrOwnerOrReadOnly, IsBusinessUserOrder, IsCustomerReviewer, IsReviewOwnerOrReadOnly


class OfferModelViewSet(ModelViewSet):
    """
    ViewSet for managing offers.

    Handles offer creation, listing, updating, and deletion with appropriate permissions.
    Supports filtering, searching, and ordering.
    """
    queryset = Offer.objects.prefetch_related('details')
    pagination_class = OfferPagination
    filter_backends = [ DjangoFilterBackend, SearchFilter, OrderingFilter ]
    filterset_class = OfferFilter
    search_fields = ['title', 'description' ]
    ordering_fields = [ 'updated_at',  'min_price' ]
    ordering = ['-updated_at']
    
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
        if self.action == 'partial_update':
            return OfferUpdateSerializer
        return OfferDetailSerializer


class OfferDetailView(RetrieveAPIView):
    """
    API view for retrieving a single offer detail.

    Requires authentication to access.
    """
    serializer_class = OfferDetailOrderSerializer
    permission_classes  = [IsAuthenticated]
    queryset = OfferDetail.objects.all()
    

class OrderViewSet(ModelViewSet):
    """
    ViewSet for managing orders.

    Handles order creation, listing, updating, and deletion with appropriate permissions.
    """
    serializer_class = OrderCreateSerializer
    
    def get_queryset(self):
        user  = self.request.user
        if self.action == 'destroy':
            return Order.objects.all()
        return Order.objects.filter(Q(customer_user=user) | Q(business_user=user))

    def get_serializer_context(self):
        return {'request': self.request}
    
    def get_permissions(self):
        if self.action == 'list':
            return [IsBusinessOrCustomerUser()]
        if self.action == 'retrieve':
            return [IsAuthenticated(), IsBusinessUserOrOwnerOrReadOnly(), IsBusinessOrCustomerUser()]
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
            return Response({'detail':'You dont have permission to perform this action'}, status=status.HTTP_403_FORBIDDEN)
        serialiser = self.get_serializer(order, data = request.data)
        serialiser.is_valid(raise_exception=True)
        data = serialiser.save()
        return Response( OrderSerializer(data).data, status=status.HTTP_200_OK)
    

class OrderCountView(APIView):
    """
    API view to get the count of in-progress orders for a business user.

    Requires authentication.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        user = get_object_or_404(User, id=business_user_id)

        if not hasattr(user, 'profile') or user.profile.type != 'business':
            return Response({'detail': 'The user is not found or is not a business user.'},status=status.HTTP_404_NOT_FOUND)
        
        count = Order.objects.filter( business_user=user, status='in_progress').count()

        return Response({'order-count': count}, status=status.HTTP_200_OK)


class CompletedOrderCountView(APIView):
    """
    API view to get the count of completed orders for a business user.

    Requires authentication.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        user = get_object_or_404(User, id=business_user_id)

        if not hasattr(user, 'profile') or user.profile.type != 'business':
            return Response({'detail': 'The user is not found or is not a business user.'},status=status.HTTP_404_NOT_FOUND)
        
        count = Order.objects.filter( business_user=user, status='completed').count()

        return Response({'completed_order_count': count}, status=status.HTTP_200_OK)


class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    permission_classes = [IsCustomerReviewer, IsReviewOwnerOrReadOnly]
    serializer_class = ReviewSerializer


class BaseInfoView(APIView):
    """
    API view to get basic information about the platform.

    Includes review count, average rating, business profile count, and offer count.
    Accessible without authentication.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        data = {}
        review_stats = Review.objects.aggregate(review_count = Count('id'), average_rating = Avg('rating'))
        data['review_count'] = review_stats['review_count']
        data['average_rating'] = (round(review_stats['average_rating'], 1) if review_stats['average_rating'] is not None else 0)
        
        data['business_profile_count'] = Profile.objects.filter(type = 'business').count()
        data['offer_count'] = Offer.objects.count()
        return Response(data, status=status.HTTP_200_OK)
        
    
    
    
    
    
