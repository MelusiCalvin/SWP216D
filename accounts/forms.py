from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Parent, Driver, Child

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'user_type', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class ParentProfileForm(forms.ModelForm):
    class Meta:
        model = Parent
        fields = ['address', 'emergency_contact']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ['first_name', 'last_name', 'date_of_birth', 'gender', 'school_name', 
                 'school_address', 'grade', 'special_instructions', 'photo']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'special_instructions': forms.Textarea(attrs={'rows': 3}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class DriverProfileForm(forms.ModelForm):
    class Meta:
        model = Driver
        fields = ['license_number', 'license_expiry', 'vehicle_model', 'vehicle_color',
                 'vehicle_plate', 'vehicle_year', 'insurance_provider', 'insurance_policy_number']
        widgets = {
            'license_expiry': forms.DateInput(attrs={'type': 'date'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

print("Account forms created")