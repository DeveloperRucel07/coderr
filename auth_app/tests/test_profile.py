from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from auth_app.models import Profile

class TestProfile(APITestCase):
    
    def setUp(self):
        self.user1 = User.objects.create_user(username='devlogo', password='testpassword', email='devlogo@gmail.com')
        self.user2 = User.objects.create_user(username='dev', password='testpassword', email='userdev@gmail.com')
        self.user3 = User.objects.create_user(username='admin', password='testpassword', email='admin@gmail.com')
        self.user4 = User.objects.create_user(username='boss', password='testpassword', email='boss@gmail.com')
        
        self.profile1 = Profile.objects.get(user = self.user1)
        self.profile2 = Profile.objects.get(user = self.user2)
        self.profile3 = Profile.objects.get(user = self.user3)
        self.profile4 = Profile.objects.get(user = self.user4)
        
        self.profile1.type = 'customer'
        self.profile2.type = 'customer'
        self.profile3.type = 'business'
        self.profile4.type = 'business'
        
        self.profile1.save()
        self.profile2.save()
        self.profile3.save()
        self.profile4.save()
        
        self.url_user1 = reverse('profile-detail', kwargs={'pk': self.user1.profile.pk})
        self.url_user2 = reverse('profile-detail', kwargs={'pk': self.user2.profile.pk})
        self.url_user3 = reverse('profile-detail', kwargs={'pk': self.user3.profile.pk})
        self.url_user4 = reverse('profile-detail', kwargs={'pk': self.user4.profile.pk})
        
        self.token = Token.objects.create(user = self.user3)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
    def test_get_all_business(self):
        url = reverse('profiles-list-business')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_get_all_customer(self):
        url = reverse('profiles-list-customer')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    
    def test_get_detail_profile(self):
        response = self.client.get(self.url_user1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        
    def test_patch_owner_profile(self):
        data = {
            'description': 'python backend software developer',
            'location': 'Berlin'
        }
        response = self.client.patch(self.url_user3, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user3.profile.refresh_from_db()
        self.assertEqual(self.user3.profile.description, 'python backend software developer')
        self.assertEqual(self.user3.profile.location, 'Berlin')
    
    
    def test_put_owner_profile(self):
        data = {
            'username': 'max_mustermann',
            'first_name': 'Max',
            'last_name': 'Mustermann',
            'file': 'profile_picture.jpg',
            'location': 'Berlin',
            'tel': '123456789',
            'description': 'Business description',
            'working_hours': '9-17',
            'type': 'business',
            'email': 'max@business.de',
        }
        response = self.client.put(self.url_user3, data, format = 'json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        
          
    def test_patch_others_profile(self):
        data = {
            'description': 'python backend software developer',
            'location': 'Berlin'
        }
        response = self.client.patch(self.url_user2, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.user2.profile.refresh_from_db()
        self.assertNotEqual(self.profile2.description, 'python backend software developer' )
        self.assertNotEqual(self.profile2.location, 'Berlin')
        
        
        
        
