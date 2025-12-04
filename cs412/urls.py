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
    path("hw/", include("hw.urls")), # module 1 example
    path("quotes/", include("quotes.urls")), # ps1
    path("formdata/", include("formdata.urls")), # module 2 example
    path('restaurant/', include('restaurant.urls')), # ps2
    path('blog/', include('blog.urls')), # modules 3-7 example
    path('mini_insta/', include('mini_insta.urls')), # ps3-ps7
    path('marathon_analysis', include('marathon_analysis.urls')), # module 8 example
    path('voter_analytics/', include('voter_analytics.urls')), # ps8
    path('dadjokes', include('dadjokes.urls')), # ps10
    path('partout', include('partout.urls')), # ps10

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

