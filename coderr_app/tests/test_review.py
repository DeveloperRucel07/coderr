from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from auth_app.models import Profile
from coderr_app.models import Offer, OfferDetail, Order, Review


class ReviewTestCase(APITestCase):
    def setUp(self):
        self.customer_user = User.objects.create_user(username='admin', password='testpassword', email='admin@gmail.com')
        self.customer_user2 = User.objects.create_user(username='customer', password='testpassword', email='customer@gmail.com')
        self.business_user = User.objects.create_user(username='boss', password='testpassword', email='boss@gmail.com')
        self.business_user2 = User.objects.create_user(username='busy', password='testpassword', email='busy@gmail.com')
        
        self.admin_user = User.objects.create_superuser(username='staff', password='testpassword', email='staff@gmail.com')
        
        self.profile1 = Profile.objects.get(user = self.customer_user)
        self.profile2 = Profile.objects.get(user = self.business_user)
        self.profile3 = Profile.objects.get(user = self.business_user2)
        self.profile4 = Profile.objects.get(user = self.customer_user2)
        self.profile1.type = 'customer'
        self.profile2.type = 'business'
        self.profile3.type = 'business'
        self.profile4.type = 'customer'
        
        self.profile1.save()
        self.profile2.save()
        self.profile3.save()
        self.profile4.save()
        
        self.token = Token.objects.create(user = self.admin_user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        self.token1 = Token.objects.create(user = self.customer_user)
        self.client1 = APIClient()
        self.client1.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        self.token2 = Token.objects.create(user = self.business_user)
        self.client2 = APIClient()
        self.client2.credentials(HTTP_AUTHORIZATION='Token ' + self.token2.key)
        
        self.token3 = Token.objects.create(user = self.business_user2)
        self.client3 = APIClient()
        self.client3.credentials(HTTP_AUTHORIZATION='Token ' + self.token3.key)
        
        self.token4 = Token.objects.create(user = self.customer_user2)
        self.client4 = APIClient()
        self.client4.credentials(HTTP_AUTHORIZATION='Token ' + self.token4.key)
        
        self.review1 = Review.objects.create(business_user = self.business_user, reviewer = self.customer_user, rating = 3, description = 'no Problem, but you can do more.')
        self.review2 = Review.objects.create(business_user = self.business_user2, reviewer = self.customer_user2, rating = 3, description = 'no Problem, but you can do more.')
        
        
        
    def test_get_all_review(self):
        url = reverse('review-list')
        response = self.client1.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
    def test_customer_create_review(self):
        url = reverse('review-list')
        data = {
            'business_user': self.business_user2.id,
            'rating': 4,
            'description': 'Better service'
        }
        response = self.client1.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_business_create_review(self):
        url = reverse('review-list')
        data = {
            'business_user': self.business_user2.id,
            'rating': 4,
            'description': 'Better service'
        }
        response = self.client3.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_customner_patch_review(self):
        url = reverse('review-detail', kwargs={'pk': self.review2.id})
        data = {
            'rating': 5,
            'description':'Excellent'
        }
        response = self.client4.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.review2.refresh_from_db()
        self.assertEqual(self.review2.rating, 5)
        
    def test_customer_delete_review(self):
        url = reverse('review-detail', kwargs={'pk': self.review1.id})
        response = self.client1.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
    def test_customer_delete_review_not_reviewer(self):
        url = reverse('review-detail', kwargs={'pk': self.review1.id})
        response = self.client4.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_business_delete_review(self):
        url = reverse('review-detail', kwargs={'pk': self.review1.id})
        response = self.client2.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)