# partout/forms.py

from django import forms
from .models import *




class CreateProfileForm(forms.ModelForm):
    '''form to create a driver profile'''

    class Meta:
        model = Driver
        fields = ['first_name', 'last_name', 'username', 'email', "city", "state", "zip_code", "profile_image", "bio"]
        
class UpdateProfileForm(forms.ModelForm):
    '''form to update driver profile'''

    class Meta:
        model = Driver
        fields = ['first_name', 'last_name', 'username', 'email', "city", "state", "zip_code", "profile_image", "bio"]
