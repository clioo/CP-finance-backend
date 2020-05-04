from rest_framework import serializers
from core.models import AnnualBudget, MonthBudget, Expense, ExpensesTag


class AnnualBudgetSerializer(serializers.ModelSerializer):
    """Serializer for annual budget model"""

    class Meta:
        model = AnnualBudget
        fields = ('year', 'description', 'amount')
        read_only_fields =  ('user', 'id',)


class ExpensesTagSerializer(serializers.ModelSerializer):
    """Serializer for expenses tag"""

    class Meta:
        model = ExpensesTag
        fields = ('name',)
        read_only_fields =  ('user', 'id',)


class MonthBudgetSerializer(serializers.ModelSerializer):
    """Serializer for annual budget model"""

    class Meta:
        model = MonthBudget
        fields = ('annual_budget', 'expenses_tag', 'description', 'amount',)
        read_only_fields = ('user', 'id',)
