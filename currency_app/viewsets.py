from rest_framework import (
    response,
    status,
    viewsets
)
import yfinance as yf
from django.apps import apps
from rest_framework.decorators import action
import pytz
from currency_app.serializers import CurrencyTrendSerializer
from currency_app.common_func import (
    filter_wrapper,
    order_wrapper,
    get_utc_now,
    get_utc_mon_now
)
from datetime import (
    datetime,
    timedelta
)
import calendar
from rest_framework.permissions import (
    AllowAny
)


class CurrencyViewSet(viewsets.ModelViewSet):

    """
    used to send business notif during ops
    """

    http_method_names = [
        'post',
        'get'
    ]

    permitted_filters = [
        'exchange_rate'
    ]

    permitted_ordering = []
    # no auth required
    permission_classes = [
        AllowAny
    ]

    @action(
        detail=True,
        methods=['get'],
        url_name='get_currency',
        permission_classes=permission_classes
    )
    @filter_wrapper(
        [
            'exchange_rate__gte'
            'exchange_rate__lte',
            'datetime'
        ]
    )
    @order_wrapper(
        [
            'datetime'
        ]
    )
    def get_currency(
        self,
        request,
        # refers to currency code
        pk,
        **kwargs
    ):
        """
        get the exchange rate of a currency
        """

        filter_dict = kwargs['filters']
        order_list = kwargs['ordering']

        if 'datetime' in filter_dict:

            filter_datetime_value = filter_dict.pop('datetime')

            if 'this_week' == filter_datetime_value:

                # if this_week is specified
                # get the first day of this week
                # and the last day of this week
                # and filter by that
                filter_dict['datetime__gte'] = get_utc_mon_now()

                # last moment of the week
                filter_dict['datetime__lte'] = (
                    get_utc_mon_now() +
                    timedelta(days=6)
                ).replace(
                    hour=23,
                    minute=59,
                    second=59
                )

            elif 'this_month' == filter_datetime_value:

                # if this_month is specified
                # get the first day of this month
                # and the last day of this month
                # and filter by that
                filter_dict['datetime__gte'] = get_utc_now().replace(
                    day=1,
                    hour=0,
                    minute=0,
                    second=0
                )

                # find the number of days in the month
                # and filter by that
                no_of_days_in_month = (
                    calendar.monthrange(
                        get_utc_now().year,
                        get_utc_now().month
                    )[1]
                )

                filter_dict['datetime__lte'] = get_utc_now().replace(
                    day=no_of_days_in_month,
                    hour=23,
                    minute=59,
                    second=59
                )

            elif 'this_year' == filter_datetime_value:

                # if this_year is specified
                # get the first day of this year
                # and the last day of this year
                # and filter by that
                filter_dict['datetime__gte'] = get_utc_now().replace(
                    month=1,
                    day=1,
                    hour=0,
                    minute=0,
                    second=0
                )

                filter_dict['datetime__lte'] = get_utc_now().replace(
                    month=12,
                    day=31,
                    hour=23,
                    minute=59,
                    second=59
                )

            else:

                raise Exception(
                    'invalid datetime filter'
                )

        if len(
            order_list
        ) == 0:

            # if no ordering is specified
            # sort by datetime in descending order
            order_list = [
                '-datetime'
            ]

        currency_queryset = apps.get_model(
            'currency_app',
            'currency'
        ).objects.filter(
            currency_code=pk
        ).filter(
            **{
                **filter_dict,
                # always filter by currency code
                'currency_code': pk
            }
        ).order_by(
            *order_list
        )

        page = self.paginate_queryset(
            currency_queryset
        )

        if page is not None:

            return self.get_paginated_response(
                # put it through a serializer
                # to make sure the data is in the right format
                CurrencyTrendSerializer(
                    page,
                    many=True
                ).data
            )

        # if there is no pages found,
        # return a standized response
        return response.Response(
            {
                'success': True,
                'count': 0,
                'next': None,
                'previous': None,
                'results': []
            },
            status=status.HTTP_200_OK
        )

    @ action(
        detail=True,
        methods=['post'],
        url_name='update_currency',
        permission_classes=permission_classes
    )
    def update_currency(
        self,
        request,
        # refers to currency code
        pk
    ):
        """
        call the yahoo api to get the exchange rate
        """

        last_updated_row_obj = apps.get_model(
            'currency_app',
            'currency'
        ).objects.filter(
            currency_code=pk
        ).order_by(
            # sory by datetime in descending order
            '-datetime'
        ).first()

        if last_updated_row_obj is None:

            # if it has nv exists before
            # retroactively fetch the data from 1st May 2024 UTC
            last_updated_datetime = (
                datetime(2024, 4, 1, 0, 0, 0).astimezone(pytz.utc)
            )

        else:

            last_updated_datetime = last_updated_row_obj.datetime

        # round up to the nearest day
        period_to_fetch = (
            get_utc_now() -
            last_updated_datetime
        ).days

        # if the period to fetch is 0
        # means the database is updated with the
        # latest exchange rate
        if period_to_fetch == 0:

            return response.Response(
                {
                    'success': True,
                    'message': 'no new exchange rate found'
                },
                status=status.HTTP_200_OK
            )

        currency = yf.Ticker(f'{pk}=X')

        # get the exchange convert the datetime column to utc timing
        exchange_rate_dict = (
            currency.history(
                start=last_updated_datetime,
                end=get_utc_now()
            )['Close'].to_dict()
        )

        # for whatever reason, the exchange rate is not found
        # return a 404
        # most probably the currency code is wrong
        if len(exchange_rate_dict) == 0:

            return response.Response(
                {
                    'success': False,
                    'message': 'no exchange rate found'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        """
        convert
        {
            Timestamp('2024-05-01 00:00:00+0100', tz='Europe/London'): 1.3652100563049316,
            Timestamp('2024-05-02 00:00:00+0100', tz='Europe/London'): 1.359969973564148,
            Timestamp('2024-05-03 00:00:00+0100', tz='Europe/London'): 1.3537299633026123,
            Timestamp('2024-05-04 00:00:00+0100', tz='Europe/London'): 1.3493000268936157
        }
        to
        [
            {
                'Date': '2024-05-01 00:00:00+0000',
                'Exchange Rate': 1.3652100563049316
            },
            {
                'Date': '2024-05-02 00:00:00+0000',
                'Exchange Rate': 1.359969973564148
            },
            {
                'Date': '2024-05-03 00:00:00+0000',
                'Exchange Rate': 1.3537299633026123
            },
            {
                'Date': '2024-05-04 00:00:00+0000',
                'Exchange Rate': 1.3493000268936157
            }
        ]
        """

        output_list = []
        # each key is a datetime obj in the dict
        for datetime_obj in exchange_rate_dict:

            utc_date_obj = datetime_obj.astimezone(pytz.utc)

            output_list.append(
                {
                    # convert to utc
                    'datetime': utc_date_obj,
                    'exchange_rate': exchange_rate_dict[datetime_obj],
                    'currency_code': pk
                }
            )

        currency_model = apps.get_model(
            'currency_app',
            'currency'
        ).objects
        # update the database
        # before saving the data
        for currency_rate_dict in output_list:

            # check if the exchange rate already exists
            if currency_model.filter(
                datetime=currency_rate_dict['datetime'],
                currency_code=currency_rate_dict['currency_code']
            ).exists():

                # if it exists, skip
                continue

            # if it does not exist, create a new record
            currency_rate_obj = currency_model.create(
                **{
                    'datetime': currency_rate_dict['datetime'],
                    'currency_code': currency_rate_dict['currency_code'],
                    'exchange_rate': currency_rate_dict['exchange_rate']
                }
            )

            currency_rate_obj.save()

        return response.Response(
            {
                'success': True,
                'exchange_rate_updated_into system': output_list
            },
            status=status.HTTP_200_OK
        )
