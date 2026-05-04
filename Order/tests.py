from rest_framework.test import APITestCase
from rest_framework import status

from Products.models import Product , Category
from Authenticate.models import User , Address
from Order.models import Order , OrderItem
from Carts.models import Cart

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


class OrderStatusCancelTest(APITestCase):
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
        self.customer_1 = User.objects.create_user(
            username='customer1',
            email='customer1@gmail.com',
            password='customer1pass',
            role='customer'
        )
        self.customer_2 = User.objects.create_user(
            username='customer2',
            email='customer2@gmail.com',
            password='customer2pass',
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
            user=self.customer_1,
            street='5-C scheme',
            city='Jaipur',
            state='Rajasthan',
            pincode='302001',
            phone='9999999999',
            label='home'
        )
        self.order = Order.objects.create(
            customer=self.customer_1,
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
        self.client.force_authenticate(user=self.customer_1)
    
    def test_customer_can_cancel_own_order(self):
        self.client.force_authenticate(user=self.customer_1)
        response = self.client.put(f'/orders/{self.order.id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_cannot_cancel_shipped_order(self):
        self.order.status = 'shipped'
        self.order.save()
        self.client.force_authenticate(user=self.customer_1)
        response = self.client.put(f'/orders/{self.order.id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_cancel_delivered_order(self):
        self.order.status = 'delivered'
        self.order.save()
        self.client.force_authenticate(user=self.customer_1)
        response = self.client.put(f'/orders/{self.order.id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_cancel_already_cancelled_order(self):
        self.order.status = 'cancelled'
        self.order.save()
        self.client.force_authenticate(user=self.customer_1)
        response = self.client.put(f'/orders/{self.order.id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_customer_cannot_cancel_other_users_order(self):
        self.client.force_authenticate(user=self.customer_2)
        response = self.client.put(f'/orders/{self.order.id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_vendor_cannot_cancel_order(self):
        self.client.force_authenticate(user=self.vendor)
        response = self.client.put(f'/orders/{self.order.id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_cannot_cancel_order(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(f'/orders/{self.order.id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_cancel_order(self):
        self.client.force_authenticate(user=None)
        response = self.client.put(f'/orders/{self.order.id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cancel_with_invalid_order_id(self):
        self.client.force_authenticate(user=self.customer_1)
        response = self.client.put(f'/orders/999/cancel/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_url_for_cancel_order(self):
        self.client.force_authenticate(user=self.customer_1)
        response = self.client.put('/orders/cancel/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class PlaceOrderTest(APITestCase):
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
        self.customer_1 = User.objects.create_user(
            username='customer1',
            email='customer1@gmail.com',
            password='customer1pass',
            role='customer'
        )
        self.customer_2 = User.objects.create_user(
            username='customer2',
            email='customer2@gmail.com',
            password='customer2pass',
            role='customer'
        )
        self.category = Category.objects.create(
            name='Electronics'
        )
        self.product_1 = Product.objects.create(
            name='Laptop',
            description='Test product',
            price=50000,
            stock=10,
            category=self.category,
            vendor=self.vendor
        )
        self.product_2 = Product.objects.create(
            name='Laptop',
            description='Test product',
            price=40000,
            stock=10,
            category=self.category,
            vendor=self.vendor
        )
        self.address = Address.objects.create(
            user=self.customer_1,
            street='5-C scheme',
            city='Jaipur',
            state='Rajasthan',
            pincode='302001',
            phone='9999999999',
            label='home'
        )
        self.cart_1 = Cart.objects.create(
            user = self.customer_1,
            product = self.product_1,
            quantity = 1
        )
        self.cart_2 = Cart.objects.create(
            user = self.customer_2,
            product = self.product_2,
            quantity = 1
        )
    
    def test_customer_place_order_as_owner(self):
        data = {
            'delivery_address' : self.address.id
        }
        self.client.force_authenticate(user=self.customer_1)
        response = self.client.post(f'/orders/place/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # verify order created
        order_exists = Order.objects.filter(customer=self.customer_1).exists()
        self.assertTrue(order_exists)
        # verify cart cleared
        cart_exists = Cart.objects.filter(user=self.customer_1).exists()
        self.assertFalse(cart_exists)

    def test_customer_cannot_place_other_user_order(self):
        data = {
            'delivery_address' : self.address.id
        }
        self.client.force_authenticate(user=self.customer_2)
        response = self.client.post(f'/orders/place/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_vendor_cannot_place_order(self):
        data = {
            'delivery_address' : self.address.id
        }
        self.client.force_authenticate(user=self.vendor)
        response = self.client.post(f'/orders/place/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_cannot_place_order(self):
        data = {
            'delivery_address' : self.address.id
        }
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(f'/orders/place/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_place_order(self):
        data = {
            'delivery_address' : self.address.id
        }
        self.client.force_authenticate(user=None)
        response = self.client.post(f'/orders/place/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_place_order_with_unowned_address(self):
        data = {
            'delivery_address' : self.address.id
        }
        self.client.force_authenticate(user=self.customer_2)
        response = self.client.post(f'/orders/place/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_cart_cannot_place_order(self):
        Cart.objects.filter(user=self.customer_1).delete()
        data = {
            'delivery_address': self.address.id
        }
        self.client.force_authenticate(user=self.customer_1)
        response = self.client.post('/orders/place/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


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
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(f'/orders/999/status/', data)
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



