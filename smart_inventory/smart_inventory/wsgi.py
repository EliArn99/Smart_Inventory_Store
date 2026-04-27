import os
from django.core.wsgi import get_wsgi_application

env = os.getenv("DJANGO_ENV", "prod").lower()

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    f"Smart_Inventory_Store.settings.{env}"
)

application = get_wsgi_application()
