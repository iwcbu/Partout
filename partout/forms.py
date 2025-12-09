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

class AddCarForm(forms.ModelForm):
    '''form to add a new car to the db'''

    class Meta:
        model = Car
        fields = [
            "make",
            "model",
            "year",
            "trim" ,
            "style",
            "engine_code",
            "drivetrain",
            "nickname",
            "ownership_type"
        ]

class UpdateCarForm(forms.ModelForm):
    '''form to update a car to the db'''

    class Meta:

        model = Car
        fields = [
            "make",
            "model",
            "year",
            "trim" ,
            "style",
            "engine_code",
            "drivetrain",
            "nickname",
            "ownership_type"
        ]

        
        
class CreateListingForm(forms.ModelForm):
    '''for to create a new listing for the market'''

    class Meta:

        model = Listing
        fields = [
            "title",
            "description",
            "car",
            "part_type",
            "condition",
            "price",
            "open_to_offers",
            "city",
            "state",
            "image",
        ]

    def __init__(self, *args, **kwargs):
        ''' prevents car selection from being all cars, and only allows
            cars from driver's garage'''

        driver = kwargs.pop("driver", None) # pull out driver from kwargs for filtering
        super().__init__(*args, **kwargs)

        if driver is not None:
            # only show this driver's cars
            self.fields["car"].queryset = Car.objects.filter(owner=driver)

class UpdateListingForm(forms.ModelForm):
    '''form to update a listing'''

    class Meta:
        model = Listing
        fields = [
            "title",
            "description",
            "car",
            "part_type",
            "condition",
            "price",
            "open_to_offers",
            "city",
            "state",
            "image",
            "status",
        ]

    def __init__(self, *args, **kwargs):
        ''' prevents car selection from being all cars, and only allows
            cars from driver's garage'''

        driver = kwargs.pop("driver", None) # pull out driver from kwargs for filtering
        super().__init__(*args, **kwargs)

        if driver is not None:
            # only show this driver's cars
            self.fields["car"].queryset = Car.objects.filter(owner=driver)


       
class CreateOfferForm(forms.ModelForm):
    '''for to create a new listing for the market'''

    class Meta:
        model = Offer
        fields = [
            "amount", 
        ]
