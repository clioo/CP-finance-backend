from django.urls import path, include
from rest_framework.routers import DefaultRouter
from expenses import views


app_name = 'expenses'


router = DefaultRouter()
router.register('annualbudget', views.AnnualBudgetViewSet)


urlpatterns = [
    path('', include(router.urls))
]
