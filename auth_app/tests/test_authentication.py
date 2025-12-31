from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from auth_app.models import  Profile


class UserRegistrationTest(APITestCase):
    
    def setUp(self):
        self.url = reverse('registration')
        self.valid_data = {
            'username': 'TestUser',
            'email': 'example@mail.de',
            'password': 'examplePassword',
            'repeated_password': 'examplePassword',
            'type': 'customer',
        }
 
    def test_user_registration_creates_profile(self):
        response = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='TestUser').exists())
        user = User.objects.get(username='TestUser')
        self.assertTrue(Profile.objects.filter(user=user).exists())
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.type, 'customer')
        self.assertTrue(user.check_password('examplePassword'))
        
class UserLoginTest(APITestCase):
    def setUp(self):
        self.url = reverse('login')
        self.password = 'examplePassword'
        self.user= User.objects.create_user(username= 'TestUser', password = self.password)
    
    def test_login_success(self):
        data = {
            'username': self.user.username,
            'password': self.password
        }
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_errors(self):
        data = {
            'username': self.user.username,
            'password': 'ThisIsTheWrongPassword'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)