from datetime import timedelta

from django.db.models import Count, Min
from django.shortcuts import render
from django.utils import timezone

from .cities import CITIES, CITY_NAMES
from .models import Flight

SORTS = {
    'price': ('price', 'Cheapest'),
    'early': ('departure', 'Earliest'),
    'late': ('-departure', 'Latest'),
    'fast': (None, 'Fastest'),
}

POPULAR = [
    ('Delhi', 'Mumbai'), ('Mumbai', 'Goa'), ('Bengaluru', 'Delhi'),
    ('Kolkata', 'Chennai'), ('Delhi', 'Srinagar'), ('Hyderabad', 'Kochi'),
]


def home(request):
    ctx = {'cities': CITY_NAMES, 'sorts': SORTS, 'today': timezone.localdate().isoformat()}
    g = request.GET

    if g.get('source'):
        source = g.get('source', '').strip()
        destination = g.get('destination', '').strip()
        date = g.get('departure', '').strip()
        sort = g.get('sort', 'price')
        airline = g.get('airline', '').strip()
        nonstop = g.get('nonstop') == '1'
        max_price = g.get('max_price', '').strip()
        slot = g.get('slot', '').strip()

        base = Flight.objects.filter(source__iexact=source, destination__iexact=destination,
                                     departure__gt=timezone.now())
        if date:
            base = base.filter(departure__date=date)
        ctx['airlines'] = sorted(base.values_list('airline', flat=True).distinct())

        flights = base
        if airline:
            flights = flights.filter(airline=airline)
        if nonstop:
            flights = flights.filter(stops=0)
        if max_price.isdigit():
            flights = flights.filter(price__lte=int(max_price))

        flights = list(flights.order_by(SORTS.get(sort, SORTS['price'])[0] or 'departure')[:200])
        if slot:
            ranges = {'morning': (5, 12), 'afternoon': (12, 17), 'evening': (17, 24), 'night': (0, 5)}
            lo, hi = ranges.get(slot, (0, 24))
            flights = [f for f in flights if lo <= timezone.localtime(f.departure).hour < hi]
        if sort == 'fast':
            flights.sort(key=lambda f: f.duration_minutes)
        elif sort == 'price':
            flights.sort(key=lambda f: f.price)

        ctx.update(flights=flights, searched=True, sort=sort, airline=airline,
                   nonstop=nonstop, max_price=max_price, slot=slot,
                   count=len(flights), codes=CITIES)
        # date strip: cheapest fare for the next 7 days on this route
        strip = []
        start = timezone.localdate()
        for i in range(7):
            d = start + timedelta(days=i)
            low = Flight.objects.filter(source__iexact=source, destination__iexact=destination,
                                        departure__date=d, departure__gt=timezone.now()
                                        ).aggregate(m=Min('price'))['m']
            strip.append({'date': d, 'low': low})
        ctx['strip'] = strip
    else:
        ctx['popular'] = []
        for s, d in POPULAR:
            low = Flight.objects.filter(source=s, destination=d, departure__gt=timezone.now()
                                        ).aggregate(m=Min('price'))['m']
            if low:
                ctx['popular'].append({'source': s, 'destination': d, 'low': low,
                                       'sc': CITIES[s][0], 'dc': CITIES[d][0]})
        ctx['stats'] = {
            'flights': Flight.objects.filter(departure__gt=timezone.now()).count(),
            'cities': len(CITY_NAMES),
            'airlines': Flight.objects.values('airline').distinct().count(),
        }
    return render(request, 'home.html', ctx)
