from django.db import models

# Create your models here.


class currency(models.Model):

    """
    this is the model to store the currency exchange rate
    over time
    """

    # the exchange rate at the point of time
    datetime = models.DateTimeField()

    currency_code = models.CharField(max_length=3)

    # stores the exchange rate to 1 USD
    exchange_rate = models.FloatField()

    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        string representation of the model
        """

        # return as a dictionary
        return str(
            {
                # show as 12 Mar 2024 12:00:00 UTC
                'datetime': self.datetime.strftime(
                    '%d %b %Y %H:%M:%S %Z'
                ),
                'currency_code': self.currency_code,
                'exchange_rate': self.exchange_rate
            }
        )

    class Meta:
        """
        meta class for the model
        """

        # each currency code can only have one entry for each datetime
        unique_together = [
            'datetime',
            'currency_code'
        ]
