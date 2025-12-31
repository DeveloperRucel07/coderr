from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import  OfferListCreateView

router = DefaultRouter()
router.register( r'offers',OfferListCreateView,basename='offer')

urlpatterns = [
    path('', include(router.urls) )
    
]