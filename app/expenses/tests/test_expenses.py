from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import AnnualBudget


ANNUAL_BUDGET_LIST_URL = reverse('expenses:annualbudget-list')


def sample_user(email='test@test.com', password='password1234'):
    return get_user_model().objects.create_user(email=email,
                                                password=password)


class PublicExpensesTests(TestCase):
    """Test public endpoints for expenses app"""

    def setUp(self):
        self.client = APIClient()

    def test_get_annual_budget_unauthorize(self):
        """Test that anonumous users can not see annual budgets"""
        response = self.client.get(ANNUAL_BUDGET_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateExpensesTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = sample_user()
        self.client.force_authenticate(self.user)

    def test_create_annual_budget_success(self):
        """Test create annual budget successfully"""
        payload = {
            'year': 2020,
            'amount': 202000000,
            'description': 'Budget for this greatful year',
        }
        response = self.client.post(ANNUAL_BUDGET_LIST_URL, payload)
        exists = AnnualBudget.objects.filter(
            user=self.user,
            year=payload['year']
            ).exists()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exists)
