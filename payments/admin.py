from django.contrib import admin
from .models import PaymentMethod, Payment, DriverPayout

class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('parent', 'payment_type', 'is_default', 'created_at')
    list_filter = ('payment_type', 'is_default')
    search_fields = ('parent__user__username', 'parent__user__email')

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('ride', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('ride__parent__user__username', 'transaction_id')
    date_hierarchy = 'created_at'

class DriverPayoutAdmin(admin.ModelAdmin):
    list_display = ('driver', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('driver__user__username', 'transaction_id')
    date_hierarchy = 'created_at'

admin.site.register(PaymentMethod, PaymentMethodAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(DriverPayout, DriverPayoutAdmin)

print("Payment admin configurations created")