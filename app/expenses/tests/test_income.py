from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from expenses.tests.utils import sample_user, sample_income
from core.models import Income


INCOME_LIST = reverse('expenses:income-list')


def income_detail_url(income_id):
    """Income detail url"""
    return reverse('expenses:income-detail', args=[income_id])


class PublicIncomeTests(TestCase):
    """Test public incomes endpoints"""

    def setUp(self):
        self.client = APIClient()

    def test_get_incomes_unauthorized(self):
        """Test get incomes unauthorized"""
        self.client.get(INCOME_LIST)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIncomeTests(TestCase):

    def setUp(self):
        self.user = sample_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_get_all_incomes_success(self):
        """Test get all incomes"""
        sample_income(self.user)
        sample_income(self.user)
        sample_income(self.user)
        incomes_in_database = len(Income.objects.all())
        response = self.client.get(INCOME_LIST)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(incomes_in_database, 3)


    def test_create_simple_income_success(self):
        """Test create a simple income with no periodicity"""
        payload = {
            'date': '2020-12-12',
            'amount': 4000,
            'description': 'siepp'
        }
        response = self.client.post(INCOME_LIST, payload)
        income = Income.objects.get(response.data.get('id'))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(income)

    def test_create_periodically_income_success(self):
        """Test create a periodically income"""
        payload = {
            'date': '2020-12-12',
            'amount': 4000,
            'description': 'siepp',
            'periodicity': 'm'
        }
        response = self.client.post(INCOME_LIST, payload)
        income = Income.objects.get(response.data.get('id'))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(income)

    def test_patch_income_amount_success(self):
        """Test path income amount successfully"""
        payload = {'amount': 2500}
        income = sample_income(self.user)
        url = income_detail_url(income.id)
        response = self.client.patch(url, payload)
        income.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(income.amount, resnpose.data['amount'])

    def test_create_income_no_date_error(self):
        """Test create an income with no date"""
        payload = {
            'amount': 4000,
            'description': 'siepp',
            'periodicity': 'm'
        }
        response = self.client.post(INCOME_LIST, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_income_no_amount_error(self):
        """Test create an income with no date"""
        payload = {
            'date': '2020-12-12',
            'description': 'siepp',
            'periodicity': 'm'
        }
        response = self.client.post(INCOME_LIST, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
