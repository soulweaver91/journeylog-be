"""journeylog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

from .routers import root_router, journey_photos_router
from .views import photo_file_view

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^nested_admin/', include('nested_admin.urls')),
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^image/(?P<visibility>(private|public))/(?P<kind>(photo|thumb))/(?P<journey_id>\d+)/(?P<file>.+)',
        photo_file_view),
    url(r'^', include(root_router.urls)),
    url(r'^', include(journey_photos_router.urls)),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
      path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
