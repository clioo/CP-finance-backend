from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models
from django.db.utils import IntegrityError


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


class ModelTests(TestCase):
    """Tests for models"""

    def setUp(self):
        self.user = sample_user()
        self.annual_budget = models.AnnualBudget(
            amount=2000000,
            year='2025',
            user=self.user
        )
        self.annual_budget.save()
        self.expenses_tag1 = models.ExpensesTag(name='cheve', user=self.user)
        self.expenses_tag1.save()
        self.month_budget = models.MonthBudget(
            description='Cerveza para los fines de semana',
            amount=1000,
            annual_budget=self.annual_budget,
            expenses_tag=self.expenses_tag1,
            user=self.user
        )
        self.month_budget.save()

    def test_create_annual_budget_success(self):
        """Test create successfully anual budget"""
        annual_budget = models.AnnualBudget(
            amount=200000,
            year='2020',
            user=self.user
        )
        annual_budget.save()
        self.assertEqual(str(annual_budget),
                         f'{annual_budget.year} budget')

    def test_create_repeated_annual_budget_error(self):
        """Test that users can't create repeated anual budgets"""
        annual_budget1 = models.AnnualBudget(
            amount=200000,
            year='2020',
            user=self.user
        )
        annual_budget2 = models.AnnualBudget(
            amount=300000,
            year='2020',
            user=self.user
        )
        with (self.assertRaises(IntegrityError)):
            annual_budget1.save()
            annual_budget2.save()
        # To do: assert that error is raised

    def test_create_expenses_tag_successful(self):
        expenses_tag1 = models.ExpensesTag(name='cheve', user=self.user)
        expenses_tag2 = models.ExpensesTag(name='tdc', user=self.user)
        expenses_tag1.save()
        expenses_tag2.save()
        self.assertEqual(str(expenses_tag1), 'Expense ' + expenses_tag1.name)
        self.assertEqual(str(expenses_tag2), 'Expense ' + expenses_tag2.name)

    def test_create_month_budget_success(self):
        """Test create a monthly budget with certain tag"""
        annual_budget = models.AnnualBudget(
            amount=2000000,
            year='2020',
            user=self.user
        )
        annual_budget.save()
        expenses_tag1 = models.ExpensesTag(name='cheve', user=self.user)
        expenses_tag1.save()
        month_budget = models.MonthBudget(
            description='Cerveza para los fines de semana',
            amount=1000,
            annual_budget=annual_budget,
            expenses_tag=expenses_tag1,
            user=self.user
        )
        month_budget.save()
        self.assertEqual(str(month_budget),
                         f'Budget for {month_budget.expenses_tag.name}')

    def test_create_month_budget_amount_0(self):
        """Test that you can't create a month budget with 0 amount"""
        # To do: assert when fails
        pass

    def test_create_expense_success(self):
        expense1 = models.Expense(
            amount=300,
            date='2025-12-12',
            month_budget=self.month_budget,
            user=self.user
        )
        expense1.save()
        expense2 = models.Expense(
            amount=200,
            date='2025-12-12',
            expenses_tag=self.expenses_tag1,
            user=self.user
        )
        expense2.save()
        self.assertEqual(str(expense1),
                         expense1.month_budget.expenses_tag.name)
        self.assertEqual(str(expense2),
                         expense2.expenses_tag.name)

    def test_no_tag_or_month_budget_error(self):
        with self.assertRaises(ValueError):
            expense1 = models.Expense(
                amount=200,
                date='2025-12-12',
                user=self.user
            )
            expense1.save()
