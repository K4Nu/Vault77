from allauth.account.signals import email_confirmed
from django.db.models.signals import post_save
from allauth.account.models import EmailAddress
from .models import AppUser
from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from allauth.socialaccount.models import SocialAccount

User=get_user_model()

@receiver(user_signed_up)
def google_user_profile(request,user,**kwargs):
    """
    Signal to populate the AppUser model or update it after a user signs up using Google
    """
    try:
       social_account=SocialAccount.objects.get(user=user)
       data=social_account.extra_data
       firstname=data.get("given_name", "")
       lastname=data.get('family_name',"")
       email=data.get("email","")

       user.firstname=firstname
       user.lastname=lastname
       user.email=email
       user.save()

    except SocialAccount.DoesNotExist:
        pass

@receiver(email_confirmed)
def email_confirmed_callback(request,email_address, **kwargs):
    user=AppUser.objects.get(email=email_address.email)
    user.is_verified=True
    user.is_active=True
    user.save()

@receiver(post_save,sender=AppUser)
def super_user_verification(sender,instance,created,**kwargs):
    if created and (instance.is_superuser or instance.is_staff):
        if not instance.is_verified:
            instance.is_verified=True
            instance.is_active=True
            instance.save(update_fields=["is_verified","is_active"])
        email_address,email_created=EmailAddress.objects.get_or_create(user=instance,
                                                                       email=instance.email,
                                                                       defaults={"verified":True,"primary":True})
        if not email_created and not email_address.verified:
            email_address.verified = True
            email_address.save(update_fields=['verified'])
