from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from users.forms import CustomSignupForm, UserInfoForm, PasswordChangeForm, EmailChangeForm

User = get_user_model()

class CustomSignupFormTest(TestCase):
    def setUp(self):
        pass

    def correct_signup(self):
        form_data=CustomSignupForm({"email":"test@test12.com","password1":"3/lS30v8}7Of","password2":"3/lS30v8}7Of"})
        self.assertTrue(form_data.is_valid())