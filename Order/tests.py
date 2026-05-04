from rest_framework.test import APITestCase
from rest_framework import status

from Products.models import Product , Category
from Authenticate.models import User , Address
from Order.models import Order , OrderItem

# Create your tests here.

class OrderListTest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@gmail.com',
            password='adminpass',
            role='admin'
        )
        self.vendor = User.objects.create_user(
            username='vendor',
            email='vendor@gmail.com',
            password='vendorpass',
            role='vendor'
        )
        self.customer = User.objects.create_user(
            username='customer',
            email='customer@gmail.com',
            password='customerpass',
            role='customer'
        )
        self.category = Category.objects.create(
            name='Electronics'
        )
        self.product = Product.objects.create(
            name='Laptop',
            description='Test product',
            price=50000,
            stock=10,
            category=self.category,
            vendor=self.vendor
        )
        self.address = Address.objects.create(
            user=self.customer,
            street='5-C scheme',
            city='Jaipur',
            state='Rajasthan',
            pincode='302001',
            phone='9999999999',
            label='home'
        )
        self.order = Order.objects.create(
            customer=self.customer,
            delivery_address=self.address,
            total_price=50000,
            status='pending'
        )
        self.client.force_authenticate(user=self.customer)
    
    def test_get_order_list_as_customer(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get('/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_order_list_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/orders/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_order_list_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/orders/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OrderDetailTest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@gmail.com',
            password='adminpass',
            role='admin'
        )
        self.vendor = User.objects.create_user(
            username='vendor',
            email='vendor@gmail.com',
            password='vendorpass',
            role='vendor'
        )
        self.customer = User.objects.create_user(
            username='customer',
            email='customer@gmail.com',
            password='customerpass',
            role='customer'
        )
        self.category = Category.objects.create(
            name='Electronics'
        )
        self.product = Product.objects.create(
            name='Laptop',
            description='Test product',
            price=50000,
            stock=10,
            category=self.category,
            vendor=self.vendor
        )
        self.address = Address.objects.create(
            user=self.customer,
            street='5-C scheme',
            city='Jaipur',
            state='Rajasthan',
            pincode='302001',
            phone='9999999999',
            label='home'
        )
        self.order = Order.objects.create(
            customer=self.customer,
            delivery_address=self.address,
            total_price=50000,
            status='pending'
        )
        self.item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            price=50000,
            status='pending'
        )
        self.client.force_authenticate(user=self.customer)
    
    def test_get_order_detail_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f'/orders/{self.order.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_order_detail_as_vendor(self):
        self.client.force_authenticate(user=self.vendor)
        response = self.client.get(f'/orders/{self.order.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_order_detail_as_customer(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.get(f'/orders/{self.order.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


