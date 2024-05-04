from rest_framework import routers
from currency_app import viewsets


app_name = 'currency_app'


router = routers.DefaultRouter()

router.register(
    r'currency',
    viewsets.CurrencyViewSet,
    basename='currency'
)


urlpatterns = [
    *router.urls
]
