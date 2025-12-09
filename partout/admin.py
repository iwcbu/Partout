from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Driver)         # gives access to Driver model to show in database
admin.site.register(Car)            # gives access to Car model to show in database
admin.site.register(Listing)        # gives access to Listing model to show in database
admin.site.register(Follow)         # gives access to Follow model to show in database
admin.site.register(Like)           # gives access to Like model to show in database
# admin.site.register(Comment)        # gives access to Comment model to show in database
admin.site.register(SavedListing)   # gives access to SavedListing model to show in database
admin.site.register(Offer)          # gives access to Offer model to show in database
admin.site.register(DirectMessage)  # gives access to DirectMessage model to show in database
admin.site.register(Message)        # gives access to Message model to show in database
admin.site.register(Rating)         # gives access to Rating model to show in database
