from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse

from .models import User, Address

# Create your tests here.

class RegistrationTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='TestUser',
            password='TestPass',
            email='testuser@email.com'
        )

    def test_register_new_user(self):
        data = {
            'username' : 'NewUser',
            'email' : 'newuser01@gmail.com',
            'password' : 'NewPass123',
            'role' : 'customer'
        }
        response = self.client.post('/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_duplicate_username(self):
        data = {
            'username' : 'TestUser',
            'email' : 'duplicate01@gmail.com',
            'password' : 'DupliPass123',
            'role' : 'customer'
        }
        response = self.client.post('/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_missing_fields(self):
        data = {
            'username' : 'NewUser',
            'email' : 'newuser01@gmail.com',
            'role' : 'customer'
        }
        response = self.client.post('/auth/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='TestUser',
            password='TestPass',
            email='testuser@email.com'
        )
    
    def test_login_success(self):
        data = {
            'username' : 'TestUser',
            'password' : 'TestPass',
        }
        response = self.client.post('/auth/login/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_wrong_username(self):
        data = {
            'username' : 'WrongUser',
            'password' : 'TestPass',
        }
        response = self.client.post('/auth/login/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_wrong_password(self):
        data = {
            'username' : 'TestUser',
            'password' : 'WrongPass',
        }
        response = self.client.post('/auth/login/', data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AddressListTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='TestUser',
            password='TestPass',
            email='testuser@email.com'
        )
        self.address = Address.objects.create(
            user = self.user,
            street = '5-C scheme',
            city = 'jaipur',
            state = 'rajasthan',
            pincode = '303030',
            phone = '9999999999',
            label = 'home',
        )
        self.client.force_authenticate(user=self.user)
    
    def test_create_address(self):
        data = {
            'street' : '5-C scheme',
            'city' : 'jaipur',
            'state' : 'rajasthan',
            'pincode' : 303030,
            'phone' : 9999999999,
            'label' : 'home',
        }
        response = self.client.post('/auth/addresses/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_address_list_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/auth/addresses/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_address_list_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/auth/addresses/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AddressDetailTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='TestUser',
            password='TestPass',
            email='testuser@email.com'
        )
        self.address = Address.objects.create(
            user = self.user,
            street = '5-C scheme',
            city = 'jaipur',
            state = 'rajasthan',
            pincode = '303030',
            phone = '9999999999',
            label = 'home',
        )
        self.client.force_authenticate(user=self.user)

    def test_get_address(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/auth/addresses/{self.address.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_address(self):
        data = {
            'street': 'New Street',
            'city': 'delhi',
            'state': 'delhi',
            'pincode': '110001',
            'phone': '8888888888',
            'label': 'office',
        }
        response = self.client.put(f'/auth/addresses/{self.address.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_delete_address(self):
        response = self.client.delete(f'/auth/addresses/{self.address.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_other_user_address(self):
        other_user = User.objects.create_user(
            username='OtherUser',
            password='OtherPass',
            email='otheruser@email.com'
        )
        self.client.force_authenticate(user=other_user)
        response = self.client.delete(f'/auth/addresses/{self.address.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

