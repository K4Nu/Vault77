from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

class AppUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is needed")
        if not password:
            raise ValueError("Password is needed")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
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

        return self.create_user(email, password, **extra_fields)

class AppUser(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=100, unique=True)
    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    #wishlist = models.ManyToManyField('Product', related_name='wishlisted_by', blank=True)
    #possibly change to is_active by default=False
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = AppUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['firstname', 'lastname']

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

class AddressModel(models.Model):
    user=models.ForeignKey("AppUser", on_delete=models.CASCADE,related_name="address")
    address1=models.CharField(max_length=255)
    address2=models.CharField(max_length=255,blank=True,null=True)
    city=models.CharField(max_length=100)
    country=models.CharField(max_length=100)
    postal_code=models.CharField(max_length=20)

    def __str__(self):
        return f'{self.address1}, {self.city}, {self.country}'

    class Meta:
        verbose_name="Address"
        verbose_name_plural = 'Addresses'
        ordering = ['city']