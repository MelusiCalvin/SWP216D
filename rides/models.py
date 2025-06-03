from django.db import models
from accounts.models import Parent, Child, Driver

class Location(models.Model):
    address = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    name = models.CharField(max_length=100, blank=True)  # Optional name for saved locations
    
    def __str__(self):
        return self.address

class RideRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    RIDE_TYPE_CHOICES = (
        ('home_to_school', 'Home to School'),
        ('school_to_home', 'School to Home'),
    )
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='ride_requests')
    child = models.ForeignKey(Child, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True)
    ride_type = models.CharField(max_length=20, choices=RIDE_TYPE_CHOICES, default='home_to_school')
    # Pickup location
    pickup_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='pickup_rides', null=True, blank=True)
    pickup_address = models.TextField(default='Roodepoort', null=False)
    pickup_latitude = models.FloatField(default=-26.137657)  # Default to Roodepoort coordinates
    pickup_longitude = models.FloatField(default=27.805727)  # Default to Roodepoort coordinates
    pickup_place_id = models.CharField(max_length=255, blank=True, null=True)  # Google Place ID
    
    # Dropoff location
    dropoff_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='dropoff_rides', null=True, blank=True)
    dropoff_address = models.TextField(default='Soweto', null=False)
    dropoff_latitude = models.FloatField(default=-26.2673)  # Default to Soweto coordinates
    dropoff_longitude = models.FloatField(default=-26.2673)  # Default to Soweto coordinates
    dropoff_place_id = models.CharField(max_length=255, blank=True, null=True)  # Google Place ID
    
    scheduled_time = models.DateTimeField()  # Changed from pickup_time to match your views
    pickup_time = models.DateTimeField(null=True, blank=True)  # Actual pickup time
    estimated_dropoff_time = models.DateTimeField(null=True, blank=True)
    dropoff_time = models.DateTimeField(null=True, blank=True)  # Actual dropoff time
    
    distance = models.FloatField(default=0.0)  # in kilometers
    estimated_fare = models.DecimalField(max_digits=10, decimal_places=2)
    actual_fare = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_paid = models.BooleanField(default=False)
    
    special_instructions = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"RideRequest #{self.id} - {self.child.first_name} - {self.status}"
        
class RecurringRide(models.Model):
    DAYS_OF_WEEK = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )
    
    ride_request = models.OneToOneField(RideRequest, on_delete=models.CASCADE, related_name='recurring_ride')
    days_of_week = models.CharField(max_length=13)  # Stored as comma-separated integers (e.g., "0,2,4")
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        days = [self.DAYS_OF_WEEK[int(day)][1] for day in self.days_of_week.split(',')]
        return f"Recurring ride on {', '.join(days)}"

class RideTracking(models.Model):
    ride = models.ForeignKey(RideRequest, on_delete=models.CASCADE, related_name='tracking_points')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Tracking for Ride #{self.ride.id} at {self.timestamp}"

class Rating(models.Model):
    ride = models.OneToOneField(RideRequest, on_delete=models.CASCADE, related_name='rating')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Rating for Ride #{self.ride.id}: {self.rating}/5"

print("Ride models created")