from django.urls import path
from .views import LoginView, RegistrationView, LogoutView, ProfilesBusinessListView, ProfilesCustomerListView, UserProfileGetUpdateView
urlpatterns = [
    path('login/',LoginView.as_view(), name = 'login'),
    path('registration/',RegistrationView.as_view(), name='registration'),
    path('logout/', LogoutView.as_view(), name = 'logout'),
    path('profile/<int:pk>/', UserProfileGetUpdateView.as_view(), name = 'profile-detail'),
    path('profiles/customer/', ProfilesCustomerListView.as_view(), name = 'profiles-list-customer'),
    path('profiles/business/', ProfilesBusinessListView.as_view(), name = 'profiles-list-business'),
]