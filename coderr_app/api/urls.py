from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import  OfferListCreateView, ReviewViewSet, OrderViewSet, BaseInfoView, OfferDetailView, OrderCountView, CompletedOrderCountView

router = DefaultRouter()
router.register( r'offers', OfferListCreateView, basename='offer')
router.register( r'orders', OrderViewSet, basename='order')
router.register( r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls) ),
    path('base-info/', BaseInfoView.as_view() , name = 'base-info'),
    path('offerdetails/<int:pk>/', OfferDetailView.as_view() ,name = 'offerdetail-detail'),
    path('order-count/<int:business_user_id>/', OrderCountView.as_view(), name = 'order-count'),
    path('completed-order-count/<int:business_user_id>/',CompletedOrderCountView.as_view(), name = 'completed-order-count'),
    
]