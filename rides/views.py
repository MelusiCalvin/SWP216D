from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse
from .forms import RideRequestForm, RecurringRideForm, RatingForm, LocationForm
from .models import RideRequest, Rating, Location
from accounts.models import Parent, Driver
from decimal import Decimal
from ride2school.settings import GOOGLE_MAPS_API_KEY
import json
import math

@login_required
def home(request):
    return render(request, 'rides/home.html')

@login_required
def request_ride(request):
    if request.user.user_type != 'parent':
        messages.error(request, 'Only parents can request rides.')
        return redirect('parent_dashboard')
    
    parent = Parent.objects.get(user=request.user)
    
    if request.method == 'POST':
        ride_form = RideRequestForm(parent, request.POST)
        pickup_form = LocationForm(request.POST, prefix='pickup')
        dropoff_form = LocationForm(request.POST, prefix='dropoff')
        recurring_form = RecurringRideForm(request.POST)
        
        if ride_form.is_valid():
            with transaction.atomic():
                # Get location data from hidden fields
                pickup_lat = request.POST.get('pickup_latitude')
                pickup_lng = request.POST.get('pickup_longitude')
                pickup_place_id = request.POST.get('pickup_place_id')
                
                dropoff_lat = request.POST.get('dropoff_latitude')
                dropoff_lng = request.POST.get('dropoff_longitude')
                dropoff_place_id = request.POST.get('dropoff_place_id')
                
                # Create pickup location
                pickup_location = Location.objects.create(
                    address=ride_form.cleaned_data['pickup_address'],
                    latitude=pickup_lat,
                    longitude=pickup_lng,
                    name='Pickup Location'
                )
                
                # Create dropoff location
                dropoff_location = Location.objects.create(
                    address=ride_form.cleaned_data['dropoff_address'],
                    latitude=dropoff_lat,
                    longitude=dropoff_lng,
                    name='Dropoff Location'
                )
                
                # Calculate estimated fare
                estimated_fare = calculate_fare(pickup_lat, pickup_lng, dropoff_lat, dropoff_lng)
                
                # Save ride request
                ride = ride_form.save(commit=False)
                ride.parent = parent
                ride.pickup_location = pickup_location
                ride.dropoff_location = dropoff_location
                ride.pickup_latitude = pickup_lat
                ride.pickup_longitude = pickup_lng
                ride.pickup_place_id = pickup_place_id
                ride.dropoff_latitude = dropoff_lat
                ride.dropoff_longitude = dropoff_lng
                ride.dropoff_place_id = dropoff_place_id
                ride.estimated_fare = estimated_fare
                ride.save()
                
                # Handle recurring ride if selected
                is_recurring = request.POST.get('is_recurring') == 'on'
                if is_recurring and recurring_form.is_valid():
                    recurring_ride = recurring_form.save(commit=False)
                    recurring_ride.ride_request = ride
                    recurring_ride.save()
                
                messages.success(request, 'Your ride request has been submitted successfully!')
                return redirect('ride_details', ride_id=ride.id)
    else:
        ride_form = RideRequestForm(parent)
        pickup_form = LocationForm(prefix='pickup')
        dropoff_form = LocationForm(prefix='dropoff')
        recurring_form = RecurringRideForm()
    
    return render(request, 'rides/request_ride.html', {
        'ride_form': ride_form,
        'pickup_form': pickup_form,
        'dropoff_form': dropoff_form,
        'recurring_form': recurring_form,
        'GOOGLE_MAPS_API_KEY': GOOGLE_MAPS_API_KEY,
    })

def calculate_fare(pickup_lat, pickup_lng, dropoff_lat, dropoff_lng):
    """Calculate fare based on distance using Haversine formula"""
    # Convert to float and then to radians
    pickup_lat, pickup_lng, dropoff_lat, dropoff_lng = map(
        lambda x: math.radians(float(x)), 
        [pickup_lat, pickup_lng, dropoff_lat, dropoff_lng]
    )
    
    # Haversine formula
    dlng = dropoff_lng - pickup_lng
    dlat = dropoff_lat - pickup_lat
    a = math.sin(dlat/2)**2 + math.cos(pickup_lat) * math.cos(dropoff_lat) * math.sin(dlng/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of earth in kilometers
    distance = c * r
    
    # Calculate fare: Base fare + distance rate
    base_fare = Decimal('30.00')  # R30 base fare
    rate_per_km = Decimal('8.50')  # R8.50 per km
    
    return base_fare + (Decimal(str(distance)) * rate_per_km)
@login_required
def ride_details(request, ride_id):
    if request.user.user_type == 'parent':
        parent = Parent.objects.get(user=request.user)
        ride = get_object_or_404(RideRequest, id=ride_id, parent=parent)
    elif request.user.user_type == 'driver':
        driver = Driver.objects.get(user=request.user)
        ride = get_object_or_404(RideRequest, id=ride_id, driver=driver)
    else:  # Admin
        ride = get_object_or_404(RideRequest, id=ride_id)
    
    # Check if the ride has a rating
    has_rating = hasattr(ride, 'rating')

    # Prepare days_of_week for the template
    days_of_week = []
    if hasattr(ride, 'recurring_ride') and ride.recurring_ride and ride.recurring_ride.days_of_week:
        days_of_week = ride.recurring_ride.days_of_week.split(',')

    return render(request, 'rides/ride_details.html', {
        'ride': ride,
        'has_rating': has_rating,
        'days_of_week': days_of_week,  # Pass to template
    })

@login_required
def rate_ride(request, ride_id):
    if request.user.user_type != 'parent':
        messages.error(request, 'Only parents can rate rides.')
        return redirect('home')
    
    parent = Parent.objects.get(user=request.user)
    ride = get_object_or_404(RideRequest, id=ride_id, parent=parent, status='completed')
    
    # Check if the ride has already been rated
    if hasattr(ride, 'rating'):
        messages.info(request, 'You have already rated this ride.')
        return redirect('ride_details', ride_id=ride.id)
    
    if request.method == 'POST':
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.ride = ride
            rating.save()
            
            # Update driver's average rating
            if ride.driver:
                driver_ratings = Rating.objects.filter(ride__driver=ride.driver)
                avg_rating = sum(r.rating for r in driver_ratings) / len(driver_ratings)
                ride.driver.rating = round(avg_rating, 1)
                ride.driver.save()
            
            messages.success(request, 'Thank you for rating your ride!')
            return redirect('ride_details', ride_id=ride.id)
    else:
        form = RatingForm()
    
    return render(request, 'rides/rate_ride.html', {
        'form': form,
        'ride': ride,
    })

@login_required
def cancel_ride(request, ride_id):
    if request.user.user_type != 'parent':
        messages.error(request, 'Only parents can cancel rides.')
        return redirect('parent_dashboard')
    
    parent = Parent.objects.get(user=request.user)
    ride = get_object_or_404(RideRequest, id=ride_id, parent=parent)
    
    # Only allow cancellation if the ride is pending or accepted
    if ride.status not in ['pending', 'accepted']:
        messages.error(request, 'This ride cannot be cancelled.')
        return redirect('ride_details', ride_id=ride.id)
    
    if request.method == 'POST':
        ride.status = 'cancelled'
        ride.save()
        
        messages.success(request, 'Your ride has been cancelled successfully.')
        return redirect('my_rides')
    
    return render(request, 'rides/cancel_ride.html', {'ride': ride})

@login_required
def my_rides(request):
    if request.user.user_type == 'parent':
        parent = Parent.objects.get(user=request.user)
        upcoming_rides = RideRequest.objects.filter(
            parent=parent,
            status__in=['pending', 'accepted'],
            scheduled_time__gte=timezone.now()
        ).order_by('scheduled_time')
        
        past_rides = RideRequest.objects.filter(
            parent=parent,
            status__in=['completed', 'cancelled']
        ).order_by('-scheduled_time')
        
        in_progress_rides = RideRequest.objects.filter(
            parent=parent,
            status='in_progress'
        )
        
        return render(request, 'rides/my_rides.html', {
            'upcoming_rides': upcoming_rides,
            'past_rides': past_rides,
            'in_progress_rides': in_progress_rides,
        })
    
    elif request.user.user_type == 'driver':
        driver = Driver.objects.get(user=request.user)
        upcoming_rides = RideRequest.objects.filter(
            driver=driver,
            status='accepted',
            scheduled_time__gte=timezone.now()
        ).order_by('scheduled_time')
        
        past_rides = RideRequest.objects.filter(
            driver=driver,
            status__in=['completed', 'cancelled']
        ).order_by('-scheduled_time')
        
        in_progress_rides = RideRequest.objects.filter(
            driver=driver,
            status='in_progress'
        )
        
        return render(request, 'rides/driver_rides.html', {
            'upcoming_rides': upcoming_rides,
            'past_rides': past_rides,
            'in_progress_rides': in_progress_rides,
        })
    
    else:  # Admin
        return redirect('admin:rides_riderequest_changelist')

@login_required
def available_rides(request):
    if request.user.user_type != 'driver':
        messages.error(request, 'Only drivers can view available rides.')
        return redirect('driver_dashboard')#shouldnt take me to the driver dashboard if not a driver
    
    driver = Driver.objects.get(user=request.user)
    
    # Only active drivers can see available rides
    if not (driver.background_check_verified and driver.is_active):
        print("backgroudcheck: "+ driver.background_check_verified +" is active"+ driver.is_active +" [DEBUG] Driver not verified or not active — redirecting to dashboard")
        messages.warning(request, 'Your account is not verified yet. Please wait for admin approval.')
        return redirect('driver_dashboard')
    
    available_rides = RideRequest.objects.filter(
        status='pending'
    ).order_by('-scheduled_time')
    
    return render(request, 'rides/available_rides.html', {
        'available_rides': available_rides,
    })

@login_required
def accept_ride(request, ride_id):
    if request.user.user_type != 'driver':
        messages.error(request, 'Only drivers can accept rides.')
        return redirect('driver_dashboard')
    
    driver = Driver.objects.get(user=request.user)
    ride = get_object_or_404(RideRequest, id=ride_id, status='pending')
    
    # Only verified drivers can accept rides
    if not driver.is_active or not driver.background_check_verified:
        messages.warning(request, 'Your account is not verified yet. Please wait for admin approval.')
        return redirect('driver_dashboard')
    
    if request.method == 'POST':
        ride.driver = driver
        ride.status = 'accepted'
        ride.save()
        
        messages.success(request, 'You have successfully accepted the ride.')
        return redirect('ride_details', ride_id=ride.id)
    
    return render(request, 'rides/accept_ride.html', {'ride': ride})

@login_required
def start_ride(request, ride_id):
    if request.user.user_type != 'driver':
        messages.error(request, 'Only drivers can start rides.')
        return redirect('driver_dashboard')
    
    driver = Driver.objects.get(user=request.user)
    ride = get_object_or_404(RideRequest, id=ride_id, driver=driver, status='accepted')
    
    if request.method == 'POST':
        ride.status = 'in_progress'
        ride.pickup_time = timezone.now()
        ride.save()
        
        messages.success(request, 'The ride has been started successfully.')
        return redirect('ride_details', ride_id=ride.id)
    
    return render(request, 'rides/start_ride.html', {'ride': ride})

@login_required
def complete_ride(request, ride_id):
    if request.user.user_type != 'driver':
        messages.error(request, 'Only drivers can complete rides.')
        return redirect('driver_dashboard')
    
    driver = Driver.objects.get(user=request.user)
    ride = get_object_or_404(RideRequest, id=ride_id, driver=driver, status='in_progress')
    
    if request.method == 'POST':
        ride.status = 'completed'
        ride.dropoff_time = timezone.now()
        
        # Calculate actual fare (simplified)
        ride.actual_fare = ride.estimated_fare
        ride.save()
        
        # Update driver stats
        driver.total_rides += 1
        driver.total_earnings += ride.actual_fare
        driver.save()
        
        messages.success(request, 'The ride has been completed successfully.')
        return redirect('ride_details', ride_id=ride.id)
    
    return render(request, 'rides/complete_ride.html', {'ride': ride})

@login_required
def update_location(request):
    if request.user.user_type != 'driver':
        return JsonResponse({'error': 'Only drivers can update location'}, status=403)
    
    if request.method == 'POST':
        data = json.loads(request.body)
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        ride_id = data.get('ride_id')
        
        driver = Driver.objects.get(user=request.user)
        
        # Update driver's current location
        driver.current_latitude = latitude
        driver.current_longitude = longitude
        driver.save()
        
        # If there's an active ride, add a tracking point
        if ride_id:
            ride = get_object_or_404(RideRequest, id=ride_id, driver=driver, status='in_progress')
            ride.tracking_points.create(latitude=latitude, longitude=longitude)
        
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

print("Ride views created")