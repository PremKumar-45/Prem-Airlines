"""Generate a realistic flight schedule.

    python manage.py seed_flights            # next 30 days
    python manage.py seed_flights --days 60  # next 60 days
    python manage.py seed_flights --clear    # wipe flights that have no bookings first

Safe to run repeatedly: a flight number that already exists on a given day is skipped.
"""
import math
import random
from datetime import datetime, time, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from flights.cities import CITIES
from flights.models import Flight

AIRLINES = [
    # name, code, price factor, meal included, aircraft
    ('Prem Airlines', 'PA', 1.15, True, ['Airbus A321neo', 'Boeing 737-800']),
    ('IndiGo', '6E', 0.90, False, ['Airbus A320neo', 'Airbus A321neo', 'ATR 72']),
    ('Air India', 'AI', 1.10, True, ['Airbus A320neo', 'Boeing 787-8', 'Airbus A321']),
    ('Akasa Air', 'QP', 0.88, False, ['Boeing 737 MAX 8']),
    ('SpiceJet', 'SG', 0.85, False, ['Boeing 737-800', 'Bombardier Q400']),
    ('Air India Express', 'IX', 0.87, False, ['Boeing 737-800']),
]

SLOTS = [(5, 30), (7, 15), (9, 45), (12, 0), (14, 30), (17, 10), (19, 45), (21, 30)]


def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[1], a[2], b[1], b[2]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))


def build_routes():
    """Hubs are fully connected; every other city connects to all hubs plus a few neighbours."""
    names = list(CITIES)
    hubs = [c for c in names if CITIES[c][3]]
    pairs = set()
    for a in hubs:
        for b in hubs:
            if a != b:
                pairs.add((a, b))
    for c in names:
        if c in hubs:
            continue
        for h in hubs:
            # skip silly tiny hops, keep everything else
            if km(CITIES[c], CITIES[h]) > 150:
                pairs.add((c, h))
                pairs.add((h, c))
        near = sorted((n for n in names if n != c and n not in hubs),
                      key=lambda n: km(CITIES[c], CITIES[n]))[:2]
        for n in near:
            if km(CITIES[c], CITIES[n]) > 150:
                pairs.add((c, n))
                pairs.add((n, c))
    return sorted(pairs)


class Command(BaseCommand):
    help = 'Seed the database with a realistic flight schedule.'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=30)
        parser.add_argument('--clear', action='store_true')

    def handle(self, *args, **opts):
        random.seed(2026)
        tz = timezone.get_current_timezone()
        today = timezone.localdate()

        if opts['clear']:
            n, _ = Flight.objects.filter(booking__isnull=True).delete()
            self.stdout.write(f'Removed {n} flights without bookings.')

        existing = set(Flight.objects.filter(departure__date__gte=today)
                       .values_list('fligt_number', 'departure'))
        new = []
        routes = build_routes()
        number_for = {}  # (route, airline code) -> number, so the same flight repeats daily

        for src, dst in routes:
            s, d = CITIES[src], CITIES[dst]
            dist = km(s, d)
            hub_pair = s[3] and d[3]
            per_day = 4 if hub_pair else 2
            slots = random.sample(SLOTS, per_day)
            for slot in sorted(slots):
                name, code, factor, meal, crafts = random.choice(AIRLINES)
                key = (src, dst, slot)
                number_for[key] = f"{code}{random.randint(100, 999)}"
                stops = 1 if dist > 1800 and random.random() < 0.15 else 0
                minutes = int(35 + dist / 12.5 + (70 if stops else 0))
                craft = random.choice(crafts)
                for day in range(opts['days']):
                    base_day = today + timedelta(days=day)
                    dep = timezone.make_aware(datetime.combine(base_day, time(*slot)), tz)
                    if dep <= timezone.now() + timedelta(hours=2):
                        continue
                    num = number_for[key]
                    if (num, dep) in existing:
                        continue
                    # weekends & close-in dates cost more
                    mult = 1 + (0.12 if dep.weekday() >= 4 else 0) + max(0, (5 - day)) * 0.04
                    price = (1500 + dist * 4.2) * factor * mult * random.uniform(0.95, 1.08)
                    price = round(price / 10) * 10 - 1 + 0.0
                    new.append(Flight(
                        fligt_number=num, airline=name, source=src, destination=dst,
                        departure=dep, arrival=dep + timedelta(minutes=minutes),
                        price=price, seats=60, aircraft=craft, stops=stops, meal_included=meal,
                    ))
        Flight.objects.bulk_create(new, batch_size=1000)
        self.stdout.write(self.style.SUCCESS(
            f'Created {len(new)} flights on {len(routes)} routes for the next {opts["days"]} days.'))
