from django.db import models
from accounts.models import User
from rides.models import RideRequest

class Notification(models.Model):
    TYPE_CHOICES = (
        ('ride_request', 'Ride Request'),
        ('ride_accepted', 'Ride Accepted'),
        ('driver_arrived', 'Driver Arrived'),
        ('ride_started', 'Ride Started'),
        ('ride_completed', 'Ride Completed'),
        ('ride_cancelled', 'Ride Cancelled'),
        ('payment', 'Payment'),
        ('system', 'System'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    ride = models.ForeignKey(RideRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=100)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_notification_type_display()} for {self.user.username}: {self.title}"

print("Notification models created")