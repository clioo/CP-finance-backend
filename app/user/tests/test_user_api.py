from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicApiUserTests(TestCase):
    """Testi the public user api endpoints"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """test create valid user"""
        payload = {
            'email': 'test1@test.com',
            'password': 'password12345',
            'name': 'rodolfo'
        }
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**response.data)
        self.assertTrue(user.check_password(payload['password']))
        # Make sure password is not being send by the API
        self.assertNotIn(payload['password'], response.data)

    def test_create_user_already_exists(self):
        """Test create user that already exists"""
        payload = {
            'email': 'test@test.com',
            'password': 'passwordsecur3',
            'name': 'chicho'
        }
        create_user(**payload)
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_user(self):
        """Test create an invalid user"""
        payload = {
            'username': '',
            'password': 'asdfeq323',
            'name': 'asdsad'
        }
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_for_user(self):
        """Test create a token for an existing user"""
        payload = {
            'email': 'test@test2.com',
            'password': 'pass43w31o3rod3',
        }
        create_user(**payload)
        response = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_credentials_token(self):
        """test invalid credentials for getting a token"""
        payload = {
            'email': 'asd@asd.com',
            'password': 'password2',
        }
        create_user(email='asd@asd.com', password='password3q')
        response = self.client.post(TOKEN_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test to get a token with unexisting user"""
        payload = {
            'email': 'test@trt.com',
            'password': 'password1'
        }
        response = self.client.post(TOKEN_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        """Test create a token with a missing field"""
        payload = {'email': 'asd@asd.com', 'password': ''}
        response = self.client.post(TOKEN_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test retrieve a user without token"""
        response = self.client.get(ME_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_password_too_short(self):
        """Test that a password is too short for creating the user"""
        payload = {
            'email': 'asd@asd.com',
            'password': '123',
            'name': 'asdssad'
        }
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PrivateApiUserTests(TestCase):
    """Test private api endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='asd@asd.com', password='password1')
        self.client.force_authenticate(user=self.user)

    def test_retrive_profile_success(self):
        """Test retrieve profile for logged in user"""
        response = self.client.get(ME_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'email': self.user.email,
            'name': self.user.name
        })

    def test_not_allowed_post(self):
        """Test a not allowed post"""
        response = self.client.post(ME_URL, {})
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile for authenticated user"""
        payload = {
            'name': 'carlangas',
            'password': 'securepassword123'
        }
        response = self.client.patch(ME_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
