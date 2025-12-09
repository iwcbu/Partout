# partout/urls.py

from .views import *
from django.contrib.auth import views as auth_views # generic view for auth
from django.urls import path


urlpatterns = [
    # market
    path("", MarketView.as_view(), name="market"),
    path("/market", MarketView.as_view(), name="market"),
    path("/market/listing/<int:pk>", ListingView.as_view(), name="show_listing"),
    path("/market/listing/<int:pk>/update", UpdateListingView.as_view(), name="update_listing"),
    path("/market/listing/<int:pk>/delete", DeleteListingView.as_view(), name="delete_listing"),
    path("/market/seller/<int:seller_pk>/listing/new", CreateListingView.as_view(), name="create_listing"),
    
    path("/market/seller/<int:seller_pk>/message/new", MessageSellerView.as_view(), name="message_seller"),
    path("/market/listing/<int:listing_pk>/offer/new", CreateOfferView.as_view(), name="create_offer"),
    path("/market/listing/offer/<int:pk>/delete", DeleteOfferView.as_view(), name="delete_offer"),
    path("/market/listing/offer/<int:pk>/accept", AcceptOfferView.as_view(), name="accept_offer"),
    
    path("offers/<int:pk>/message_buyer/", MessageOfferBuyerView.as_view(), name="message_buyer_from_offer"),

    # home
    path("/home", HomeView.as_view(), name="home"),


    # profile
    path("/profile/<int:pk>", ProfileView.as_view(), name="show_profile"),
    path("/profile/new", CreateProfileView.as_view(), name="create_profile"),
    path('/profile/update', UpdateProfileView.as_view(), name='update_profile'),
    path("/profile/add_car", AddCarView.as_view(), name="add_car"),
    path("/profile/add_car", AddCarView.as_view(), name="add_car"),
    path("/profile/car/<int:pk>/update", UpdateCarView.as_view(), name="update_car"),
    path("/profile/car/<int:pk>/remove", DeleteCarView.as_view(), name="delete_car"),




    # private interactions
    path("/messages", MessagesView.as_view(), name="messages"),
    path("/messages/new", StartConvoView.as_view(), name="start_convo"),
    path("/profile/remove_convo/<int:pk>", DeleteConvoView.as_view(), name="delete_convo"),
    path("/messages/conversation/<int:pk>", ConversationView.as_view(), name="conversation"),

    # # social interactions
    # path('profile/<int:pk>/followers', ShowFollowersView.as_view(), name='show_followers'),
    # path('profile/<int:pk>/following', ShowFollowingView.as_view(), name='show_following'),
    path('profile/<int:pk>/follow', FollowView.as_view(), name='follow'),
    path('profile/<int:pk>/delete_follow', FollowView.as_view(), name='delete_follow'),
    path('listing/<int:pk>/like', LikeView.as_view(), name='like'),
    path('listing/<int:pk>/delete_like', LikeView.as_view(), name='delete_like'),
    path('listing/<int:pk>/save', SaveView.as_view(), name='save'),
    path('listing/<int:pk>/delete_save', SaveView.as_view(), name='delete_save'),

     # auth
    path('/login', auth_views.LoginView.as_view(template_name='partout/login.html'), name='login'),
    path('/logout', auth_views.LogoutView.as_view(next_page='logout_confirmation'), name='logout'),
    path('/logged_out', TemplateView.as_view(template_name='partout/logout.html'), name='logout_confirmation'),



]