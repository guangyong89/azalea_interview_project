from django.test import TestCase
from rest_framework.test import APITestCase
from django.urls import reverse
from django.apps import apps
from currency_app.common_func import (
    get_utc_mon_now
)
from datetime import (
    timedelta
)
# Create your tests here.


class TestCurrencyUpdate(APITestCase):

    """
    class to setup credit related settings
    """

    def setUp(self):
        """
        setup credit related settings
        """
        pass

    def test_update_currency(self):
        """
        test update currency
        """

        # make sure database is empty
        self.assertEqual(
            apps.get_model(
                'currency_app',
                'currency'
            ).objects.filter(
                currency_code='SGD'
            ).count(),
            0
        )

        # http://localhost:8000/currency/SGD/update_currency/
        endpoint_to_update_currency = (
            reverse(
                'currency_app:currency-update_currency',
                args=[
                    'SGD'
                ]
            )
        )

        response = self.client.post(
            path=endpoint_to_update_currency,
            content_type='application/json'
        )

        # ensure its 200s
        self.assertEqual(
            response.status_code,
            200
        )

        # check to ensure database have been updated
        self.assertGreater(
            apps.get_model(
                'currency_app',
                'currency'
            ).objects.filter(
                currency_code='SGD'
            ).count(),
            0
        )

    def test_get_currency(self):
        """
        test we can see currency
        """

        currency_model = apps.get_model(
            'currency_app',
            'currency'
        ).objects

        # create some dummy data
        # for this week
        data_to_create_dict_list = [
            # last week hav 1 day
            {
                'currency_code': 'SGD',
                'datetime': (
                    get_utc_mon_now() - timedelta(days=1)
                ),
                'rate': 1.05
            },
            # this week have 5 days
            {
                'currency_code': 'SGD',
                'datetime': get_utc_mon_now(),
                'rate': 1.1
            },
            {
                'currency_code': 'SGD',
                'datetime': (
                    get_utc_mon_now() + timedelta(days=1)
                ),
                'rate': 1.2
            },
            {
                'currency_code': 'SGD',
                'datetime': (
                    get_utc_mon_now() + timedelta(days=2)
                ),
                'rate': 1.3
            },
            {
                'currency_code': 'SGD',
                'datetime': (
                    get_utc_mon_now() + timedelta(days=3)
                ),
                'rate': 1.4
            },
            {
                'currency_code': 'SGD',
                'datetime': (
                    get_utc_mon_now() + timedelta(days=4)
                ),
                'rate': 1.5
            }
        ]

        for data_to_create_dict in (
            data_to_create_dict_list
        ):

            currency_model.create(
                **{
                    'datetime': data_to_create_dict['datetime'],
                    'currency_code': data_to_create_dict['currency_code'],
                    'exchange_rate': data_to_create_dict['rate']
                }
            )

        # http://localhost:8000/currency/SGD/get_currency/?filter=datetime~this_month&order=datetime
        endpoint_to_list_currency = (
            reverse(
                'currency_app:currency-get_currency',
                args=[
                    'SGD'
                ]
            )
        )

        response = self.client.get(
            path=endpoint_to_list_currency,
            content_type='application/json'
        )

        self.assertEqual(
            response.status_code,
            200
        )

        # first entry is latest one
        self.assertEqual(
            response.data['results'][0]['datetime'],
            # get the min value of datetime
            max(
                [
                    data_to_create_dict['datetime']
                    for data_to_create_dict in data_to_create_dict_list
                ]
            ).strftime(
                # convert to this '2024-05-03T00:00:00Z
                '%Y-%m-%dT%H:%M:%SZ'
            )
        )

        endpoint_to_list_currency_wif_ascending_sort = (
            endpoint_to_list_currency+'?order=datetime'
        )

        response = self.client.get(
            path=endpoint_to_list_currency_wif_ascending_sort,
            content_type='application/json'
        )

        self.assertEqual(
            response.status_code,
            200
        )

        # first entry is earliest one
        self.assertEqual(
            response.data['results'][0]['datetime'],
            # get the min value of datetime
            min(
                [
                    data_to_create_dict['datetime']
                    for data_to_create_dict in data_to_create_dict_list
                ]
            ).strftime(
                # convert to this '2024-05-03T00:00:00Z
                '%Y-%m-%dT%H:%M:%SZ'
            )
        )

        # check to ensure datetime filter is working
        endpoint_to_list_currency_wif_filter = (
            endpoint_to_list_currency+'?filter=datetime~this_week'
        )

        response = self.client.get(
            path=endpoint_to_list_currency_wif_filter,
            content_type='application/json'
        )

        self.assertEqual(
            response.status_code,
            200
        )

        # should return 5 entries for this week
        self.assertEqual(
            len(response.data['results']),
            5
        )
