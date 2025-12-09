# partout/views.py

from .models import *
from .forms import *

from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.urls import reverse
from django.shortcuts import redirect
from django.views.generic import TemplateView, ListView, DetailView, View, CreateView, UpdateView, DeleteView


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "partout/home.html"

    def get_current_driver(self):
        """
        maps the logged in user to the Driver.
        """
        user = self.request.user
        if not user.is_authenticated:
            return None

        try:
            return Driver.objects.get(user=user)
        except Driver.DoesNotExist:
            return None


    def get_context_data(self, **kwargs):
        '''        
        recent_listings - Newest active listings
        
        popular_listings - "Popular" listings by like count

        '''

        context = super().get_context_data(**kwargs)

        user = self.request.user
        driver = self.get_current_driver()
        if user.is_authenticated and driver:
            context["messages"] = Message.objects.filter(receiver=driver).order_by("-created")[:3]

        context["recent_listings"] = (
            Listing.objects.filter(status="active")
            .select_related("seller", "car")
            .order_by("-created")[:3]
        )

        context["popular_listings"] = (Listing.objects.filter(status="active").annotate(num_likes=Count("likes")).select_related("seller", "car").order_by("-num_likes", "-created")[:8])

        return context


class MarketView(ListView):
    model = Listing
    template_name = "partout/market.html"
    context_object_name = "listings"
    paginate_by = 12

    def get_queryset(self):
        qs = (
            Listing.objects.filter(status="active")
            .select_related("seller", "car")
            .order_by("-created")
        )

        part_type = self.request.GET.get("part_type")
        drivetrain = self.request.GET.get("drivetrain")
        ownership_type = self.request.GET.get("ownership_type")
        search = self.request.GET.get("q")

        if part_type:
            qs = qs.filter(part_type=part_type)

        if drivetrain:
            qs = qs.filter(car__drivetrain=drivetrain)

        if ownership_type:
            qs = qs.filter(car__ownership_type=ownership_type)

        if search:
            qs = qs.filter(
                Q(title__icontains=search)
                | Q(car__make__icontains=search)
                | Q(car__model__icontains=search)
                | Q(car__nickname__icontains=search)
            )

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Choices for filters (for dropdowns in the template)
        context["part_type_choices"] = Listing._meta.get_field("part_type").choices
        context["condition_choices"] = Listing._meta.get_field("condition").choices
        context["drivetrain_choices"] = Car.drivetrain_choices
        context["ownership_type_choices"] = Car.ownership_type_choices

        # Keep current filter values (so form can keep them selected)
        context["current_filters"] = {
            "part_type": self.request.GET.get("part_type", ""),
            "drivetrain": self.request.GET.get("drivetrain", ""),
            "ownership_type": self.request.GET.get("ownership_type", ""),
            "q": self.request.GET.get("q", ""),
        }

        return context
    

class ListingView(DetailView):
    '''Displays selected Listing'''

    model = Listing
    template_name = 'partout/show_listing.html'
    context_object_name = 'listing'


    def get_context_data(self, **kwargs):
        '''gets context data related to listings'''
        context = super().get_context_data(**kwargs)
        likes = self.object.get_likes()
        comments = self.object.get_all_comments()

        context['photo'] = self.object.image
        context['comments'] = comments
        context['likes'] = likes

        if self.request.user.is_authenticated:
            driver = self.request.user.driver
            context['liked_by_user'] = likes.filter(driver=driver).exists

        
        return context
    

class CreateListingView(LoginRequiredMixin, CreateView):
    '''View to create listing for a given driver'''

    model = Listing
    form_class = CreateListingForm
    template_name = 'partout/create_listing_form.html'


    def form_valid(self, form):
        '''link the seller to the current user'''
        driver = self.request.user.driver
        form.instance.seller = driver

        return super().form_valid(form)
    
    def get_form_kwargs(self):
        """pass the current driver into the form for filtering car objects"""
        kwargs = super().get_form_kwargs()
        kwargs["driver"] = self.request.user.driver
        
        return kwargs

    def get_success_url(self):
        '''redirects user to their profile after creating a new car'''


        return reverse("show_listing", kwargs={ "pk": self.object.pk } )
    


class DeleteListingView(LoginRequiredMixin, DeleteView):
    '''deletes car object from django db'''

    model = Listing
    template_name = "partout/delete_listing_form.html"

    def get_context_data(self, **kwargs):
            '''returns context data required for deleting listing'''

            context = super().get_context_data()
            pk = self.kwargs['pk']
            listing = Listing.objects.get(pk=pk)
            context['listing'] = listing

            return context 
    
    def get_login_url(self):
        '''return the url for the apps login'''
        return reverse('login')

    def get_success_url(self):
        '''return the url to redirect to after a successful delete'''

        return reverse('market')
    

class MessageSellerView(LoginRequiredMixin, View):
    '''creates a DirectMessage conversation between seller and current driver
    then redirects to the conversation view'''

    def get_current_driver(self):
        '''gets the current user's driver profile'''

        user = self.request.user
        if not user.is_authenticated:
            return None
        
        try:
            return Driver.objects.get(user=user)
        except Driver.DoesNotExist:
            return None
        
    def get(self, request, seller_pk, *args, **kwargs):
        '''creates a a convo between seller and driver'''

        driver = self.get_current_driver()
        if driver is None:
            return redirect("create_profile")

        seller = Driver.objects.get(pk=seller_pk)
        
        convo = DirectMessage.objects.create()
        convo.participants.set([driver, seller])

        return redirect("conversation", pk=convo.pk)
        
    


class MessagesView(LoginRequiredMixin, ListView):
    model = DirectMessage
    template_name = "partout/messages.html"
    context_object_name = "conversations"

    def get_current_driver(self):
        """
        maps the logged in user to the Driver.
        """
        user = self.request.user
        if not user.is_authenticated:
            return None

        try:
            return Driver.objects.get(user=user)
        except Driver.DoesNotExist:
            return None

    def get_queryset(self):
        driver = self.get_current_driver()
        if driver is None:
            return DirectMessage.objects.none()

        return (
            DirectMessage.objects.filter(participants=driver)
            .prefetch_related("participants")
            .order_by("-updated", "-created")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        driver = self.get_current_driver()
        context["current_driver"] = driver

        if driver:
            context["offers"] = Offer.objects.filter(listing__seller=driver)
            context["following"] = Follow.get_following(driver)


        return context

class ConversationView(LoginRequiredMixin, DetailView):
    template_name = "partout/conversation.html"
    model = DirectMessage

    def get_current_driver(self):
        """
        maps the logged in user to the Driver.
        """
        user = self.request.user
        if not user.is_authenticated:
            return None

        try:
            return Driver.objects.get(user=user)
        except Driver.DoesNotExist:
            return None

    def get_context_data(self, **kwargs):

        context =  super().get_context_data(**kwargs)

        driver = self.get_current_driver()
        if driver:
            context["driver"] = driver

            pk = self.kwargs["pk"]
            c = DirectMessage.objects.get(pk=pk)

            peeps = c.participants.all()
            context["participants"] = peeps

            if driver in peeps:
                context["is_allowed"] = True
            else:
                context["is_allowed"] = False

            convo = Message.objects.filter(conversation=c).order_by("created")

            context["conversation"] = convo

        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        convo = self.object
        driver = self.get_current_driver()

        peeps = convo.participants.all()
        receiver = driver
        for p in peeps:
            if p != driver:
                receiver = p

        if driver is None:
            return redirect("login")
        
        text = request.POST.get("text","").strip()
        if text:
            Message.objects.create(conversation=convo, sender=driver,text=text,receiver=receiver)

        return redirect("conversation", pk=convo.pk)


class StartConvoView(LoginRequiredMixin, View):
    
    template_name = 'partout/start_convo_form.html'

    def get_current_driver(self):
        """
        maps the logged in user to the Driver.
        """
        user = self.request.user
        if not user.is_authenticated:
            return None

        try:
            return Driver.objects.get(user=user)
        except Driver.DoesNotExist:
            return None

    def form_valid(self, form):
            '''link the owner to the current user'''

            driver = self.request.user.driver
            form.instance.owner = driver

            return super().form_valid(form)
    

    def get_success_url(self):
        '''redirects user to their profile after creating a new car'''

        driver = self.request.user.driver

        return reverse("show_profile", kwargs={ "pk": driver.pk } )
    


class DeleteConvoView(DeleteView):
    '''deletes car object from django db'''

    model = DirectMessage
    template_name = "partout/delete_convo_form.html"

    def get_context_data(self, **kwargs):
        '''returns context data required for deleting post'''

        context = super().get_context_data()
        pk = self.kwargs['pk']
        convo = DirectMessage.objects.get(pk=pk)
        context['convo'] = convo

        return context 
    
    def get_login_url(self):
        '''return the url for the apps login'''

        return reverse('login')

    def get_success_url(self):
        '''return the url to redirect to after a successful delete'''

        return reverse('messages')
    



class ProfileView(LoginRequiredMixin, DetailView):
    template_name = "partout/show_profile.html"
    model = Driver
    context_object_name = "driver"

    def get_context_data(self, **kwargs):
        '''  
        cars - cars in this driver's "garage"

        listings - listings created by this driver

        saved_listings - listings they’ve saved

        stats - quick stats for flexing on their profile page

        '''

        context = super().get_context_data(**kwargs)
        driver = self.object

        context["cars"] = (
            driver.cars.all()
            .select_related()
            .order_by("-year", "make", "model")
        )

        context["listings"] = (Listing.objects.filter(seller=driver).order_by("-created"))

        context["saved_listings"] = (
            SavedListing.objects.filter(user=driver)
            .select_related("listing__car", "listing__seller")
            .order_by("-created")
        )

        ratings = Rating.objects.filter(rating_receiver=driver)
        
        avgRating = 0
        numRatings = ratings.count()

        if numRatings > 0:
            total = 0
            for r in ratings:
                total += r.rating
            
            avgRating = total / numRatings
        
        avgRating = round(avgRating, 1)

        followers = Follow.get_num_followers(driver)
        following = Follow.get_num_following(driver)



        context["stats"] = {
            "total_listings": driver.listings.count(),
            "active_listings": driver.listings.filter(status="active").count(),
            "total_cars": driver.cars.count(),
            "saved_count": driver.saved_listings.count(),
            "rating": avgRating,
            "followers": followers,
            "following": following,
        }

        userProfile = self.request.user.driver
        followers_qs = Follow.get_follower_profiles(driver)
        context["followed_by_user"] = userProfile in followers_qs


        return context
    

class CreateProfileView(CreateView):
    '''defines a view class to create a driver profile'''

    model = Driver
    fields = ['first_name', 'last_name', 'username', 'email', "city", "state", "zip_code", "profile_image", "bio"]
    template_name = 'partout/create_profile_form.html'


    def get_context_data(self, **kwargs):
        '''gets context data for a view'''
        context = super().get_context_data(**kwargs)
        if self.request.method == 'POST':
            userForm = UserCreationForm(self.request.POST)
            profileForm = CreateProfileForm(self.request.POST, self.request.FILES)
        else:
            userForm = UserCreationForm()
            profileForm = CreateProfileForm()


        context['userForm'] = userForm
        context['profileForm'] = profileForm
        return context
    
    def form_valid(self, form):
        '''Takes a successful form and submits the data to the database'''

        userForm = UserCreationForm(self.request.POST)
        if userForm.is_valid():
            user = userForm.save()
            login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
            form.instance.user = user
            return super().form_valid(form)
        else:
            return self.form_invalid(form)
        
    def get_success_url(self):
        user = self.request.user
        driver = Driver.objects.get(user=user)

        return reverse('profile', kwargs={'pk': driver.pk})
 
class UpdateProfileView(LoginRequiredMixin, UpdateView):
    """defines a view class to update a given profile"""

    model = Driver
    form_class = UpdateProfileForm
    template_name = 'partout/update_profile_form.html'

    def get_object(self, queryset = None):
        '''returns driver profile'''
        user = self.request.user
        profile = Driver.objects.get(user=user)
        return profile
    
    def get_success_url(self):
        '''on successful submission, show user their updated driver profile'''

        profile = self.get_object()

        return reverse('show_profile', kwargs={'pk': profile.pk})
    

    def get_login_url(self):
        '''return the url for the apps login'''
        return reverse('login')


class FollowView(TemplateView):

    def get(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return redirect('login')
        

        try:
            pk = kwargs['pk']
            driver = Driver.objects.get(pk=pk)
        except Driver.DoesNotExist: # missing posts or network error
            from django.http import Http404
            raise Http404("Profile not found")
        
        userProfile = user.driver
        action = request.GET.get("action", "follow")
        if action == "follow":
            Follow.objects.create(driver=driver, driver_that_followed=userProfile)
        else:
            Follow.objects.filter(driver=driver, driver_that_followed=userProfile).delete()
        
        return redirect( 'show_profile', pk=driver.pk )
        



class AddCarView(CreateView):
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

    template_name = 'partout/add_car_form.html'


    def form_valid(self, form):
            '''link the owner to the current user'''

            driver = self.request.user.driver
            form.instance.owner = driver

            return super().form_valid(form)
    

    def get_success_url(self):
        '''redirects user to their profile after creating a new car'''

        driver = self.request.user.driver

        return reverse("show_profile", kwargs={ "pk": driver.pk } )
    



class DeleteCarView(DeleteView):
    '''deletes car object from django db'''

    model = Car
    template_name = "partout/delete_car_form.html"

    def get_context_data(self, **kwargs):
        '''returns context data required for deleting post'''

        context = super().get_context_data()
        pk = self.kwargs['pk']
        car = Car.objects.get(pk=pk)
        context['car'] = car
        context['driver'] = car.owner

        return context 
    
    def get_login_url(self):
        '''return the url for the apps login'''
        return reverse('login')

    

    def get_success_url(self):
        '''return the url to redirect to after a successful delete'''

        # find pk of comment
        pk = self.kwargs['pk']

        #find comment
        car = Car.objects.get(pk=pk)

        # find pk of article where the comment was associated with
        driver = car.owner

        #return url to redirect to
        return reverse('show_profile', kwargs={'pk': driver.pk})
    