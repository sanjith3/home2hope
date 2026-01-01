from django import forms
from .models import Task, Item, TaskPhoto, User

class TaskCreationForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['donor_name', 'address', 'phone_numbers', 'location_link', 'category','qty', 'is_urgent', 'assigned_to']
        widgets = {
            'qty':forms.NumberInput(attrs={'class':'form-control','placeholder':'Quantity'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'is_urgent': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(role='DRIVER')
        self.fields['assigned_to'].label_from_instance = lambda obj: f"{obj.username} ({obj.phone_number})"
        self.fields['assigned_to'].required = False
        self.fields['assigned_to'].empty_label = "Broadcast to All Drivers"
        
        for field in self.fields:
            if field != 'is_urgent':
                self.fields[field].widget.attrs.update({'class': 'form-control'})

class TaskCompletionForm(forms.ModelForm):
    # This form handles the boolean flags and summary
    class Meta:
        model = Task
        fields = ['visitor_form_filled', 'trust_notice_given']
        widgets = {
            'visitor_form_filled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'trust_notice_given': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['category', 'quantity', 'condition']
        widgets = {
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
        }

class TaskPhotoForm(forms.ModelForm):
    class Meta:
        model = TaskPhoto
        fields = ['image', 'photo_type']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'photo_type': forms.Select(attrs={'class': 'form-select'}),
        }
class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class TaskPhotoMultipleForm(forms.Form):
    image1 = forms.ImageField(label='Photo 1 (Item)', required=True, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    image2 = forms.ImageField(label='Photo 2 (Item)', required=True, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    image3 = forms.ImageField(label='Photo 3 (Item)', required=True, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    image4 = forms.ImageField(label='Photo 4 (Item)', required=True, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    image5 = forms.ImageField(label='Photo 5 (Donor/Front)', required=True, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
    image6 = forms.ImageField(label='Photo 6 (Visitor Form)', required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control'}))
