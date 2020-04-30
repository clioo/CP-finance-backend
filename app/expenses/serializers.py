from rest_framework import serializers
from core.models import AnnualBudget, MonthBudget, Expense, ExpensesTag


class AnnualBudgetSerializer(serializers.ModelSerializer):
    """Serializer for annual budget model"""

    class Meta:
        model = AnnualBudget
        fields = ('year', 'description', 'amount')
        read_only_fields =  ('user', 'id',)
