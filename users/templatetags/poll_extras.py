from django import template
from allauth.socialaccount.models import SocialAccount

register = template.Library()

@register.simple_tag(takes_context=True)
def is_google_user(context):
    user = context.get('user', None)
    if user and user.is_authenticated:
        # Check if a SocialAccount with Google exists for this user
        return SocialAccount.objects.filter(user=user, provider='google').exists()
    return False