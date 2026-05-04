from rest_framework.test import APITestCase
from rest_framework import status

from Authenticate.models import User
from Products.models import Product, Category
from .models import Cart

# Create your tests here.

class CartListTest(APITestCase):
    def setUp(self):
        self.vendor = User.objects.create_user(
            username = 'NewVendor',
            email = 'newvendor@gmail.com',
            password = 'VendorPass',
            role = 'vendor'
        )
        self.customer = User.objects.create_user(
            username = 'NewCustomer',
            email = 'newcustomer@gmail.com',
            password = 'CustomerPass',
            role = 'customer'
        )
        self.category = Category.objects.create(
            name = 'Electronic'
        )
        self.product_1 = Product.objects.create(
            name = 'NewProduct_1',
            description = 'New Product is cool',
            price = 120,
            stock = 10,
            category = self.category,
            vendor = self.vendor,
        )
        self.product_2 = Product.objects.create(
            name = 'NewProduct_2',
            description = 'New Product is cool',
            price = 120,
            stock = 10,
            category = self.category,
            vendor = self.vendor,
        )
        self.cart = Cart.objects.create(
            user = self.customer,
            product = self.product_1,
            quantity = 1
        )
        self.client.force_authenticate(user=self.customer)
    
    def test_get_cart_list_authenticate(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/carts/cart/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_cart_list_unauthenticate(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/carts/cart/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_add_product_to_cart_as_customer(self):
        data = {
            'user' : self.customer.id,
            'product' : self.product_2.id,
            'quantity' : 1
        }
        self.client.force_authenticate(user=self.customer)
        response = self.client.post('/carts/cart/add/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_add_product_to_cart_as_vendor(self):
        data = {
            'user' : self.customer.id,
            'product' : self.product_2.id,
            'quantity' : 1
        }
        self.client.force_authenticate(user=self.vendor)
        response = self.client.post('/carts/cart/add/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_duplicate_product_to_cart_as_customer(self):
        data = {
            'user' : self.customer.id,
            'product' : self.product_1.id,
            'quantity' : 1
        }
        self.client.force_authenticate(user=self.customer)
        response = self.client.post('/carts/cart/add/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CartDetailTest(APITestCase):
    def setUp(self):
        self.vendor = User.objects.create_user(
            username = 'NewVendor',
            email = 'newvendor@gmail.com',
            password = 'VendorPass',
            role = 'vendor'
        )
        self.customer_1 = User.objects.create_user(
            username = 'NewCustomer_1',
            email = 'newcustomer1@gmail.com',
            password = 'CustomerPass1',
            role = 'customer'
        )
        self.customer_2 = User.objects.create_user(
            username = 'NewCustomer_2',
            email = 'newcustomer2@gmail.com',
            password = 'CustomerPass2',
            role = 'customer'
        )
        self.category = Category.objects.create(
            name = 'Electronic'
        )
        self.product_1 = Product.objects.create(
            name = 'NewProduct_1',
            description = 'New Product is cool',
            price = 120,
            stock = 10,
            category = self.category,
            vendor = self.vendor,
        )
        self.product_2 = Product.objects.create(
            name = 'NewProduct_2',
            description = 'New Product is cool',
            price = 120,
            stock = 10,
            category = self.category,
            vendor = self.vendor,
        )
        self.cart = Cart.objects.create(
            user = self.customer_1,
            product = self.product_1,
            quantity = 1
        )
        self.client.force_authenticate(user=self.customer_1)
    
    def test_get_cart_detail(self):
        self.client.force_authenticate(user=self.customer_1)
        response = self.client.get(f'/carts/cart/{self.cart.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_product_quantity_as_customer(self):
        data = {
            'quantity' : 2
        }
        self.client.force_authenticate(user=self.customer_1)
        response = self.client.put(f'/carts/cart/{self.cart.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_update_product_quantity_as_vendor(self):
        data = {
            'quantity' : 2
        }
        self.client.force_authenticate(user=self.vendor)
        response = self.client.put(f'/carts/cart/{self.cart.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_remove_product_as_customer(self):
        self.client.force_authenticate(user=self.customer_1)
        response = self.client.delete(f'/carts/cart/{self.cart.id}/remove/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_remove_product_of_other_user(self):
        self.client.force_authenticate(user=self.customer_2)
        response = self.client.delete(f'/carts/cart/{self.cart.id}/remove/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)



