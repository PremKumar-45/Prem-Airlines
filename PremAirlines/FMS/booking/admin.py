from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'flight', 'passenger_name', 'seat_number', 'travel_class',
                    'amount', 'payment_status', 'payment_method', 'payment_reference')
    list_filter = ('travel_class', 'payment_status', 'payment_method')
    search_fields = ('passenger_name', 'user__username', 'payment_reference')
