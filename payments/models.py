from django.db import models
from accounts.models import Parent, Driver
from rides.models import RideRequest

class PaymentMethod(models.Model):
    PAYMENT_TYPE_CHOICES = (
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('paypal', 'PayPal'),
    )
    
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='payment_methods')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    
    # For credit/debit cards
    card_last_four = models.CharField(max_length=4, blank=True)
    card_expiry_month = models.CharField(max_length=2, blank=True)
    card_expiry_year = models.CharField(max_length=4, blank=True)
    card_brand = models.CharField(max_length=20, blank=True)
    
    # For PayPal
    paypal_email = models.EmailField(blank=True)
    
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.payment_type in ['credit_card', 'debit_card']:
            return f"{self.get_payment_type_display()} ending in {self.card_last_four}"
        else:
            return f"{self.get_payment_type_display()}: {self.paypal_email}"

class Payment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    ride = models.OneToOneField(RideRequest, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, related_name='payments')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment for Ride #{self.ride.id}: ${self.amount} - {self.get_status_display()}"

class DriverPayout(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
    )
    
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='payouts')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payout to {self.driver.user.username}: ${self.amount} - {self.get_status_display()}"

print("Payment models created")