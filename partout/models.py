from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Driver(models.Model):
    '''contains driver model data'''
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=10)
    profile_image = models.ImageField(upload_to="drivers/profile_images/", blank=True, null=True)
    bio = models.TextField(blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True) # auth

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    


class Follow(models.Model):
    '''contains a profiles follow/following data'''

    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='driver')
    driver_that_followed = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='driver_that_followed')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        '''string representation of follow model'''

        return f'{self.driver_that_followed} follows {self.driver}' 
    


    def get_followers(driver):
        '''Returns list of profiles that follow a profile'''

        followers = Follow.objects.filter(driver=driver).distinct() # returns query list of follow relationships following profile
        return list(followers)
    
    def get_follower_profiles(driver):
        '''Returns list of profiles that follow a profile'''

        followers = Follow.objects.filter(driver=driver).distinct() 
        return [f.driver_that_followed for f in followers] # turns query list of follow relationships into just the driver profiles
    

    def get_followers_qs(driver):
        '''returns a queryset of profiles that follow a profile'''

        return Driver.objects.filter(driver_that_followed__driver=driver)
        

    def get_num_followers(driver):
        '''Returns number of followers'''

        return Follow.objects.filter(driver=driver).count()
        

    def get_following(driver):
        '''Returns list of profiles that a profile follows'''

        follows = Follow.objects.filter(driver_that_followed=driver) # returns query list of follow relationships that a profile follows
        return list(follows)


    
    
    def get_num_following(driver):
        '''Returns number of profiles a profile follows'''

        return Follow.objects.filter(driver_that_followed=driver).count()
    




class Car(models.Model):
    '''contains car model data'''
    drivetrain_choices = [
        ("FWD", "FWD"),
        ("RWD", "RWD"),
        ("AWD", "AWD"),
    ]

    styling_choices = [
        ("Coupe", "Coupe"),
        ("Convertible", "Convertible"),
        ("Sedan", "Sedan"),
        ("Hatchback", "Hatchback"),
        ("Wagon", "Wagon"),
        ("SUV", "SUV"),
        ("Truck", "Truck"),
        ("Motorcycle", "Motorcycle")
    ]

    ownership_type_choices = [
        ("Primary", "Primary"),
        ("Secondary", "Secondary"),
        ("Track", "Track"),
        ("Drag", "Drag"),
        ("Drift","Drift"),
        ("Rally", "Rally"),
    ]

    owner = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name="cars")
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    trim = models.CharField(max_length=100, blank=True)
    style = models.CharField(max_length=15, choices=styling_choices)
    engine_code = models.CharField(max_length=100, blank=True)
    drivetrain = models.CharField(max_length=3, choices=drivetrain_choices)
    nickname = models.CharField(max_length=100, blank=True)
    ownership_type = models.CharField(max_length=9, choices=ownership_type_choices)

    def __str__(self):
        if self.nickname:
            return f"{self.nickname} ({self.year} {self.make} {self.model} {self.trim})"
        return f"{self.year} {self.make} {self.model} {self.trim}"


class Listing(models.Model):
    '''contains listing model data'''

    condition_choices = [
        ("new", "New"),
        ("like_new", "Like New"),
        ("used", "Used"),
        ("abused", "Abused"),
    ]

    part_type = [
        ("engne", "Engine"),
        ("trans", "Transmission"),
        ("exhst", "Exhaust"),
        ("wheel", "Wheels"),
        ("suspn", "Suspension"),
        ("exter", "Exterior"),
        ("inter", "Interior"),
    ]

    status_choices = [
        ("active", "Active"),
        ("pending", "Pending"),
        ("sold", "Sold"),
        ("na", "Not Availavle")
    ]

    title = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    
    seller = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name="listings")
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="listings")  # the car that this part came from or is intended for
    
    
    part_type = models.CharField(max_length=15, choices=part_type)
    condition = models.CharField(max_length=10, choices=condition_choices)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    open_to_offers = models.BooleanField(default=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=2)
    # meetup_preference = models.TextField(
    #     help_text="Example: Warren Towers, Marsh Plaza, or somewhere between you and the buyer."
    # )
    image = models.ImageField(upload_to="listings/images/", blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=status_choices, default="active")

    def __str__(self):
        '''string representation of model'''
        return f'{self.title} ~ {self.seller} (${self.price})'
    
    def get_all_comments(self):
        '''returns all comment objects associated with listing'''

        from .models import Comment
        return Comment.objects.filter(listing=self).order_by('created')
    
    def get_likes(self):
        '''returns likes on a listing'''

        from .models import Like
        return Like.objects.filter(listing=self).order_by('created')



class Comment(models.Model):
    '''contains comment model data'''
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name="comments")
    
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.listing}"


class Like(models.Model):
    '''contains like model data'''
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="likes")
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name="likes" )
    
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("listing", "driver")

    def __str__(self):
        return f"{self.user} likes {self.listing}"


class SavedListing(models.Model):
    '''contains saved listing model data'''
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="saved_by")
    user = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name="saved_listings")
    
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("listing", "user")

    def __str__(self):
        return f"{self.user} saved {self.listing}"


class Offer(models.Model):
    '''contains offer model data'''
    status_choices = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("declined", "Declined"),
    ]

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="offers")
    buyer = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name="offers_made")

    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=status_choices, default="pending")

    def __str__(self):
        return f"Offer ${self.amount} by {self.buyer} on {self.listing}"




class DirectMessage(models.Model):
    '''contains dm model data'''

    participants = models.ManyToManyField("Driver", related_name="directmessage")
    listing = models.ForeignKey(
        "Listing", on_delete=models.CASCADE, related_name="directmessage",
        blank=True, null=True, 
        help_text="Optional: the listing this conversation is about"
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        names = ""
        for p in self.participants.all():
            if p == self.participants.all()[0]:
                names += p.first_name
                continue
            names += ", " + p.first_name

        return f"Chat between {names}"

class Message(models.Model):
    '''contains message model data'''

    conversation = models.ForeignKey(DirectMessage, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey("Driver", on_delete=models.CASCADE, related_name="sent_messages", default=None)
    receiver = models.ForeignKey("Driver", on_delete=models.CASCADE, related_name="received_messages", default=None)

    text = models.TextField(max_length=300)
    created = models.DateTimeField(auto_now_add=True)
        
    def __str__(self):
        return f"Message from {self.sender} in {self.conversation}"
    

class Rating(models.Model):
    '''contains rating model data'''

    rater = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name="ratings_given" )
    rating_receiver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name="ratings_received")
    rating = models.DecimalField(max_digits=1, decimal_places=0)
    comment = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating} stars from {self.rater} to {self.rating_receiver}"