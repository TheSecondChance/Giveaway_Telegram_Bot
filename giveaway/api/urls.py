from django.urls import path
from .views import hook


urlpatterns = [
    path("web-hook", hook, name="web-hook"),
]