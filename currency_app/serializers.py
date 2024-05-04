from rest_framework import (
    serializers
)
from django.apps import apps


class CurrencyTrendSerializer(serializers.ModelSerializer):

    class Meta:
        model = apps.get_model(
            'currency_app',
            'currency'
        )
        fields = [
            'currency_code',
            'exchange_rate',
            'datetime'
        ]
