from email.policy import default

from allauth.account.signals import email_confirmed
from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.account.models import EmailAddress
from .models import AppUser

@receiver(email_confirmed)
def email_confirmed_callback(request,email_address, **kwargs):
    user=AppUser.objects.get(email=email_address.email)
    user.is_verified=True
    user.save()

@receiver(post_save,sender=AppUser)
def super_user_verification(sender,instance,created,**kwargs):
    if created and (instance.is_superuser or instance.is_staff):
        if not instance.is_verified:
            instance.is_verified=True
            instance.save(update_fields=["is_verified"])
        email_address,email_created=EmailAddress.objects.get_or_create(user=instance,
                                                                       email=instance.email,
                                                                       defaults={"verified":True,"primary":True})
        if not email_created and not email_address.verified:
            email_address.verified = True
            email_address.save(update_fields=['verified'])
