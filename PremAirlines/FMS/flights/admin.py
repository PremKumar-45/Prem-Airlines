from django.contrib import admin
from .models import Flight


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('fligt_number', 'airline', 'source', 'destination',
                    'departure', 'arrival', 'price', 'stops')
    list_filter = ('airline', 'source', 'destination', 'stops')
    search_fields = ('fligt_number', 'source', 'destination', 'airline')
    date_hierarchy = 'departure'
