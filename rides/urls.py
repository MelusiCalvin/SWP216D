from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('dashboard/', views.home, name='parent-dashboard'),
    
    path('request/', views.request_ride, name='request_ride'),
    path('my-rides/', views.my_rides, name='my_rides'),
    path('available-rides/', views.available_rides, name='available_rides'),
    
    path('ride/<int:ride_id>/', views.ride_details, name='ride_details'),
    path('ride/<int:ride_id>/cancel/', views.cancel_ride, name='cancel_ride'),
    path('ride/<int:ride_id>/rate/', views.rate_ride, name='rate_ride'),
    
    path('ride/<int:ride_id>/accept/', views.accept_ride, name='accept_ride'),
    path('ride/<int:ride_id>/start/', views.start_ride, name='start_ride'),
    path('ride/<int:ride_id>/complete/', views.complete_ride, name='complete_ride'),
    
    path('update-location/', views.update_location, name='update_location'),
]

print("Ride URLs created")