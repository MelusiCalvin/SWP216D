from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('parent', 'Parent'),
        ('driver', 'Driver'),
        ('admin', 'Admin'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

class Parent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
    address = models.CharField(max_length=255)
    emergency_contact = models.CharField(max_length=17, blank=True)
    
    def __str__(self):
        return f"Parent: {self.user.username}"

class Child(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='children')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    school_name = models.CharField(max_length=255)
    school_address = models.CharField(max_length=255)
    grade = models.CharField(max_length=20)
    special_instructions = models.TextField(blank=True)
    photo = models.ImageField(upload_to='child_photos/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} (Child of {self.parent.user.username})"

class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_profile')
    license_number = models.CharField(max_length=50)
    license_expiry = models.DateField()
    vehicle_model = models.CharField(max_length=100)
    vehicle_color = models.CharField(max_length=50)
    vehicle_plate = models.CharField(max_length=20)
    vehicle_year = models.IntegerField()
    insurance_provider = models.CharField(max_length=100)
    insurance_policy_number = models.CharField(max_length=100)
    background_check_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    total_rides = models.IntegerField(default=0)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    rating_count = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Driver: {self.user.username}"

print("Account models created")