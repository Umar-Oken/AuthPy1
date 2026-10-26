from django.contrib.auth.models import AbstractUser
from django.db.models.fields import EmailField

from apps.managers import UserManager


# Create your models here.
class User(AbstractUser):
    username = None
    email = EmailField(unique=True)
    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
