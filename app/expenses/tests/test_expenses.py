from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from django.db.utils import IntegrityError
from datetime import datetime
from expenses.tests.utils import sample_user, sample_expenses_tag,\
                                 sample_annual_budget, sample_month_budget,\
                                 sample_expense


ANNUAL_BUDGET_LIST_URL = reverse('expenses:annualbudget-list')
MONTH_BUDGET_LIST_URL = reverse('expenses:monthbudget-list')
EXPENSES_TAG_LIST_URL = reverse('expenses:expensestag-list')
EXPENSE_LIST_URL = reverse('expenses:expense-list')


def annual_budget_detail_url(annual_budget_id):
    """Annual budget detail URL"""
    return reverse('expenses:annualbudget-detail', args=[annual_budget_id])


def month_budget_detail_url(month_budget_id):
    """month budget detail URL"""
    return reverse('expenses:monthbudget-detail', args=[month_budget_id])


def expenses_tag_detail_url(expenses_tag_id):
    """Expenses tag detail URL"""
    return reverse('expenses:expensestag-detail', args=[expenses_tag_id])


def expense_detail_url(expense_id):
    """Expense detail url"""
    return reverse('expenses:expense-detail', args=[expense_id])


class PublicExpensesTests(TestCase):
    """Test public endpoints for expenses app"""

    def setUp(self):
        self.client = APIClient()

    def test_get_annual_budget_unauthorize(self):
        """Test that anonumous users can not see annual budgets"""
        response = self.client.get(ANNUAL_BUDGET_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_month_budget_aunauthorized(self):
        """Test that anonymous users can not see monthly budgets"""
        response = self.client.get(MONTH_BUDGET_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_expenses_tag_aunauthorized(self):
        """Test that anonymous users can not see expenses tag"""
        response = self.client.get(EXPENSES_TAG_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_expenses_aunauthorized(self):
        """Test that anonymous users can not see expenses"""
        response = self.client.get(EXPENSE_LIST_URL)
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
        self.client.patch(
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
        self.client.patch(
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
        """Test create month budget without annual budget"""
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
        self.assertEqual(response.data['description'],
                         month_budget.description)

    def test_create_expense_expenses_tag_success(self):
        """Test create expense with expenses tag successfully"""
        expenses_tag = sample_expenses_tag(self.user)
        payload = {
            'description': 'cerveza',
            'amount': 300,
            'date': datetime.today().strftime('%Y-%m-%d'),
            'expenses_tag': expenses_tag.id
        }
        response = self.client.post(EXPENSE_LIST_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_expense_month_budget_success(self):
        """Test create expense with month budget successfully"""
        month_budget = sample_month_budget(self.user)
        payload = {
            'description': 'cerveza',
            'amount': 300,
            'date': datetime.today().strftime('%Y-%m-%d'),
            'month_budget': month_budget.id
        }
        response = self.client.post(EXPENSE_LIST_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_expense_month_budget_expenses_tag_invalid(self):
        """Test create expense with month budget and expenses tag invalid"""
        month_budget = sample_month_budget(self.user)
        expenses_tag = sample_expenses_tag(self.user)
        payload = {
            'description': 'cerveza',
            'amount': 300,
            'date': datetime.today().strftime('%Y-%m-%d'),
            'month_budget': month_budget.id,
            'expenses_tag': expenses_tag.id
        }
        with self.assertRaises(ValueError):
            self.client.post(EXPENSE_LIST_URL, payload)

    def test_create_expense_no_month_budget_nor_expenses_tag_invalid(self):
        """Test create expense without month budget and expenses tag invalid"""
        payload = {
            'description': 'cerveza',
            'amount': 300,
            'date': datetime.today().strftime('%Y-%m-%d'),
        }
        with self.assertRaises(ValueError):
            self.client.post(EXPENSE_LIST_URL, payload)

    def test_patch_expense(self):
        """Test patch expense"""
        month_budget = sample_month_budget(self.user)
        expense = sample_expense(self.user, month_budget=month_budget)
        payload = {'amount': 5000, 'description': 'carro de mi jefa'}
        url = expense_detail_url(expense.id)
        response = self.client.patch(url, payload)
        expense.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['amount'], expense.amount)
        self.assertEqual(response.data['description'], expense.description)

    def test_get_all_expenses_user(self):
        """Test get all expenses"""
        month_budget = sample_month_budget(self.user)
        sample_expense(self.user, month_budget=month_budget)
        sample_expense(self.user, month_budget=month_budget)
        sample_expense(self.user, month_budget=month_budget)
        response = self.client.get(EXPENSE_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
