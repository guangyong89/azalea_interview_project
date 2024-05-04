This App has 2 main endpoint

1.http://localhost:8000/currency_app/currency/SGD/update_currency/
This first url calls the yahoo finance api endpoint and update the latest exchange rate to SGD in the database

2.http://localhost:8000/currency_app/currency/SGD/get_currency/
This second endpoint allows users to view the historial closing exchange rate

    Allowed filter key, filter value
    'exchange_rate__gte', 1-1000
    'exchange_rate__lte', 1-1000
    'datetime', any of the following ['this_week','this_month']

    e.g
    http://localhost:8000/currency_app/currency/SGD/get_currency/?filter=datetime~this_week - see this week data
    http://localhost:8000/currency_app/currency/SGD/get_currency/?filter=datetime~this_month - see this month data

For both
change 'SGD' to 'MYR' for diffrent currency for both url

"""
HOW TO SET UP
""

1. create a virtual env to install package - RUN python3 -m venv /path/to/your/virtualenv
2. cd to the project folder
3. run pip3 install -r requirements.txt
4. RUN python3 manage.py test
   You should see
   Found 2 test(s).
   Creating test database for alias 'default'...
   System check identified no issues (0 silenced).
   ..

   ***

   Ran 2 tests in 0.378s

   OK
   Destroying test database for alias 'default'...

5. RUN python3 manage.py runserver
