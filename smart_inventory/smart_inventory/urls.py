# Smart_Inventory_Store/urls.py

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views  # Import Django's built-in auth views
from store import views as store_views  # Import views from your store app

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')),

]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
