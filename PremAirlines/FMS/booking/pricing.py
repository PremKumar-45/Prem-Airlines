from decimal import Decimal

# seat rows -> class
BUSINESS_ROWS = range(1, 3)    # rows 1-2
PREMIUM_ROWS = range(3, 6)     # rows 3-5
ROWS = range(1, 11)
LETTERS = 'ABCDEF'

CLASS_MULT = {'ECONOMY': Decimal('1.00'), 'PREMIUM': Decimal('1.35'), 'BUSINESS': Decimal('2.20')}
MEAL_PRICE = {'NONE': 0, 'VEG': 350, 'NONVEG': 400, 'JAIN': 350}
BAGGAGE_PER_BLOCK = 900   # per extra 5 kg
MAX_BAGGAGE_BLOCKS = 4
GST = Decimal('0.05')


def all_seats():
    return [f"{r}{l}" for r in ROWS for l in LETTERS]


def seat_class(seat):
    row = int(seat[:-1])
    if row in BUSINESS_ROWS:
        return 'BUSINESS'
    if row in PREMIUM_ROWS:
        return 'PREMIUM'
    return 'ECONOMY'


def quote(flight, seat, meal, baggage, meal_included=None):
    """Return dict with every price component. Server side source of truth."""
    cls = seat_class(seat)
    fare = (flight.price * CLASS_MULT[cls]).quantize(Decimal('1'))
    included = flight.meal_included if meal_included is None else meal_included
    meal_cost = 0 if (included or cls != 'ECONOMY') else MEAL_PRICE.get(meal, 0)
    bag = BAGGAGE_PER_BLOCK * baggage
    subtotal = fare + meal_cost + bag
    tax = (subtotal * GST).quantize(Decimal('1'))
    return {'class': cls, 'fare': fare, 'meal': Decimal(meal_cost), 'baggage': Decimal(bag),
            'tax': tax, 'total': subtotal + tax}
