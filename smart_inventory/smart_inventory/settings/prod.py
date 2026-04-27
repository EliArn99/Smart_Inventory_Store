from .base import *

DEBUG = False

ALLOWED_HOSTS = get_list_env("DJANGO_ALLOWED_HOSTS")

if not ALLOWED_HOSTS:
    raise RuntimeError("DJANGO_ALLOWED_HOSTS is not set")

CSRF_TRUSTED_ORIGINS = get_list_env("DJANGO_CSRF_TRUSTED_ORIGINS", "")

if not DATABASES["default"]["PASSWORD"]:
    raise RuntimeError("POSTGRES_PASSWORD is not set")

SECURE_SSL_REDIRECT = get_bool_env("DJANGO_SECURE_SSL_REDIRECT", True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

SECURE_HSTS_SECONDS = int(get_env("DJANGO_SECURE_HSTS_SECONDS", 31536000))
SECURE_HSTS_INCLUDE_SUBDOMAINS = get_bool_env("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", True)
SECURE_HSTS_PRELOAD = get_bool_env("DJANGO_SECURE_HSTS_PRELOAD", True)

EMAIL_BACKEND = get_env(
    "EMAIL_BACKEND",
    "django.core.mail.backends.smtp.EmailBackend",
)
