from django.contrib import admin
from .models import Location, RideRequest, RecurringRide, RideTracking, Rating

class RideTrackingInline(admin.TabularInline):
    model = RideTracking
    extra = 0

class RecurringRideInline(admin.StackedInline):
    model = RecurringRide
    can_delete = True
    extra = 0

class RatingInline(admin.StackedInline):
    model = Rating
    can_delete = True
    extra = 0

class RideRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'child', 'ride_type', 'status', 'scheduled_time', 'driver')
    list_filter = ('status', 'ride_type', 'scheduled_time')
    search_fields = ('child__first_name', 'child__last_name', 'parent__user__username', 'driver__user__username')
    inlines = [RecurringRideInline, RideTrackingInline, RatingInline]
    date_hierarchy = 'scheduled_time'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('parent', 'child', 'ride_type', 'status')
        }),
        ('Locations', {
            'fields': ('pickup_location', 'dropoff_location')
        }),
        ('Timing', {
            'fields': ('scheduled_time', 'pickup_time', 'dropoff_time')
        }),
        ('Driver', {
            'fields': ('driver',)
        }),
        ('Fare', {
            'fields': ('estimated_fare', 'actual_fare')
        }),
        ('Additional Information', {
            'fields': ('special_instructions',)
        }),
    )

class LocationAdmin(admin.ModelAdmin):
    list_display = ('address', 'name', 'latitude', 'longitude')
    search_fields = ('address', 'name')

class RatingAdmin(admin.ModelAdmin):
    list_display = ('ride', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')

admin.site.register(Location, LocationAdmin)
admin.site.register(RideRequest, RideRequestAdmin)
admin.site.register(Rating, RatingAdmin)

print("Ride admin configurations created")