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


class OrderStatusUpdateTest(APITestCase):
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

    def test_update_order_status_as_admin(self):
        data = {
            'status' : 'confirmed'
        }
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(f'/orders/{self.order.id}/status/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_order_status_as_customer(self):
        data = {
            'status' : 'confirmed'
        }
        self.client.force_authenticate(user=self.customer)
        response = self.client.put(f'/orders/{self.order.id}/status/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_order_status_as_vendor(self):
        data = {
            'status' : 'confirmed'
        }
        self.client.force_authenticate(user=self.vendor)
        response = self.client.put(f'/orders/{self.order.id}/status/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_order_id(self):
        data = {
            'status': 'confirmed'
        }
        self.client.force_authenticate(user=self.vendor)
        response = self.client.put(f'/orders/item/999/status/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_update_invalid_status(self):
        data = {
            'status' : 'out for delivery'
        }
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(f'/orders/{self.order.id}/status/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_cancelled_order(self):
        self.order.status = 'cancelled'
        self.order.save()
        data = {
            'status': 'shipped'
        }
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(f'/orders/{self.order.id}/status/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class OrderItemStatusUpdateTest(APITestCase):
    def setUp(self):
        self.vendor_1 = User.objects.create_user(
            username='vendor01',
            email='vendor01@gmail.com',
            password='vendor01pass',
            role='vendor'
        )
        self.vendor_2 = User.objects.create_user(
            username='vendor02',
            email='vendor02@gmail.com',
            password='vendor02pass',
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
            vendor=self.vendor_1
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
    
    def test_update_item_status_as_vendor(self):
        data = {
            'status' : 'confirmed'
        }
        self.client.force_authenticate(user=self.vendor_1)
        response = self.client.put(f'/orders/item/{self.item.id}/status/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_item_status_as_customer(self):
        data = {
            'status' : 'confirmed'
        }
        self.client.force_authenticate(user=self.customer)
        response = self.client.put(f'/orders/item/{self.item.id}/status/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_item_status_as_othen_vendor(self):
        data = {
            'status' : 'confirmed'
        }
        self.client.force_authenticate(user=self.vendor_2)
        response = self.client.put(f'/orders/item/{self.item.id}/status/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_item_id(self):
        data = {
            'status': 'confirmed'
        }
        self.client.force_authenticate(user=self.vendor_1)
        response = self.client.put(f'/orders/item/999/status/', data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_invalid_status(self):
        data = {
            'status' : 'out for delivery'
        }
        self.client.force_authenticate(user=self.vendor_1)
        response = self.client.put(f'/orders/item/{self.item.id}/status/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_update_cancelled_item(self):
        self.item.status = 'cancelled'
        self.item.save()
        data = {
            'status': 'shipped'
        }
        self.client.force_authenticate(user=self.vendor_1)
        response = self.client.put(f'/orders/item/{self.item.id}/status/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



