from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import AnnualBudget, ExpensesTag, MonthBudget
from django.db.utils import IntegrityError


ANNUAL_BUDGET_LIST_URL = reverse('expenses:annualbudget-list')
MONTH_BUDGET_LIST_URL = reverse('expenses:monthbudget-list')
EXPENSES_TAG_LIST_URL = reverse('expenses:expensestag-list')


def annual_budget_detail_url(annual_budget_id):
    """Annual budget detail URL"""
    return reverse('expenses:annualbudget-detail', args=[annual_budget_id,])


def month_budget_detail_url(month_budget_id):
    """month budget detail URL"""
    return reverse('expenses:monthbudget-detail', args=[month_budget_id,])


def expenses_tag_detail_url(expenses_tag_id):
    """Expenses tag detail URL"""
    return reverse('expenses:expensestag-detail', args=[expenses_tag_id,])


def sample_user(email='test@test.com', password='password1234'):
    return get_user_model().objects.create_user(email=email,
                                                password=password)


def sample_expenses_tag(user, name='cheve'):
    return ExpensesTag.objects.create(user=user, name=name)


def sample_annual_budget(user, year=2020,
                         amount=300000, description=''):
    return AnnualBudget.objects.create(
        user=user,
        amount=amount,
        year=year,
        description=description
    )


def sample_month_budget(user, **params):
    defaults = {
        'description': 'mensualidad carro',
        'amount': 3000,
        'annual_budget': sample_annual_budget(user),
        'expenses_tag': sample_expenses_tag(user)
    }
    defaults.update(params)
    return MonthBudget.objects.create(user=user, **defaults)


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

    def test_patch_description_annual_budget_success(self):
        """Test patch description successfully"""
        annual_budget = sample_annual_budget(user=self.user)
        payload = {
            'description': 'description1'
        }
        response = self.client.patch(
            annual_budget_detail_url(annual_budget.id),
            payload
        )
        annual_budget.refresh_from_db()
        self.assertEqual(annual_budget.description, payload['description'])

    def test_patch_year_annual_budget_success(self):
        """Test patch year successfully"""
        annual_budget = sample_annual_budget(user=self.user)
        payload = {
            'year': 2022
        }
        url = annual_budget_detail_url(annual_budget.id)
        response = self.client.patch(
            url,
            payload
        )
        annual_budget.refresh_from_db()
        self.assertEqual(annual_budget.year, payload['year'])

    def test_retrieve_annual_budget_success(self):
        annual_budget = sample_annual_budget(user=self.user)
        url = annual_budget_detail_url(annual_budget.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['year'], annual_budget.year)
        self.assertEqual(response.data['amount'], annual_budget.amount)

    def test_create_anual_budget_amount_0(self):
        """Test create annual budget with 0 amount"""
        payload = {
            'year': 2020,
            'amount': 0,
            'description': 'Budget for this greatful year',
        }
        response = self.client.post(ANNUAL_BUDGET_LIST_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_annual_buget_year_repeated(self):
        """Test creating a repeated annual budget"""
        payload = {
            'year': 2020,
            'amount': 202000000,
            'description': 'Budget for this greatful year',
        }
        self.client.post(ANNUAL_BUDGET_LIST_URL, payload)
        with self.assertRaises(IntegrityError):
            self.client.post(ANNUAL_BUDGET_LIST_URL, payload)

    def test_create_expenses_tags_success(self):
        """Test create successfully a expenses tag"""
        payload = {'name': 'cheve'}
        response = self.client.post(EXPENSES_TAG_LIST_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_expenses_tag_empty_name(self):
        """Test create a expenses tag with empty name"""
        payload = {'name': ''}
        response = self.client.post(EXPENSES_TAG_LIST_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_expenses_tags(self):
        expenses_tag = sample_expenses_tag(self.user)
        payload = {'name': 'comida'}
        url = expenses_tag_detail_url(expenses_tag.id)
        response = self.client.patch(url, payload)
        expenses_tag.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], expenses_tag.name)

    def test_create_month_buget_success(self):
        """Test create a month budget successfully"""
        annual_budget = sample_annual_budget(self.user)
        expenses_tag = sample_expenses_tag(self.user)
        payload = {
            'annual_budget': annual_budget.id,
            'expenses_tag': expenses_tag.id,
            'amount': 3000,
        }
        response = self.client.post(MONTH_BUDGET_LIST_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_month_budget_no_annual_budget(self):
        """Test create month budget withouy annual budget"""
        annual_budget = sample_annual_budget(self.user)
        expenses_tag = sample_expenses_tag(self.user)
        payload = {
            'annual_budget': '',
            'expenses_tag': expenses_tag.id,
            'amount': 3000,
        }
        response = self.client.post(MONTH_BUDGET_LIST_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_month_budget_no_expenses_tag(self):
        """Test create month budget no expenses"""
        annual_budget = sample_annual_budget(self.user)
        payload = {
            'annual_budget': annual_budget.id,
            'expenses_tag': '',
            'amount': 3000,
        }
        response = self.client.post(MONTH_BUDGET_LIST_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_month_budget(self):
        """Test partial update on month budget"""
        month_budget = sample_month_budget(self.user)
        payload = {'amount': 5000, 'description': 'mensualidad camioneta'}
        url = month_budget_detail_url(month_budget.id)
        response = self.client.patch(url, payload)
        month_budget.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['amount'], month_budget.amount)
        self.assertEqual(response.data['description'], month_budget.description)
