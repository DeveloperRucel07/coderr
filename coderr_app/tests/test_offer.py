from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from auth_app.models import Profile
from coderr_app.models import Offer, OfferDetail

class OfferTestCase(APITestCase):
    
    def setUp(self):
        self.customer_user = User.objects.create_user(username='admin', password='testpassword', email='admin@gmail.com')
        self.business_user = User.objects.create_user(username='boss', password='testpassword', email='boss@gmail.com')
        self.business_user2 = User.objects.create_user(username='busy', password='testpassword', email='busy@gmail.com')
        
        self.profile1 = Profile.objects.get(user = self.customer_user)
        self.profile2 = Profile.objects.get(user = self.business_user)
        self.profile3 = Profile.objects.get(user = self.business_user2)
        self.profile1.type = 'customer'
        self.profile2.type = 'business'
        self.profile3.type = 'business'
        
        self.profile1.save()
        self.profile2.save()
        self.profile3.save()
        
        self.token1 = Token.objects.create(user = self.customer_user)
        self.client1 = APIClient()
        self.client1.credentials(HTTP_AUTHORIZATION='Token ' + self.token1.key)
        
        self.token2 = Token.objects.create(user = self.business_user)
        self.client2 = APIClient()
        self.client2.credentials(HTTP_AUTHORIZATION='Token ' + self.token2.key)
        
        self.token3 = Token.objects.create(user = self.business_user2)
        self.client3 = APIClient()
        self.client3.credentials(HTTP_AUTHORIZATION='Token ' + self.token3.key)
        
        self.offer = Offer.objects.create(user=self.business_user, title='Fullstack developement', description = 'create performant  for your app and performant Backend to store your cusytomer data for better analysis...')
        
        self.basic = OfferDetail.objects.create(offer = self.offer, title = 'Basic Model', revisions = 3, delivery_time_in_days = 5, price = 500, features= ['simple_website', 'simple dashbord'], offer_type = 'basic')
        self.standard = OfferDetail.objects.create(offer = self.offer, title = 'Standard Model', revisions = 5, delivery_time_in_days = 7, price = 1000, features= ['simple_website', 'Custom dashbord', 'customer Service' ], offer_type = 'standard')
        self.premium = OfferDetail.objects.create(offer = self.offer, title = 'Premium Model', revisions = 8, delivery_time_in_days = 10, price = 3000, features= ['custom design','simple_website', 'Custom dashbord', 'customer Service'], offer_type = 'premium')
        
    def test_get_all_offer(self):
        url = reverse('offer-list')
        response = self.client1.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
        
    def test_unauthenticated_create_offer(self):
        url = reverse('offer-list')
        data = {
            'title': 'New Offer',
            'description': 'Test',
            'details': []
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_customer_create_offer(self):
        url = reverse('offer-list')
        data = {
            'title': 'New Offer',
            'description': 'Test',
            'details': []
        }
        response = self.client1.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_business_create_offer(self):
        url = reverse('offer-list')

        data = {
            'title': 'New Offer',
            'description': 'New Description',
            'details': [
                {
                    'title': 'Basic',
                    'revisions': 1,
                    'delivery_time_in_days': 3,
                    'price': 50,
                    'features': ['Logo'],
                    'offer_type': 'basic',
                },
                {
                    'title': 'Standard',
                    'revisions': 3,
                    'delivery_time_in_days': 5,
                    'price': 150,
                    'features': ['Logo', 'Card'],
                    'offer_type': 'standard',
                },
                {
                    'title': 'Premium',
                    'revisions': 6,
                    'delivery_time_in_days': 7,
                    'price': 300,
                    'features': ['Logo', 'Card', 'Flyer'],
                    'offer_type': 'premium',
                },
            ],
        }

        response = self.client2.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Offer.objects.count(), 2)
        
    def test_owner_patch_offer(self):
        url = reverse('offer-detail',  kwargs={'pk': self.offer.id})
        
        data = {
            'title':'Modern Developement',
            'details':[
                {
                    'title': 'Modern Basic developement for Mobile and Web App',
                    'offer_type': 'basic',
                    'price':'750'
                },
                {
                    'title': 'Modern Standard developement for Mobile and Web App',
                    'offer_type': 'standard',
                    'price':'1250'
                }
            ]
        }
        response = self.client2.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.offer.refresh_from_db()
        self.basic.refresh_from_db()
        self.standard.refresh_from_db()
        self.assertEqual(self.offer.title, 'Modern Developement')
        self.assertEqual(self.basic.price, 750)
        self.assertEqual(self.standard.price, 1250)
        
    def test_customer_patch(self):
        url = reverse('offer-detail',  kwargs={'pk': self.offer.id})
        data = {
            'title': 'Customer can not patch offer',
            'description': 'only business and owner can patch this offer'
        }
        
        response = self.client1.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_not_owner_delete(self):
        url = reverse('offer-detail',  kwargs={'pk': self.offer.id})
        response = self.client3.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
                  
    def test_owner_delete(self):
        url = reverse('offer-detail',  kwargs={'pk': self.offer.id})
        response = self.client2.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Offer.objects.count(), 0)
                
    
            
        
        
        
        
        
