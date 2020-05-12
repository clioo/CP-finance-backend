from django.contrib.auth import get_user_model
from core.models import AnnualBudget, ExpensesTag, MonthBudget, Expense, Income


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


def sample_expense(user, **params):
    """Requires month_budget or expenses_tag in params"""
    defaults = {
        'description': 'cerveza',
        'amount': 3000,
        'date': datetime.now(),
    }
    defaults.update(params)
    return Expense.objects.create(user=user, **defaults)


def sample_income(user, **params):
    defaults = {
        'date': '2020-12-12',
        'amount': 4000,
        'description': 'siepp'
    }
    defaults.update(params)
    return Income.objects.create(user=user, **defaults)
