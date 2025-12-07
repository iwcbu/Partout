# partout/urls.py

from django.urls import path
from .views import *


urlpatterns = [

    # home
    path("", HomeView.as_view(), name="home"),
    path("/home", HomeView.as_view(), name="home"),

    # market
    path("/market", MarketView.as_view(), name="market"),
    path("/market/listing/<int:pk>", ListingView.as_view(), name="listing"),

    # profile
    path("/profile/<int:pk>", ProfileView.as_view(), name="profile"),
    path("/profile/new", CreateProfileView.as_view(), name="create_profile"),


    # private interactions
    path("/messages", MessagesView.as_view(), name="messages"),
    path("/messages/new", StartConvoView.as_view(), name="start_convo"),
    path("/messages/conversation/<int:pk>", ConversationView.as_view(), name="conversation"),

    # # social interactions
    # path('profile/<int:pk>/followers', ShowFollowersView.as_view(), name='show_followers'),
    # path('profile/<int:pk>/following', ShowFollowingView.as_view(), name='show_following'),
    # path('profile/<int:pk>/follow', FollowView.as_view(), name='follow'),
    # path('profile/<int:pk>/delete_follow', FollowView.as_view(), name='delete_follow'),
    # path('post/<int:pk>/like', LikeView.as_view(), name='like'),
    # path('post/<int:pk>/delete_like', LikeView.as_view(), name='delete_like'),


]