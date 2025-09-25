"""
URL configuration for cs412 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path("hw/", include("hw.urls")), # hello world test
    path("quotes/", include("quotes.urls")), # ps1
    path("formdata/", include("formdata.urls")), # formdata test
    path('restaurant/', include('restaurant.urls')), # ps2
    path('blog/', include('blog.urls')), # ps2

    

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
