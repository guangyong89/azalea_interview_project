from urllib.parse import unquote
import functools
from datetime import (
    datetime,
    timedelta
)
import pytz


def filter_wrapper(permitted_filters):
    def real_filter_wrapper(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            # get filters sent in
            filter_fields = args[0].request.query_params.get('filter', None)

            # initialize data
            filters = {}
            list_fields = []

            # quick hacks, add a entry so wont get index error below
            if len(permitted_filters) == 0:
                permitted_filters.append(None)

            if filter_fields is None:
                pass
            else:
                '''
                Split the code into each field.
                Values being sent in as an array will appear as:

                fieldX__in~a,d,f,fieldY~t

                need to split them out and assign them back to the same filter field
                '''
                filter_fields = filter_fields.split(',')
                prev_filter = ''
                for each in filter_fields:
                    each = each.split('~')

                    if len(each) == 1:
                        # if length of split string is 1, it is likely to belong to part of an array
                        if prev_filter:
                            filterData = unquote(each[0])

                            # True and False will be sent in as a string. Need to make it a boolean
                            if filterData in ['True', 'False']:
                                filterData = (filterData == 'True')

                            filters[prev_filter] += ',%s' % (filterData)
                            if (prev_filter not in list_fields):
                                list_fields.append(prev_filter)

                    elif each[0] in permitted_filters or permitted_filters[0] == "__all__":

                        filterData = unquote(each[1])

                        # True and False will be sent in as a string.
                        # Need to make it a boolean
                        if filterData.capitalize() in ['True', 'False']:

                            filterData = (filterData.capitalize() == 'True')

                        filters[each[0]] = filterData
                        prev_filter = each[0]

                    else:

                        pass

            for x in list_fields:
                filters[x] = unquote(filters[x]).split(",")

            # search for __in type filters. __in type filters must be list
            # the filter might be a string instead of an array if only 1 value is
            # sent in based on the above function. convert non list into list for the
            # __in type filters to work
            for key in filters:
                if key.endswith('__in') & (not isinstance(filters[key], list)):
                    filters[key] = [filters[key]]

            return func(*args, **filters)
        return wrapper
    return real_filter_wrapper


def check_if_need_to_be_replaced(order_entry_str):
    """
    if any of the below is indicated, convert to pk,
    so it will return
    orderid-1, orderid-2
    instead of
    orderid-1, orderid-11
    """

    order_str_to_convert_to_pk_list = [
        'booking_id'
    ]

    # for every entry whitelisted above,
    # add in a matching entry with a '-' infront
    order_str_to_convert_to_pk_list = [
        '-{}'.format(
            x
        ) for x in order_str_to_convert_to_pk_list
    ] + order_str_to_convert_to_pk_list

    if order_entry_str in order_str_to_convert_to_pk_list:

        # check if there is a dash infront and return accordingly
        if ('-' in order_entry_str):

            return '-pk'

        else:

            return 'pk'

    # by default, return original str
    return order_entry_str


def order_wrapper(permitted_ordering):
    def real_filter_wrapper(func):
        @ functools.wraps(func)
        def wrapper(*args, **kwargs):

            PermittedList = []

            order_query_str = args[0].request.query_params.get('order', None)

            # quick hacks, add a entry so wont get index error below
            if len(permitted_ordering) == 0:

                permitted_ordering.append(None)

            # if there is order detail this is in string
            if order_query_str is not None:

                # convert the string to lis
                order_query_list = order_query_str.split(',')

                for order_entry_str in order_query_list:

                    # remove the - if any
                    check_query = order_entry_str.replace('-', '')

                    # check if the order instruction is in the permitted order or not
                    if (
                        (check_query in permitted_ordering) |
                        # if developer indicuate __all__ will return also
                        (permitted_ordering[0] == '__all__')
                    ):

                        # check if its a whitelisted field that needs to be replaced with pk
                        order_entry_str = check_if_need_to_be_replaced(
                            order_entry_str=order_entry_str
                        )

                        # append it to output
                        PermittedList.append(order_entry_str)

                combined = {
                    'filters': kwargs,
                    'ordering': PermittedList
                }

            else:

                combined = {
                    'filters': kwargs,
                    'ordering': []
                }

            # pass in a empty pk if none found
            # pk is needed when we filtering on retrieve
            pk = args[0].kwargs.get('pk', None)

            return func(*args, **combined, pk=pk)

        return wrapper

    return real_filter_wrapper


def get_utc_now():
    """
    create this function to attempt to standardize the way to retrieve utc now
    datetime
    """

    return datetime.utcnow().replace(
        tzinfo=pytz.utc
    )


def get_utc_mon_now():
    """
    return the monday date for the current week
    """

    # get the current datetime
    utc_now = get_utc_now().replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    # minus away all the days that is currently in the date
    return utc_now - timedelta(
        days=utc_now.weekday()
    )
