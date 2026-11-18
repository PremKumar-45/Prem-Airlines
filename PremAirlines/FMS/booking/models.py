from django.db import models
from django.contrib.auth.models import User
from flights.models import Flight


class Booking(models.Model):
    PAYMENT_PENDING = 'PENDING'
    PAYMENT_PAID = 'PAID'
    PAYMENT_STATUS = [
        (PAYMENT_PENDING, 'Pending'),
        (PAYMENT_PAID, 'Paid'),
    ]

    PAYMENT_METHODS = [
        ('CARD', 'Credit / Debit Card'),
        ('UPI', 'UPI'),
        ('NETBANKING', 'Net Banking'),
        ('WALLET', 'Wallet'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)

    passenger_name = models.CharField(max_length=30)
    seat_number = models.CharField(max_length=10)
    booking_date = models.DateTimeField(auto_now_add=True)

    # ---- travel options ----
    CLASSES = [
        ('ECONOMY', 'Economy'),
        ('PREMIUM', 'Premium Economy'),
        ('BUSINESS', 'Business'),
    ]
    MEALS = [
        ('NONE', 'No meal'),
        ('VEG', 'Veg meal'),
        ('NONVEG', 'Non-veg meal'),
        ('JAIN', 'Jain meal'),
    ]
    travel_class = models.CharField(max_length=10, choices=CLASSES, default='ECONOMY')
    meal = models.CharField(max_length=8, choices=MEALS, default='NONE')
    extra_baggage = models.PositiveSmallIntegerField(default=0)  # extra 5 kg blocks
    phone = models.CharField(max_length=15, blank=True)

    # ---- payment details ----
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default=PAYMENT_PENDING)
    payment_method = models.CharField(max_length=12, choices=PAYMENT_METHODS, blank=True)
    payment_reference = models.CharField(max_length=40, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    @property
    def is_paid(self):
        return self.payment_status == self.PAYMENT_PAID

    def __str__(self):
        return self.user.username + "-" + self.flight.fligt_number
