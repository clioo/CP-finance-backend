from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin
from django.utils.translation import gettext_lazy as _
import datetime


def validate_cero(value):
    if value <= 0:
        raise ValidationError(
            _(f'{value} not valid, it must be greater than 0.')
        )


def year_choices():
    return [(r, r) for r in range(current_year(), current_year() + 10)]


def current_year():
    return datetime.date.today().year


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """Creating a superuser"""
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Customer user model that support using email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UserManager()
    USERNAME_FIELD = 'email'


class BaseBudget(models.Model):
    """Base budget model that validates amount"""
    description = models.CharField(max_length=255,
                                   verbose_name='Descripción')
    amount = models.FloatField(verbose_name='Cantidad',
                               validators=[validate_cero])
    user = models.ForeignKey('User', on_delete=models.PROTECT,
                             verbose_name='Usuario')


class BaseTag(models.Model):
    user = models.ForeignKey('User', verbose_name=_('User'))
    name = models.CharField(max_length=255, verbose_name=_('Name'))


class AnnualBudget(BaseBudget):
    year = models.IntegerField(verbose_name=_('Year'), choices=year_choices)

    class Meta:
        unique_together = ['year', 'user']


class ExpensesTag(BaseTag):

    def __str__(self):
        return _('Expense') + ' ' + self.name


class MonthBudget(BaseBudget):
    annual_budget = models.ForeignKey('AnnualBudget', on_delete=models.PROTECT,
                                      verbose_name=_('Annual budget'))
    expenses_tag = models.ForeignKey('ExpensesTag', on_delete=models.PROTECT,
                                     verbose_name=_('Expenses tag'))

    def __str__(self):
        return _('Budget for') + ' ' + self.expenses_tag.name

class Expense(BaseBudget):
    """Single expense, detailed"""
    date = models.DateField(verbose_name=_('Date'))
    expenses_tag = models.ForeignKey(
        'ExpensesTag',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_('Expenses tag')
    )
    month_budget = models.ForeignKey(
        'MonthBudget',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_('Month budget')
    )

    def save(self, *args, **kwargs):
        if self.expenses_tag and self.month_budget:
            raise ValueError(_("""You can choose just one option: 
                                  month budget or expenses tag"""))
        elif not self.expenses_tag and not self.month_budget:
            raise ValueError(_("""You need to choose just option: 
                                  month budget or expenses tag"""))
        super(Expense, self).save(*args, **kwargs)
