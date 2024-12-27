from allauth.account.models import EmailAddress
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import BaseUserManager
import os
from uuid import uuid4
from allauth.account.models import EmailAddress

class CustomUserManager(BaseUserManager):
    """
    Create and return a regular user with the given email and password.
    """
    def create_user(self, email, password=None, **extra_fields):

        if not email:
            raise ValueError('Users must have an email address')
        email=self.normalize_email(email)
        user=self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get('is_superuser'):
            raise ValueError("Superuser must have is_superuser=True.")

        user = self.create_user(email, password, **extra_fields)
        EmailAddress.objects.create(user=user, email=user.email, verified=True, primary=True)
        Profile.objects.create(user=user)
        return user


class CustomUser(AbstractUser):
    username=None
    email = models.EmailField(unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects=CustomUserManager()

    def __str__(self):
        return self.email

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    image = models.ImageField(upload_to='avatars/', null=True, blank=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    newsletter = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.first_name or ""} {self.last_name or ""}'.strip()

    def save(self, *args, **kwargs):
        if self.image and not self.image.name.startswith("avatars/default"):
            extension=os.path.splitext(self.image.name)[1].lower()
            new_filename=f'{uuid4()}{extension}'
            self.image.name=new_filename
        super().save(*args,**kwargs)

class Address(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='addresses')
    street = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=50, blank=True)
    zipcode = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f'{self.street or ""}, {self.city or ""}, {self.zipcode or ""}, {self.country or ""}'.strip(", ")