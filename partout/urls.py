# partout/urls.py

from django.urls import path
from .views import *


urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("/market", MarketView.as_view(), name="market"),
    path("/messages", MessagesView.as_view(), name="messages"),
    path("/profile/<int:pk>", ProfileView.as_view(), name="profile"),
]