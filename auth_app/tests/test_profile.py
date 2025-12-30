from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from auth_app.models import Profile

class TestProfile(APITestCase):
    
    def setUp(self):
        self.user1 = User.objects.create_user(username='devlogo', password='testpassword', email='devlogo@gmail.com', type = 'customer')
        self.user2 = User.objects.create_user(username='dev', password='testpassword', email='userdev@gmail.com' , type = 'customer')
        self.user3 = User.objects.create_user(username='admin', password='testpassword', email='admin@gmail.com' , type = 'business')
        self.user4 = User.objects.create_user(username='boss', password='testpassword', email='boss@gmail.com' , type = 'business')
        
        self.profile1 = Profile.objects.get(user = self.user1)
        self.profile2 = Profile.objects.get(user = self.user2)
        self.profile3 = Profile.objects.get(user = self.user3)
        self.profile4 = Profile.objects.get(user = self.user4)
        
        # self.token = Token.objects.create(user = self.user)
        # self.client = APIClient()
        # self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        # profile-detail, profiles-list-business
    def test_get_all_business(self):
        url = reverse('profiles-list-business')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        
