from rest_framework.serializers import ModelSerializer, BooleanField
from rest_framework import serializers
from giveaway.models import User, Question, Answer


class UserSerializer(ModelSerializer):
    phone_number = serializers.CharField(required=False)
    telegram_id = serializers.IntegerField(required=False)
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'user_name', 'phone_number',
                  'telegram_id', 'language', 'is_taker', 'is_gifter', 'is_active']

class UserTelegramIdSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'user_name', 'phone_number',
                  'telegram_id', 'language', 'is_taker', 'is_gifter', 'is_active']

class QuestionSerializer(ModelSerializer):
    class Meta:
        model = Question
        fields = ['gifter', 'answer_format', 'correct_answer', 'question_code']
        extra_kwargs = {
            'question_code': {'required': False} 
        }

class AnswerSerializer(ModelSerializer):
    class Meta:
        model = Answer
        fields = ['taker', 'question_code', 'answer']