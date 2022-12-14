"""khaikang URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path
from django.urls import include
from . import views
from . import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/config', views.user_config),
    path('account/', include('django.contrib.auth.urls')),
    path('home/',  views.home, name='home'),
    path('signup/',  views.signup),
    path('api/post', views.api_post),
    path('api/get_recent_posts_counter', views.api_get_recent_posts_counter),
    path('api/get_latest_posts', views.api_get_latest_posts),
    path('api/get_previous_posts', views.api_get_previous_posts),
    path('user/<username>', views.user_timeline),
    path('api/follow_request/<request_value>/<dest_username>', views.api_follow_request),
    path('api/repost_request/<post_id>', views.api_repost_request),
    path('api/fav_request/<post_id>', views.api_fav_request),

]

if settings.DEBUG:  
        urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)