# partout/urls.py

from django.urls import path
from .views import *


urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("/home", HomeView.as_view(), name="home"),

    path("/market", MarketView.as_view(), name="market"),
    path("/market/listing/<int:pk>", ListingView.as_view(), name="listing"),

    path("/profile/<int:pk>", ProfileView.as_view(), name="profile"),

    path("/messages", MessagesView.as_view(), name="messages"),
    path("/messages/conversation/<int:pk>", ConversationView.as_view(), name="conversation"),

]