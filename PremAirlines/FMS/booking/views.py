import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from flights.models import Flight
from .models import Booking
from .pricing import (all_seats, seat_class, quote, ROWS, CLASS_MULT, MEAL_PRICE,
                      BAGGAGE_PER_BLOCK, MAX_BAGGAGE_BLOCKS)


def _book_context(flight, error=None, form=None):
    booked = set(Booking.objects.filter(flight=flight).values_list('seat_number', flat=True))
    rows = []
    for r in ROWS:
        rows.append({'n': r, 'cls': seat_class(f'{r}A').lower(),
                     'left': [{'id': f'{r}{l}', 'taken': f'{r}{l}' in booked} for l in 'ABC'],
                     'right': [{'id': f'{r}{l}', 'taken': f'{r}{l}' in booked} for l in 'DEF']})
    return {
        'data': flight, 'rows': rows, 'error': error, 'form': form or {},
        'free': len(all_seats()) - len(booked),
        'meals': Booking.MEALS, 'mult': {k: float(v) for k, v in CLASS_MULT.items()},
        'meal_price': MEAL_PRICE, 'bag_price': BAGGAGE_PER_BLOCK,
        'meal_included': flight.meal_included, 'max_bag': MAX_BAGGAGE_BLOCKS,
    }


@login_required(login_url='login')
def book_flight(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    if flight.departure <= timezone.now():
        messages.info(request, 'That flight has already departed.')
        return redirect('home')

    if request.method == 'POST':
        name = request.POST.get('pname', '').strip()
        seat = request.POST.get('snum', '')
        meal = request.POST.get('meal', 'NONE')
        phone = request.POST.get('phone', '').strip()
        try:
            bag = int(request.POST.get('baggage', 0))
        except ValueError:
            bag = 0
        bag = min(max(bag, 0), MAX_BAGGAGE_BLOCKS)
        if meal not in dict(Booking.MEALS):
            meal = 'NONE'
        form = {'pname': name, 'snum': seat, 'meal': meal, 'baggage': bag, 'phone': phone}

        if not name:
            return render(request, 'booking.html', _book_context(flight, 'Passenger name is required.', form))
        if phone and not (phone.isdigit() and 10 <= len(phone) <= 12):
            return render(request, 'booking.html', _book_context(flight, 'Enter a valid mobile number.', form))
        if seat not in all_seats():
            return render(request, 'booking.html', _book_context(flight, 'Please pick a seat from the seat map.', form))

        with transaction.atomic():
            if Booking.objects.filter(flight=flight, seat_number=seat).exists():
                form['snum'] = ''
                return render(request, 'booking.html',
                              _book_context(flight, 'That seat is no longer available. Please pick another.', form))
            q = quote(flight, seat, meal, bag)
            booking = Booking.objects.create(
                user=request.user, flight=flight, passenger_name=name, seat_number=seat,
                travel_class=q['class'], meal=meal,
                extra_baggage=bag, phone=phone, amount=q['total'],
            )
        return redirect('payment', id=booking.id)

    return render(request, 'booking.html', _book_context(flight, form={
        'pname': request.user.get_full_name(), 'meal': 'NONE', 'baggage': 0}))


@login_required(login_url='login')
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related('flight').order_by('-booking_date')
    return render(request, 'mybook.html', {'data': bookings})


@login_required(login_url='login')
def payment(request, id):
    booking = get_object_or_404(Booking, id=id, user=request.user)
    if booking.is_paid:
        return redirect('ticket', id=booking.id)

    context = {'booking': booking, 'methods': Booking.PAYMENT_METHODS}

    if request.method == 'POST':
        method = request.POST.get('method', '')
        valid = [m[0] for m in Booking.PAYMENT_METHODS]
        context['selected'] = method
        error = None

        if method not in valid:
            error = 'Please choose a payment method.'
        elif method == 'CARD':
            number = request.POST.get('card_number', '').replace(' ', '')
            expiry = request.POST.get('expiry', '').strip()
            cvv = request.POST.get('cvv', '').strip()
            holder = request.POST.get('card_name', '').strip()
            if not (number.isdigit() and 13 <= len(number) <= 19):
                error = 'Enter a valid card number.'
            elif len(expiry) != 5 or expiry[2] != '/' or not (expiry[:2] + expiry[3:]).isdigit() \
                    or not 1 <= int(expiry[:2]) <= 12:
                error = 'Enter expiry as MM/YY.'
            elif not (cvv.isdigit() and len(cvv) in (3, 4)):
                error = 'Enter a valid CVV.'
            elif not holder:
                error = 'Enter the name on the card.'
        elif method == 'UPI':
            upi = request.POST.get('upi_id', '').strip()
            if '@' not in upi or len(upi) < 5:
                error = 'Enter a valid UPI ID (e.g. name@bank).'
        elif method == 'NETBANKING':
            if not request.POST.get('bank'):
                error = 'Please select your bank.'
        elif method == 'WALLET':
            if not request.POST.get('wallet'):
                error = 'Please select a wallet.'

        if error:
            context['error'] = error
        else:
            # NOTE: demo/simulated gateway. Replace this block with a real
            # gateway (Razorpay, Stripe, ...) call for production. Card numbers
            # and CVV are intentionally NOT stored.
            booking.payment_method = method
            booking.payment_status = Booking.PAYMENT_PAID
            booking.payment_reference = 'PREM' + uuid.uuid4().hex[:10].upper()
            booking.paid_at = timezone.now()
            booking.save()
            messages.success(request, 'Payment successful. Your ticket is confirmed!')
            return redirect('ticket', id=booking.id)

    return render(request, 'payment.html', context)


@login_required(login_url='login')
def ticket(request, id):
    booking = get_object_or_404(Booking, id=id, user=request.user)
    if not booking.is_paid:
        return redirect('payment', id=booking.id)
    return render(request, 'ticket.html', {'booking': booking})


@login_required(login_url='login')
def cancel(request, id):
    booking = get_object_or_404(Booking, id=id, user=request.user)
    if request.method == 'POST':
        booking.delete()
        messages.info(request, 'Booking cancelled.')
    return redirect('mybookings')
