import io
import json, telebot
# from bot.main import bot
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from django.db import transaction
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, UpdateAPIView, DestroyAPIView

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

class UserTelegramIdViewSet(RetrieveAPIView, UpdateAPIView, DestroyAPIView):
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
    
    def delete(self, request, *args, **kwargs):
        telegram_id = request.query_params.get('telegram_id')
        if telegram_id:
            user = User.objects.filter(telegram_id=telegram_id).first()
            if user:
                user.delete()
                return Response({"detail": "User deleted successfully"},
                                status=status.HTTP_204_NO_CONTENT)
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
        question_code = request.data.get('question_code')
        answer_text = request.data.get('answer_text')

        if not telegram_id:
            return Response({"status": 400, "detail": "telegram_id query param is required"},
                            status=status.HTTP_400_BAD_REQUEST)
        if not question_code:
            return Response({"status": 400, "detail": "question_code is required in the body"},
                            status=status.HTTP_400_BAD_REQUEST)
        if not answer_text:
            return Response({"status": 400, "detail": "answer_text is required in the body"},
                            status=status.HTTP_400_BAD_REQUEST)
        taker = Taker.objects.filter(telegram_id=telegram_id).first()
        if not taker:
            return Response({"status": 404, "detail": "No taker found with the provided telegram_id"},
                            status=status.HTTP_404_NOT_FOUND)
        question = Question.objects.filter(pk=question_code).first()
        if not question:
            return Response({"status": 404, "detail": "No question found with the provided question_code"},
                            status=status.HTTP_404_NOT_FOUND)
        existing_answer = Answer.objects.filter(taker=taker, question_code=question_code).first()
        if existing_answer:
            return Response({"status": 400, "detail": "Taker has already answered this question."},
                            status=status.HTTP_400_BAD_REQUEST)
        is_correct = False
        if question.correct_answer and answer_text:
            normalized_answer_text = answer_text.replace(" ", "").strip().lower()
            normalized_correct_answer = question.correct_answer.replace(" ", "").strip().lower()
            is_correct = normalized_answer_text == normalized_correct_answer
        data = request.data.copy()
        data['taker'] = taker.pk
        data['is_correct'] = is_correct
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"status": 201, "data": serializer.data, "detail": "Answer successfully created"},
                        status=status.HTTP_201_CREATED)

class ResultGiverViewSet(RetrieveAPIView):
    serializer_class = AnswerSerializer

    def get(self, request, *args, **kwargs):
        giver_telegram_id = request.query_params.get('telegram_id')
        question_code = request.query_params.get('question_code')

        if not giver_telegram_id:
            return Response({"status": 400, "detail": "giver_telegram_id query param is required"},
                            status=status.HTTP_400_BAD_REQUEST)
        if not question_code:
            return Response({"status": 400, "detail": "question_code query param is required"},
                            status=status.HTTP_400_BAD_REQUEST)
        giver = Gifter.objects.filter(telegram_id=giver_telegram_id).first()
        if not giver:
            return Response({"status": 404, "detail": "No giver found with the provided giver_telegram_id"},
                            status=status.HTTP_404_NOT_FOUND)
        question = Question.objects.filter(pk=question_code, gifter=giver).first()
        if not question:
            return Response({"status": 404, "detail": "No question found for the provided question_code and giver"},
                            status=status.HTTP_404_NOT_FOUND)
        correct_answers = Answer.objects.filter(question_code=question, is_correct=True)
        correct_answer_count = correct_answers.count()
        if correct_answer_count < 200:
            answer_data = []
            for answer in correct_answers:
                taker_username = answer.taker.user_name if answer.taker.user_name else "No username"
                taker_name = answer.taker.first_name if answer.taker.first_name else "No name"
                taker_id = answer.taker.telegram_id
                answer_data.append({
                    'taker_username': taker_username,
                    'taker_name': taker_name,
                    'answer': answer.answer_text,
                    'taker_id': taker_id
                })
            return Response({"status": 200, "correct_answers": answer_data,
                             "detail": "Correct answers found but less than 20"},
                            status=status.HTTP_200_OK)
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.drawString(100, 750, f"Giver: {giver_telegram_id}")
        p.drawString(100, 725, f"Question Code: {question_code}")
        p.drawString(100, 700, f"Total Correct Answers: {correct_answer_count}")
        y_position = 675
        for idx, answer in enumerate(correct_answers, start=1):
            taker_username = answer.taker.user_name if answer.taker.user_name else "No username"
            taker_name = answer.taker.first_name if answer.taker.first_name else "No name"
            
            p.drawString(100, y_position, f"Taker {idx} - Username: {taker_username}, Name: {taker_name}")
            y_position -= 25
            p.drawString(100, y_position, f"Correct Answer {idx}: {answer.answer_text}")
            y_position -= 25 
        p.showPage()
        p.save()
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="correct_answers_{question_code}.pdf"'
        return response

class AfterAnswerViewSet(RetrieveAPIView, UpdateAPIView):
    serializer_class = QuestionSerializer

    def get(self, request, *args, **kwargs):
        giver_telegram_id = request.query_params.get('telegram_id')
        if not giver_telegram_id:
            return Response({"status": 400, "detail": "giver_telegram_id query param is required"},
                            status=status.HTTP_400_BAD_REQUEST)
        giver = Gifter.objects.filter(telegram_id=giver_telegram_id).first()
        if not giver:
            return Response({"status": 404, "detail": "No giver found with the provided giver_telegram_id"},
                            status=status.HTTP_404_NOT_FOUND)
        empty_correct_answers = Question.objects.filter(correct_answer=None, gifter=giver)
        if not empty_correct_answers.exists():
            return Response({"status": 404, "detail": "No questions with empty correct_answer found"},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(empty_correct_answers, many=True)
        return Response({"status": 200, "detail": "Questions fetched successfully", "data": serializer.data})

    def put(self, request, *args, **kwargs):
        giver_telegram_id = request.query_params.get('telegram_id')
        question_code = request.query_params.get('question_code')
        correct_answer = request.data.get('correct_answer')

        if not giver_telegram_id:
            return Response({"status": 400, "detail": "giver_telegram_id query param is required"},
                            status=status.HTTP_400_BAD_REQUEST)
        if not question_code:
            return Response({"status": 400, "detail": "question_code query param is required"},
                            status=status.HTTP_400_BAD_REQUEST)
        if not correct_answer:
            return Response({"status": 400, "detail": "correct_answer is required"},
                            status=status.HTTP_400_BAD_REQUEST)
        giver = Gifter.objects.filter(telegram_id=giver_telegram_id).first()
        if not giver:
            return Response({"status": 404, "detail": "No giver found with the provided giver_telegram_id"},
                            status=status.HTTP_404_NOT_FOUND)
        question = Question.objects.filter(pk=question_code, gifter=giver).first()
        if not question:
            return Response({"status": 404, "detail": "No question found for the provided question_code and giver"},
                            status=status.HTTP_404_NOT_FOUND)
        question.correct_answer = correct_answer
        question.save()
        answers = Answer.objects.filter(question_code=question)
        updated_answers = []
        for answer in answers:
            if answer.answer_text:
                normalized_answer_text = answer.answer_text.replace(" ", "").strip().lower()
                normalized_correct_answer = correct_answer.replace(" ", "").strip().lower()
                if normalized_answer_text == normalized_correct_answer:
                    answer.is_correct = True
                else:
                    answer.is_correct = False
            else:
                answer.is_correct = False
            updated_answers.append(answer)
        with transaction.atomic():
            Answer.objects.bulk_update(updated_answers, ['is_correct'])
        return Response({"status": 200, "detail": "Answers updated successfully"})



# TELEGRAM_BOT_WEBHOOK_URL = "https://bcd68b0417f6aeef18b0fe38d16faa40.serveo.net/account/web-hook"

# webhook_url = f'{TELEGRAM_BOT_WEBHOOK_URL}'
# bot.remove_webhook()
# bot.set_webhook(url=webhook_url)
