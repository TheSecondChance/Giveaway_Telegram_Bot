import json, telebot
# from bot.main import bot
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, UpdateAPIView

from .serializers import (UserSerializer, UserTelegramIdSerializer,
                          QuestionSerializer, AnswerSerializer)
from giveaway.models import User, Question ,Gifter, Taker, Answer


@csrf_exempt
def hook(request):

    body = request.body.decode('utf-8')

    if not body:
        return JsonResponse({'error': 'Request body is empty...'})

    body_data = json.loads(body)
    update = telebot.types.Update.de_json(body_data)
    bot.process_new_updates([update])
    return JsonResponse({"status": "200"}, safe=False)

class UserCreateViewSet(CreateModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserTelegramIdViewSet(RetrieveAPIView, UpdateAPIView):
    serializer_class = UserTelegramIdSerializer

    def get(self, request, *args, **kwargs):
        telegram_id = request.query_params.get('telegram_id')

        if telegram_id:
            user = User.objects.filter(telegram_id=telegram_id).first()

            if user:
                serializer = self.get_serializer(user)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "No user found with the provided telegram_id"},
                                status=status.HTTP_404_NOT_FOUND)

        return Response({"detail": "telegram_id query param is required"},
                        status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, *args, **kwargs):
        telegram_id = request.query_params.get('telegram_id')
        if telegram_id:
            user = User.objects.filter(telegram_id=telegram_id).first()
            if user:
                serializer = self.get_serializer(instance=user, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
            else:
                return Response({"detail": "No user found with the provided telegram_id"},
                                status=status.HTTP_404_NOT_FOUND)

        return Response({"detail": "telegram_id query param is required"},
                        status=status.HTTP_400_BAD_REQUEST)

class QuestionViewSet(CreateModelMixin, GenericViewSet):
    serializer_class = QuestionSerializer

    def create(self, request, *args, **kwargs):
        telegram_id = request.query_params.get('telegram_id')

        if not telegram_id:
            return Response({"detail": "telegram_id query param is required"},
                            status=status.HTTP_400_BAD_REQUEST)

        gifter = Gifter.objects.filter(telegram_id=telegram_id).first()
        if not gifter:
            return Response({"detail": "No gifter found with the provided telegram_id"},
                            status=status.HTTP_404_NOT_FOUND)
        data = request.data.copy()
        data['gifter'] = gifter.pk
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        question = serializer.save()
        question.question_code = question.pk
        question.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class AnswerViewSet(CreateModelMixin, GenericViewSet):
    serializer_class = AnswerSerializer

    def create(self, request, *args, **kwargs):
        telegram_id = request.query_params.get('telegram_id')
        question_code = request.query_params.get('question_code')
        if not telegram_id:
            return Response({"detail": "telegram_id query param is required"},
                            status=status.HTTP_400_BAD_REQUEST)
        if not question_code:
            return Response({"detail": "question_code query param is required"},
                            status=status.HTTP_400_BAD_REQUEST)
        taker = Taker.objects.filter(telegram_id=telegram_id).first()
        if not taker:
            return Response({"detail": "No taker found with the provided telegram_id"},
                            status=status.HTTP_404_NOT_FOUND)
        
        question = Question.objects.filter(pk=question_code).first()
        if not question:
            return Response({"detail": "No question found with the provided question_code"},
                            status=status.HTTP_404_NOT_FOUND)
        existing_answer = Answer.objects.filter(taker=taker, question_code=question).first()
        if existing_answer:
            return Response({"detail": "Taker has already applied to this question."},
                            status=status.HTTP_400_BAD_REQUEST)
        data = request.data.copy()
        data['taker'] = taker.pk
        data['question_code'] = question.pk
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)



# TELEGRAM_BOT_WEBHOOK_URL = "https://bcd68b0417f6aeef18b0fe38d16faa40.serveo.net/account/web-hook"

# webhook_url = f'{TELEGRAM_BOT_WEBHOOK_URL}'
# bot.remove_webhook()
# bot.set_webhook(url=webhook_url)
