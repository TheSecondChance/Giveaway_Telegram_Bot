from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (hook, UserCreateViewSet, UserTelegramIdViewSet,
                    QuestionViewSet, AnswerViewSet, ResultGiverViewSet, AfterAnswerViewSet)


router = DefaultRouter()
router.register(r'create-user', UserCreateViewSet)
router.register(r'create-question', QuestionViewSet, basename="create-question")
router.register(r'answer', AnswerViewSet, basename="answer-for-taker")
# router.register(r'get-telegram-id', UserTelegramIdViewSet, basename='get-by-tg-id')

urlpatterns = [
    path("web-hook", hook, name="web-hook"),
    path("get-telegram-id/", UserTelegramIdViewSet.as_view(), name="get-by-tg-id"),
    path("result/", ResultGiverViewSet.as_view(), name="result-for-giver"),
    path("after/", AfterAnswerViewSet.as_view(), name="after-answer"),
]

urlpatterns += router.urls