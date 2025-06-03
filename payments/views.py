from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import PaymentMethod, Payment
from accounts.models import Parent
from rides.models import RideRequest
import json

@login_required
def payment_methods(request):
    if request.user.user_type != 'parent':
        messages.error(request, 'Only parents can manage payment methods.')
        return redirect('dashboard')
    
    parent = Parent.objects.get(user=request.user)
    payment_methods = PaymentMethod.objects.filter(parent=parent)
    
    return render(request, 'payments/payment_methods.html', {
        'payment_methods': payment_methods,
    })

@login_required
def add_payment_method(request):
    if request.user.user_type != 'parent':
        messages.error(request, 'Only parents can add payment methods.')
        return redirect('dashboard')
    
    parent = Parent.objects.get(user=request.user)
    
    if request.method == 'POST':
        payment_type = request.POST.get('payment_type')
        
        # In a real app, this would integrate with a payment processor
        # For this example, we'll just create a dummy payment method
        
        if payment_type == 'credit_card':
            PaymentMethod.objects.create(
                parent=parent,
                payment_type=payment_type,
                card_last_four='1234',
                card_expiry_month='12',
                card_expiry_year='2025',
                card_brand='Visa',
                is_default=not PaymentMethod.objects.filter(parent=parent).exists()
            )
        elif payment_type == 'paypal':
            PaymentMethod.objects.create(
                parent=parent,
                payment_type=payment_type,
                paypal_email=request.POST.get('paypal_email'),
                is_default=not PaymentMethod.objects.filter(parent=parent).exists()
            )
        
        messages.success(request, 'Payment method added successfully!')
        return redirect('payment_methods')
    
    return render(request, 'payments/add_payment_method.html')

@login_required
def set_default_payment_method(request, method_id):
    if request.user.user_type != 'parent':
        messages.error(request, 'Only parents can manage payment methods.')
        return redirect('dashboard')
    
    parent = Parent.objects.get(user=request.user)
    payment_method = get_object_or_404(PaymentMethod, id=method_id, parent=parent)
    
    # Set all payment methods to non-default
    PaymentMethod.objects.filter(parent=parent).update(is_default=False)
    
    # Set the selected method as default
    payment_method.is_default = True
    payment_method.save()
    
    messages.success(request, 'Default payment method updated successfully!')
    return redirect('payment_methods')

@login_required
def delete_payment_method(request, method_id):
    if request.user.user_type != 'parent':
        messages.error(request, 'Only parents can manage payment methods.')
        return redirect('dashboard')
    
    parent = Parent.objects.get(user=request.user)
    payment_method = get_object_or_404(PaymentMethod, id=method_id, parent=parent)
    
    if request.method == 'POST':
        # Check if this is the only payment method
        if payment_method.is_default and PaymentMethod.objects.filter(parent=parent).count() > 1:
            # Set another method as default
            other_method = PaymentMethod.objects.filter(parent=parent).exclude(id=method_id).first()
            other_method.is_default = True
            other_method.save()
        
        payment_method.delete()
        messages.success(request, 'Payment method deleted successfully!')
        return redirect('payment_methods')
    
    return render(request, 'payments/delete_payment_method.html', {
        'payment_method': payment_method,
    })

@login_required
def process_payment(request, ride_id):
    if request.user.user_type != 'parent':
        messages.error(request, 'Only parents can process payments.')
        return redirect('dashboard')
    
    parent = Parent.objects.get(user=request.user)
    ride = get_object_or_404(RideRequest, id=ride_id, parent=parent, status='completed')
    
    # Check if payment already exists
    if hasattr(ride, 'payment'):
        messages.info(request, 'Payment has already been processed for this ride.')
        return redirect('ride_details', ride_id=ride.id)
    
    # Get default payment method
    try:
        payment_method = PaymentMethod.objects.get(parent=parent, is_default=True)
    except PaymentMethod.DoesNotExist:
        messages.error(request, 'Please add a payment method before processing payment.')
        return redirect('add_payment_method')
    
    if request.method == 'POST':
        # In a real app, this would integrate with a payment processor
        # For this example, we'll just create a dummy payment
        
        payment = Payment.objects.create(
            ride=ride,
            payment_method=payment_method,
            amount=ride.actual_fare,
            status='completed',
            transaction_id=f'txn_{ride.id}_{parent.id}'
        )
        
        messages.success(request, 'Payment processed successfully!')
        return redirect('ride_details', ride_id=ride.id)
    
    return render(request, 'payments/process_payment.html', {
        'ride': ride,
        'payment_method': payment_method,
    })

@login_required
def payment_history(request):
    if request.user.user_type != 'parent':
        messages.error(request, 'Only parents can view payment history.')
        return redirect('dashboard')
    
    parent = Parent.objects.get(user=request.user)
    payments = Payment.objects.filter(
        ride__parent=parent
    ).order_by('-created_at')
    
    return render(request, 'payments/payment_history.html', {
        'payments': payments,
    })

print("Payment views created")