from django.contrib import admin

# Register your models here.

from django.apps import apps


@admin.register(
    apps.get_model(
        'currency_app',
        'currency'
    )
)
class CurrencyAdmin(admin.ModelAdmin):

    search_fields = [
        'currency_code'
    ]
