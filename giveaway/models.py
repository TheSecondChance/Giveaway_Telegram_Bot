from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin)


PHONE_REGEX = RegexValidator(
        regex=r'^\+251(7|9)\d{8}$', 
        message="Phone number must be in the format '+2517XXXXXXXX' or '+2519XXXXXXXX'. Up to 12 digits allowed."
    )

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
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    user_name = models.CharField(max_length=100, unique=True, null=True)
    phone_number = models.CharField(validators=[PHONE_REGEX], max_length=13, unique=True)
    telegram_id = models.IntegerField(unique=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    is_taker = models.BooleanField(default=False)
    is_gifter = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserAccountManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name',]

    def __str__(self) -> str:
        return self.phone_number

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

