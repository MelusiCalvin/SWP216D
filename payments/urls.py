from django.urls import path
from . import views

urlpatterns = [
    path('methods/', views.payment_methods, name='payment_methods'),
    path('methods/add/', views.add_payment_method, name='add_payment_method'),
    path('methods/<int:method_id>/set-default/', views.set_default_payment_method, name='set_default_payment_method'),
    path('methods/<int:method_id>/delete/', views.delete_payment_method, name='delete_payment_method'),
    
    path('process/<int:ride_id>/', views.process_payment, name='process_payment'),
    path('history/', views.payment_history, name='payment_history'),
]

print("Payment URLs created")