from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Parent, Driver, Child

class ParentInline(admin.StackedInline):
    model = Parent
    can_delete = False

class DriverInline(admin.StackedInline):
    model = Driver
    can_delete = False

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone_number', 'profile_picture')}),
    )
    
    def get_inlines(self, request, obj=None):
        if obj:
            if obj.user_type == 'parent':
                return [ParentInline]
            elif obj.user_type == 'driver':
                return [DriverInline]
        return []

class ChildAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'parent', 'school_name', 'grade')
    list_filter = ('gender', 'grade')
    search_fields = ('first_name', 'last_name', 'school_name')

class ParentAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'emergency_contact')
    search_fields = ('user__username', 'user__email', 'address')

class DriverAdmin(admin.ModelAdmin):
    list_display = ('user', 'license_number', 'vehicle_model', 'vehicle_plate', 'is_active', 'background_check_verified')
    list_filter = ('is_active', 'background_check_verified')
    search_fields = ('user__username', 'user__email', 'license_number', 'vehicle_plate')
    actions = ['approve_driver', 'deactivate_driver']
    
    def approve_driver(self, request, queryset):
        queryset.update(is_active=True)
    approve_driver.short_description = "Approve selected drivers"
    
    def deactivate_driver(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_driver.short_description = "Deactivate selected drivers"

admin.site.register(User, CustomUserAdmin)
admin.site.register(Parent, ParentAdmin)
admin.site.register(Driver, DriverAdmin)
admin.site.register(Child, ChildAdmin)

print("Account admin configurations created")