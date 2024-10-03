from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin)


PHONE_REGEX = RegexValidator(
        regex=r'^\+251(7|9)\d{8}$', 
        message="Phone number must be in the format '+2517XXXXXXXX' or '+2519XXXXXXXX'. Up to 12 digits allowed."
    )

class UserAccountManager(BaseUserManager):
    def create_user(self, phone_number, **kwargs):
        if not phone_number:
            raise ValueError("User must have phone number")
        user = self.model(phone_number=phone_number, **kwargs)
        user.save(using=self._db)

        return user
    
    def create_superuser(self, phone_number, **kwargs):
        user = self.create_user(phone_number, **kwargs)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user

class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    user_name = models.CharField(max_length=100, unique=True, null=True)
    phone_number = models.CharField(validators=[PHONE_REGEX], max_length=13, unique=True)
    telegram_id = models.IntegerField(unique=True)

    is_taker = models.BooleanField(default=False)
    is_gifter = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

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

