from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from expenses import serializers
from core.models import AnnualBudget, MonthBudget, Expense, ExpensesTag


class BaseBudgetViewSet(viewsets.GenericViewSet,
                          mixins.ListModelMixin,
                          mixins.CreateModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.RetrieveModelMixin):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Returns annual of the authenticated user."""
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Saves a new object"""
        serializer.save(user=self.request.user)


class AnnualBudgetViewSet(BaseBudgetViewSet):
    """Manage annual budget in the database"""
    queryset = AnnualBudget.objects.all()
    serializer_class = serializers.AnnualBudgetSerializer


class ExpensesTagViewSet(BaseBudgetViewSet):
    """Manage expenses tag in the database"""
    queryset = ExpensesTag.objects.all()
    serializer_class = serializers.ExpensesTagSerializer


class MonthBudgetViewSet(BaseBudgetViewSet):
    """Manage month budget in the database"""
    queryset = MonthBudget.objects.all()
    serializer_class = serializers.MonthBudgetSerializer
