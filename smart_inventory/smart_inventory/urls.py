from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views  # Import Django's built-in auth views
from store import views as store_views  # Import views from your store app

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')),

    # --- Authentication URLs ---
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('register/', store_views.register_user, name='register'),

    # --- User Profile URL ---
    path('profile/', store_views.user_profile, name='profile'),  # User profile page
]

# Optional: Serve media files during development (add only in development)
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
