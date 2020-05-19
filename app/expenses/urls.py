from django.urls import path, include
from rest_framework.routers import DefaultRouter
from expenses import views


app_name = 'expenses'


router = DefaultRouter()
router.register('annualbudget', views.AnnualBudgetViewSet)
router.register('monthbudget', views.MonthBudgetViewSet)
router.register('expensestag', views.ExpensesTagViewSet)
router.register('expense', views.ExpenseViewSet)
router.register('income', views.IncomeViewSet)


urlpatterns = [
    path('', include(router.urls))
]
