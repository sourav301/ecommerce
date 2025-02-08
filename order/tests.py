from django.test import TestCase

from django.contrib.auth.models import User, Group
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from rest_framework.authtoken.models import Token


class EcommerceAPITestCase(APITestCase):

    def setUp(self):
        """
        Create test users and assign them to groups.
        """
        # Create groups
        self.stock_manager_group, _ = Group.objects.get_or_create(name='stock_manager')
        self.customer_group, _ = Group.objects.get_or_create(name='customer')

        # Create stock manager user
        self.stock_manager = User.objects.create_user(username='stockmanager1', password='testpass')
        self.stock_manager.groups.add(self.stock_manager_group)
        self.stock_manager_token, _ = Token.objects.get_or_create(user=self.stock_manager)


        # Create customer user
        self.customer = User.objects.create_user(username='customer1', password='testpass')
        self.customer.groups.add(self.customer_group)
        self.customer_token, _ = Token.objects.get_or_create(user=self.customer)

        # Create an unauthenticated user
        self.unauthenticated_user = User.objects.create_user(username='guest', password='testpass')

        # API endpoints
        self.add_product_url = reverse('Create Product')  # Replace with actual name from urls.py
        self.add_to_cart_url = reverse('add_to_cart')  # Replace with actual name from urls.py
        self.add_category_url = reverse('Create Category')  # Replace with actual name from urls.py

        response = self.client.post(self.add_category_url,{
                                                            "name": "Electronics",
                                                            "desc": "Devices and gadgets"
                                                        })
        category_data = {
            "name": "Electronics",
            "description": "Electronic gadgets"
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.stock_manager_token.key)  # Add token
        
        category_response = self.client.post(self.add_category_url, category_data) 
        self.assertEqual(category_response.status_code, status.HTTP_201_CREATED) 
        self.category_id = category_response.data["id"]  # Extract category ID

        self.product_url = reverse("Create Product")
        self.product_data = {
            "name": "Smart Watch",
            "description": "Watch tells time",
            "price": 100.99,
            "stock": 10,
            "category": self.category_id
        }
 

    def test_stock_manager_can_add_category(self):
        """
        Ensure only stock managers can add products.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.stock_manager_token.key)  # Add token
        response = self.client.post(self.add_category_url,{
                                                            "name": "Electronics",
                                                            "desc": "Devices and gadgets"
                                                        })
        print("---------------",response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_stock_manager_can_create_product(self):
        """
        Ensure only stock managers can add products.
        """
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.stock_manager_token.key)  # Add token
        response = self.client.post(self.add_product_url, {
                                        "name": "Smart watch",
                                        "description": "Watch tells time",
                                        "price": 100.99,
                                        "stock": 10,
                                        "category": self.category_id
                                    })
        print(response.status_code,"---------------",response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
   
    
        
    
