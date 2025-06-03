from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from payments.models import Payment
from .forms import UserRegistrationForm, ParentProfileForm, DriverProfileForm, ChildForm
from .models import User, Parent, Driver, Child
from django.db import transaction
from rides.models import RideRequest


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            with transaction.atomic():
                user = user_form.save(commit=False)
                user.save()
                
                if user.user_type == 'parent':
                    return redirect('parent_profile_setup')
                elif user.user_type == 'driver':
                    return redirect('driver_profile_setup')
                else:
                    login(request, user)
                    return redirect('dashboard')
    else:
        user_form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'user_form': user_form})

@login_required
def parent_profile_setup(request):
    if hasattr(request.user, 'parent_profile'):
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = ParentProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            
            messages.success(request, 'Your parent profile has been created successfully!')
            login(request, request.user)
            return redirect('dashboard')
    else:
        form = ParentProfileForm()
    
    return render(request, 'accounts/parent_profile_setup.html', {'form': form})

@login_required
def driver_profile_setup(request):
    if hasattr(request.user, 'driver_profile'):
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = DriverProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            
            messages.success(request, 'Your driver profile has been created successfully! Our team will review your information.')
            login(request, request.user)
            return redirect('dashboard')
    else:
        form = DriverProfileForm()
    
    return render(request, 'accounts/driver_profile_setup.html', {'form': form})

@login_required
def dashboard(request):
    user = request.user
    context = {'user': user}
    
    if user.user_type == 'parent':
        parent = Parent.objects.get(user=user)
        children = Child.objects.filter(parent=parent)
        context.update({
            'parent': parent,
            'children': children,
        })
        return render(request, 'accounts/parent_dashboard.html', context)
    
    elif user.user_type == 'driver':
        driver = Driver.objects.get(user=user)
        context.update({
            'driver': driver,
        })
        return render(request, 'accounts/driver_dashboard.html', context)
    
    else:  # Admin
        from django.db.models import Count, Sum
        from django.utils import timezone
        import datetime
        
        # Get counts for dashboard
        total_users = User.objects.count()
        active_rides = RideRequest.objects.filter(status='in_progress').count()
        pending_drivers = Driver.objects.filter(is_active=False).count()
        
        # Calculate total revenue
        total_revenue = Payment.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Get pending drivers for approval
        pending_driver_list = Driver.objects.filter(is_active=False).select_related('user')[:5]
        
        # Get recent rides
        recent_rides = RideRequest.objects.all().order_by('-created_at')[:5]
        
        # User statistics
        parent_count = Parent.objects.count()
        driver_count = Driver.objects.count()
        child_count = Child.objects.count()
        
        # New users this month
        first_day_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        new_users_this_month = User.objects.filter(date_joined__gte=first_day_of_month).count()
        new_users_percentage = (new_users_this_month / total_users * 100) if total_users > 0 else 0
        
        context.update({
            'total_users': total_users,
            'active_rides': active_rides,
            'pending_drivers': pending_drivers,
            'total_revenue': total_revenue,
            'pending_driver_list': pending_driver_list,
            'recent_rides': recent_rides,
            'parent_count': parent_count,
            'driver_count': driver_count,
            'child_count': child_count,
            'new_users_this_month': new_users_this_month,
            'new_users_percentage': new_users_percentage,
        })
        
        return render(request, 'accounts/admin_dashboard.html', context)
@login_required
def add_child(request):
    if request.user.user_type != 'parent':
        messages.error(request, 'Only parents can add children.')
        return redirect('dashboard')
    
    parent = Parent.objects.get(user=request.user)
    
    if request.method == 'POST':
        form = ChildForm(request.POST, request.FILES)
        if form.is_valid():
            child = form.save(commit=False)
            child.parent = parent
            child.save()
            
            messages.success(request, f'{child.first_name} has been added successfully!')
            return redirect('dashboard')
    else:
        form = ChildForm()
    
    return render(request, 'accounts/add_child.html', {'form': form})

@login_required
def edit_child(request, child_id):
    if request.user.user_type != 'parent':
        messages.error(request, 'Only parents can edit children.')
        return redirect('dashboard')
    
    parent = Parent.objects.get(user=request.user)
    child = get_object_or_404(Child, id=child_id, parent=parent)
    
    if request.method == 'POST':
        form = ChildForm(request.POST, request.FILES, instance=child)
        if form.is_valid():
            form.save()
            
            messages.success(request, f'{child.first_name}\'s information has been updated successfully!')
            return redirect('dashboard')
    else:
        form = ChildForm(instance=child)
    
    return render(request, 'accounts/edit_child.html', {'form': form, 'child': child})

@login_required
def profile(request):
    user = request.user
    
    if user.user_type == 'parent':
        parent = Parent.objects.get(user=user)
        if request.method == 'POST':
            # Use UserChangeForm instead of UserRegistrationForm
            from django.contrib.auth.forms import UserChangeForm
            
            # Create a custom form that excludes password fields
            class CustomUserChangeForm(UserChangeForm):
                class Meta:
                    model = User
                    fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']
                    
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    # Remove the password field
                    if 'password' in self.fields:
                        del self.fields['password']
                    # Add form-control class to all fields
                    for field in self.fields:
                        self.fields[field].widget.attrs.update({'class': 'form-control'})
            
            user_form = CustomUserChangeForm(request.POST, instance=user)
            profile_form = ParentProfileForm(request.POST, instance=parent)
            
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, 'Your profile has been updated successfully!')
                return redirect('profile')
        else:
            # Use the custom form for GET requests too
            from django.contrib.auth.forms import UserChangeForm
            
            class CustomUserChangeForm(UserChangeForm):
                class Meta:
                    model = User
                    fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']
                    
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    if 'password' in self.fields:
                        del self.fields['password']
                    for field in self.fields:
                        self.fields[field].widget.attrs.update({'class': 'form-control'})
            
            user_form = CustomUserChangeForm(instance=user)
            profile_form = ParentProfileForm(instance=parent)
        
        return render(request, 'accounts/profile.html', {
            'user_form': user_form,
            'profile_form': profile_form
        })
    
    elif user.user_type == 'driver':
        driver = Driver.objects.get(user=user)
        if request.method == 'POST':
            # Use the same custom form for drivers
            from django.contrib.auth.forms import UserChangeForm
            
            class CustomUserChangeForm(UserChangeForm):
                class Meta:
                    model = User
                    fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']
                    
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    if 'password' in self.fields:
                        del self.fields['password']
                    for field in self.fields:
                        self.fields[field].widget.attrs.update({'class': 'form-control'})
            
            user_form = CustomUserChangeForm(request.POST, instance=user)
            profile_form = DriverProfileForm(request.POST, instance=driver)
            
            if user_form.is_valid() and profile_form.is_valid():
                user_form.save()
                profile_form.save()
                messages.success(request, 'Your profile has been updated successfully!')
                return redirect('profile')
        else:
            from django.contrib.auth.forms import UserChangeForm
            
            class CustomUserChangeForm(UserChangeForm):
                class Meta:
                    model = User
                    fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']
                    
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    if 'password' in self.fields:
                        del self.fields['password']
                    for field in self.fields:
                        self.fields[field].widget.attrs.update({'class': 'form-control'})
            
            user_form = CustomUserChangeForm(instance=user)
            profile_form = DriverProfileForm(instance=driver)
        
        return render(request, 'accounts/profile.html', {
            'user_form': user_form,
            'profile_form': profile_form
        })
    
    else:  # Admin
        if request.method == 'POST':
            from django.contrib.auth.forms import UserChangeForm
            
            class CustomUserChangeForm(UserChangeForm):
                class Meta:
                    model = User
                    fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']
                    
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    if 'password' in self.fields:
                        del self.fields['password']
                    for field in self.fields:
                        self.fields[field].widget.attrs.update({'class': 'form-control'})
            
            user_form = CustomUserChangeForm(request.POST, instance=user)
            
            if user_form.is_valid():
                user_form.save()
                messages.success(request, 'Your profile has been updated successfully!')
                return redirect('profile')
        else:
            from django.contrib.auth.forms import UserChangeForm
            
            class CustomUserChangeForm(UserChangeForm):
                class Meta:
                    model = User
                    fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']
                    
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    if 'password' in self.fields:
                        del self.fields['password']
                    for field in self.fields:
                        self.fields[field].widget.attrs.update({'class': 'form-control'})
            
            user_form = CustomUserChangeForm(instance=user)
        
        return render(request, 'accounts/profile.html', {
            'user_form': user_form
        })
print("Account views created")