# partout/views.py

from .models import *
from .forms import *

from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView, ListView, DetailView, View, CreateView, UpdateView, DeleteView


class HomeView(TemplateView):
    template_name = "partout/home.html"

    def get_current_driver(self):
        """
        maps the logged in user to the Driver.
        """
        user = self.request.user
        if not user.is_authenticated:
            return None

        try:
            return Driver.objects.get(email=user.email)
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
    model = Listing
    template_name = "partout/listing.html"
    context_object_name = ""


class MessagesView(ListView):
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
            return Driver.objects.get(email=user.email)
        except Driver.DoesNotExist:
            return None

    def get_queryset(self):
        driver = self.get_current_driver()
        if driver is None:
            return DirectMessage.objects.none()

        return (
            DirectMessage.objects.filter(participants=driver)
            .prefetch_related("participants", "listing")
            .order_by("-updated", "-created")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        driver = self.get_current_driver()
        context["current_driver"] = driver

        if driver:

            # unread counts per conversation
            unread_by_convo = (Message.objects.filter(conversation__participants=driver,is_read=False).exclude(sender=driver).values("conversation_id").annotate(count=Count("id")))

            context["unread_counts"] = {
                item["conversation_id"]: item["count"] for item in unread_by_convo
            }
            context["offers"] = (Offer.objects.all())


        return context

class ConversationView(DetailView):
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
            return Driver.objects.get(email=user.email)
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



class StartConvoView(View):
    def get_current_driver(self):
        """
        maps the logged in user to the Driver.
        """
        user = self.request.user
        if not user.is_authenticated:
            return None

        try:
            return Driver.objects.get(email=user.email)
        except Driver.DoesNotExist:
            return None
    
    def post(self, request, *args, **kwargs):
        current_driver = self.get_current_driver()
        if current_driver is None:
            return redirect("home")


        other_id = request.POST.get("other_driver_id")
        if not other_id:
            return redirect("messages")
        other_driver = Driver.objects.get(pk=other_id)
        
        existing_dm = DirectMessage.objects.filter(participants=current_driver).filter(participants=other_driver).first()

        if existing_dm is not None:
            dm = existing_dm

        dm = DirectMessage.objects.create()
        dm.participants.add(current_driver, other_driver)

        return redirect("conversation_detail", pk=dm.pk)
    
    def get(self, request, *args, **kwargs):
        return redirect("messages")


class ProfileView(DetailView):
    template_name = "partout/profile.html"
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
 
        