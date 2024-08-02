from django.contrib import admin
from django.apps import apps

# Get all models in the app
app_models = apps.get_app_config("diab_retina_app").get_models()

# Register all models with the admin site
for model in app_models:
    admin.site.register(model)
