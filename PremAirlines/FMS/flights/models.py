from django.db import models


class Flight(models.Model):
    fligt_number = models.CharField(max_length=10)
    airline = models.CharField(max_length=20)

    source = models.CharField(max_length=40)
    destination = models.CharField(max_length=40)

    departure = models.DateTimeField()
    arrival = models.DateTimeField()

    price = models.DecimalField(max_digits=8, decimal_places=2)
    seats = models.PositiveIntegerField(default=60)

    # ---- extra details shown on the search results ----
    aircraft = models.CharField(max_length=30, blank=True, default='Airbus A320')
    stops = models.PositiveSmallIntegerField(default=0)
    meal_included = models.BooleanField(default=False)

    class Meta:
        ordering = ['departure']

    @property
    def duration_minutes(self):
        return max(int((self.arrival - self.departure).total_seconds() // 60), 0)

    @property
    def duration_display(self):
        m = self.duration_minutes
        return f"{m // 60}h {m % 60:02d}m"

    @property
    def stops_display(self):
        return 'Non-stop' if self.stops == 0 else f"{self.stops} stop"

    def __str__(self):
        return self.fligt_number
