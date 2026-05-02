from rest_framework.test import APITestCase
from rest_framework import status

from Authenticate.models import User
from .models import Product, Category

# Create your tests here.

class ProductListTest(APITestCase):
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
        self.product = Product.objects.create(
            name = 'NewProduct',
            description = 'New Product is cool',
            price = 120,
            stock = 10,
            category = self.category,
            vendor = self.vendor,
        )
        self.client.force_authenticate(user=self.vendor)
    
    def test_get_product_list_authenticated(self):
        self.client.force_authenticate(user=self.vendor)
        response = self.client.get('/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_product_list_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/products/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_product_as_vendor(self):
        data = {
            'name' : 'NewerProduct',
            'description' : 'Newer Product is very cool',
            'price' : 20,
            'stock' : 10,
            'category' : self.category.id,
        }
        self.client.force_authenticate(user=self.vendor)
        response = self.client.post('/products/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_product_as_customer(self):
        data = {
            'name' : 'NewProductCus',
            'description' : 'New Product by customer',
            'price' : 40,
            'stock' : 20,
            'category' : self.category.id,
        }
        self.client.force_authenticate(user=self.customer)
        response = self.client.post('/products/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ProductDetailTest(APITestCase):
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
        self.product = Product.objects.create(
            name = 'NewProduct',
            description = 'New Product is cool',
            price = 120,
            stock = 10,
            category = self.category,
            vendor = self.vendor,
        )
        self.client.force_authenticate(user=self.vendor)
    def test_get_product_detail(self):
        self.client.force_authenticate(user=self.vendor)
        response = self.client.get(f'/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_product_not_found(self):
        self.client.force_authenticate(user=self.vendor)
        response = self.client.get('/products/999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_product_as_vendor(self):
        data = {
            'name' : 'NewProduct',
            'description' : 'New Product updated by vendor',
            'price' : 120,
            'stock' : 10,
            'category' : self.category.id,
        }
        self.client.force_authenticate(user=self.vendor)
        response = self.client.put(f'/products/{self.product.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_update_product_as_customer(self):
        data = {
            'name' : 'NewProduct',
            'description' : 'New Product updated by customer',
            'price' : 120,
            'stock' : 10,
            'category' : self.category.id,
        }
        self.client.force_authenticate(user=self.customer)
        response = self.client.put(f'/products/{self.product.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_product_as_vendor(self):
        self.client.force_authenticate(user=self.vendor)
        response = self.client.delete(f'/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_product_as_customer(self):
        self.client.force_authenticate(user=self.customer)
        response = self.client.delete(f'/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CategoryListTest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username = 'Admin01',
            email = 'admin01@gmail.com',
            password = 'AdminPass',
            role = 'admin'
        )
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
        self.client.force_authenticate(user=self.admin)

    def test_get_category_list_authenticated(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/products/categories/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_category_list_unauthenticate(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/products/categories/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_category_as_admin(self):
        data = {
            'name' : 'clothing'
        }
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/products/categories/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_category_as_vendor(self):
        data = {
            'name' : 'clothing'
        }
        self.client.force_authenticate(user=self.vendor)
        response = self.client.post('/products/categories/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_category_as_customer(self):
        data = {
            'name' : 'clothing'
        }
        self.client.force_authenticate(user=self.customer)
        response = self.client.post('/products/categories/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CategoryDetailTest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username = 'Admin01',
            email = 'admin01@gmail.com',
            password = 'AdminPass',
            role = 'admin'
        )
        self.vendor = User.objects.create_user(
            username = 'NewVendor',
            email = 'newvendor@gmail.com',
            password = 'VendorPass',
            role = 'vendor'
            )
        self.category = Category.objects.create(
            name = 'Electronic'
        )
        self.client.force_authenticate(user=self.admin)
    
    def test_get_category_detail(self):
        response = self.client.get(f'/products/categories/{self.category.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_get_category_not_found(self):
        response = self.client.get(f'/products/categories/900/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_category_as_admin(self):
        data = {
            'name' : 'Electronics'
        }
        self.client.force_authenticate(user=self.admin)
        response = self.client.put(f'/products/categories/{self.category.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_update_category_as_vendor(self):
        data = {
            'name' : 'Electronics'
        }
        self.client.force_authenticate(user=self.vendor)
        response = self.client.put(f'/products/categories/{self.category.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_category_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/products/categories/{self.category.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_category_as_vendor(self):
        self.client.force_authenticate(user=self.vendor)
        response = self.client.delete(f'/products/categories/{self.category.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)






