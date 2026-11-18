# Prem Airlines (Django flight booking demo)

## Run
1. `python -m venv myenv` then activate it (`myenv\Scripts\activate` on Windows, `source myenv/bin/activate` on Mac/Linux)
2. `pip install -r requirements.txt`
3. `cd FMS`
4. `python manage.py migrate`
5. `python manage.py runserver`  ->  http://127.0.0.1:8000

## Flights
The included database already has ~20,000 flights on 330 routes between 27 Indian cities
for the 30 days from the build date. To refresh or extend the schedule at any time:

    python manage.py seed_flights --days 60

Use `--clear` to remove flights that have no bookings first. You can also add or edit flights in `/admin`.

## Features
- Search with city autocomplete, swap button, 7-day cheapest-fare strip
- Filters and sorting: price, fastest, earliest/latest, airline, departure time, non-stop
- Flight cards with duration, stops, aircraft and meal info
- Visual seat map (Business / Premium Economy / Economy) with live price
- Meal choice, extra baggage, 5% GST, mobile number
- Demo payment (card, UPI, net banking, wallet), printable e-ticket, My Trips
