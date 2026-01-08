from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from auth_app.models import Profile
from coderr_app.models import Offer, OfferDetail, Order


class OrderTestCase(APITestCase):
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
        
        self.offer = Offer.objects.create(user=self.business_user, title='Fullstack developement', description = 'create performant  for your app and performant Backend to store your cusytomer data for better analysis...')
        self.offer2 = Offer.objects.create(user=self.business_user2, title='Modern developement', description = 'create robust an performamnte Apps and AI automations')
        
        self.basic = OfferDetail.objects.create(offer = self.offer, title = 'Basic Model', revisions = 3, delivery_time_in_days = 5, price = 500, features= ['simple_website', 'simple dashbord'], offer_type = 'basic')
        self.standard = OfferDetail.objects.create(offer = self.offer, title = 'Standard Model', revisions = 5, delivery_time_in_days = 7, price = 1000, features= ['simple_website', 'Custom dashbord', 'customer Service' ], offer_type = 'standard')
        self.premium = OfferDetail.objects.create(offer = self.offer, title = 'Premium Model', revisions = 8, delivery_time_in_days = 10, price = 3000, features= ['custom design','simple_website', 'Custom dashbord', 'customer Service'], offer_type = 'premium')
        
        self.basic2 = OfferDetail.objects.create(offer = self.offer2, title = 'Basic Model', revisions = 3, delivery_time_in_days = 5, price = 1500, features= ['simple_website', 'simple dashbord', 'chatbot'], offer_type = 'basic')
        self.standard2 = OfferDetail.objects.create(offer = self.offer2, title = 'Standard Model', revisions = 5, delivery_time_in_days = 7, price = 5000, features= ['simple_website', 'Custom dashbord', 'customer Service', 'chatbot' ], offer_type = 'standard')
        self.premium2 = OfferDetail.objects.create(offer = self.offer2, title = 'Premium Model', revisions = 8, delivery_time_in_days = 10, price = 10000, features= ['custom design','chatbot', 'Custom dashbord', 'customer Service', 'AI automation'], offer_type = 'premium')

        self.order1 = Order.objects.create(
            offer_detail = self.basic,
            customer_user = self.customer_user,
            business_user = self.offer.user,
            title = self.basic.title,
            revisions=self.basic.revisions,
            delivery_time_in_days=self.basic.delivery_time_in_days,
            price=self.basic.price,
            features=self.basic.features,
            offer_type=self.basic.offer_type,
        )
        self.order2 = Order.objects.create(
            offer_detail = self.premium2,
            customer_user = self.customer_user,
            business_user = self.offer2.user,
            title = self.premium2.title,
            revisions=self.premium2.revisions,
            delivery_time_in_days=self.premium2.delivery_time_in_days,
            price=self.premium2.price,
            features=self.premium2.features,
            offer_type=self.premium2.offer_type,
        )
        self.order3 = Order.objects.create(
            offer_detail = self.standard2,
            customer_user = self.customer_user2,
            business_user = self.offer2.user,
            title = self.standard2.title,
            revisions=self.standard2.revisions,
            delivery_time_in_days=self.standard2.delivery_time_in_days,
            price=self.standard2.price,
            features=self.standard2.features,
            offer_type=self.standard2.offer_type,
        )
        self.order4 = Order.objects.create(
            offer_detail = self.premium,
            customer_user = self.customer_user2,
            business_user = self.offer.user,
            title = self.premium.title,
            revisions=self.premium.revisions,
            delivery_time_in_days=self.premium.delivery_time_in_days,
            price=self.premium.price,
            features=self.premium.features,
            offer_type=self.premium.offer_type,
        )
        
    def test_get_all_order(self):
        """
        Test that a business user can retrieve all their orders.
        """
        url = reverse('order-list')
        response = self.client2.get(url) # 'client2' customer or business user can only see they orders.
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_customer_create_order(self):
        """
        Test that a customer can create an order for an offer detail.
        """
        url = reverse('order-list')
        data = {
            'offer_detail_id': self.premium2.id
        }
        response = self.client4.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    def test_business_create_order(self):
        """
        Test that a business user cannot create an order for their own offer.
        """
        url = reverse('order-list')
        data = {
            'offer_detail_id': self.premium.id
        }
        response = self.client3.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_customer_get_order_detail(self):
        """
        Test that a customer can retrieve details of their order.
        """
        url = reverse('order-detail', kwargs={'pk': self.order3.id})
        response = self.client4.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
    def test_business_and_owner_patch(self):
        """
        Test that a business user and owner can update the order status.
        """
        url = reverse('order-detail', kwargs={'pk': self.order3.id})
        data = {
            'status': 'completed'
        }
        response = self.client3.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order3.refresh_from_db()
        self.assertEqual(self.order3.status, 'completed')

    def test_admin_staff_delete(self):
        """
        Test that an admin staff can delete an order.
        """
        url = reverse('order-detail', kwargs={'pk': self.order3.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Order.objects.filter(id=self.order3.id).exists())
    
    