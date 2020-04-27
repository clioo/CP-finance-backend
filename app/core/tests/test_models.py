from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from core import models


def sample_user(email='testuser@tes.com', password='password123'):
    """Creates a simple user"""
    return get_user_model().objects.create_user(email, password)


class UserModelTests(TestCase):
    """Tests users model"""
    
    def test_user_model_email_successful(self):
        """Tests the successful creation of a simple user"""
        email = 'test@test.com'
        user = sample_user(email)
        self.assertEqual(email, user.email)

    def test_create_user_email_normalized(self):
        """Tests that the user email is normalized successfully"""
        email = 'test1@ASDSS.com'
        user = sample_user(email)
        self.assertEqual(email.lower(), user.email)

    def test_create_user_invalid_email(self):
        """Tests creating a new user with invalid email"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, '213we')    

    def test_create_superuser(self):
        """Test thta superuser is created"""
        user = get_user_model().objects.create_superuser(
            'test@test.cocm',
            'password1ddffE'
        )
        self.assertTrue(user.is_superuser)

    def test_user_str(self):
        """Test that the str generated after creating a user is correct"""
        user = sample_user()
        self.assertEqual(str(user), user.email)
