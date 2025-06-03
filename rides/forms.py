from django import forms
from .models import RideRequest, RecurringRide, Rating, Location
from accounts.models import Child

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['address', 'latitude', 'longitude', 'name']
        widgets = {
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['address'].widget.attrs.update({
            'class': 'form-control location-input', 
            'placeholder': 'Enter address'
        })
        self.fields['name'].widget.attrs.update({'class': 'form-control'})

class RideRequestForm(forms.ModelForm):
    child = forms.ModelChoiceField(queryset=Child.objects.none(), empty_label="Select a child")
    scheduled_time = forms.DateTimeField( required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
    )
    special_instructions = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False
    )
    
    class Meta:
        model = RideRequest
        fields = ['child', 'pickup_address', 'dropoff_address', 'scheduled_time', 'special_instructions']
        widgets = {
            'pickup_address': forms.TextInput(attrs={
                'class': 'form-control location-input',
                'placeholder': 'Enter pickup address'
            }),
            'dropoff_address': forms.TextInput(attrs={
                'class': 'form-control location-input',
                'placeholder': 'Enter dropoff address'
            }),
            'scheduled_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'id': 'id_scheduled_time',
                'class': 'form-check form-check-inline'
            }),
        }
    
    def __init__(self, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['child'].queryset = Child.objects.filter(parent=parent)

class RecurringRideForm(forms.ModelForm):
    days_of_week = forms.MultipleChoiceField(
        choices=RecurringRide.DAYS_OF_WEEK,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = RecurringRide
        fields = ['days_of_week', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['days_of_week'] = self.instance.days_of_week.split(',')
            self.fields['start_date'].required = False
            self.fields['end_date'].required = False
    
    def clean_days_of_week(self):
        days = self.cleaned_data['days_of_week']
        return ','.join(days)

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Share your experience...'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].widget = forms.RadioSelect(
            choices=[(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)],
            attrs={'class': 'form-check-input'}
        )

print("Ride forms created")