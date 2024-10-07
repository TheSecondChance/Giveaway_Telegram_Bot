from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import hook, UserCreateViewSet, UserTelegramIdViewSet


router = DefaultRouter()
router.register(r'create-user', UserCreateViewSet)
# router.register(r'get-telegram-id', UserTelegramIdViewSet, basename='get-by-tg-id')

urlpatterns = [
    path("web-hook", hook, name="web-hook"),
    path("get-telegram-id/", UserTelegramIdViewSet.as_view(), name="get-by-tg-id"),
]

urlpatterns += router.urls