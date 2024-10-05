from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin)


class UserAccountManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **kwargs):
        if not phone_number:
            raise ValueError("User must have phone number")
        user = self.model(phone_number=phone_number, **kwargs)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(phone_number, password=password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    user_name = models.CharField(max_length=100, null=True)
    phone_number = models.CharField(max_length=15, unique=True)
    telegram_id = models.IntegerField(unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    language = models.CharField(max_length=100, default="english")

    is_taker = models.BooleanField(default=False)
    is_gifter = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserAccountManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name',]

    def __str__(self) -> str:
        return str(self.phone_number)

class GifterManager(BaseUserManager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(is_gifter=True)

class TakerManager(BaseUserManager):
    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(is_taker=True)

class Gifter(User):
    objects = GifterManager()

    class Meta:
        proxy = True
        verbose_name = "Gifter"

class Taker(User):
    objects = TakerManager()

    class Meta:
        proxy = True
        verbose_name = "Taker"

class Question(models.Model):
    gifter = models.ForeignKey('Gifter', on_delete=models.CASCADE)
    answer_format = models.TextField(blank=True, null=True)
    correct_answer = models.TextField(blank=True, null=True)
    question_code = models.IntegerField(unique=True)

    def __str__(self) -> str:
        return str(self.question_code)

class Answer(models.Model):
    taker = models.ForeignKey(Taker, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.TextField(blank=True, null=True)

    def __str__(self) -> str:
        return self.answer