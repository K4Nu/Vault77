from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from users.forms import CustomSignupForm, UserInfoForm, PasswordChangeForm, EmailChangeForm

User = get_user_model()

class CustomSignupFormTest(TestCase):
    """
       Unit tests for the CustomSignupForm, which handles user signup with additional fields
       and validation rules.

       CustomSignupForm extends the default SignupForm by adding fields for first name, last name,
       and an optional newsletter subscription. It includes custom validation to enforce unique
       email addresses, password confirmation, and reordering of fields for the signup layout.

       Test Cases:
       - test_correct_signup: Validates that the form is correctly filled with all required fields
         and produces a valid submission.
       - test_email_uniqueness: Ensures that submitting an existing email address raises a validation
         error, preventing duplicate accounts.
       - test_optional_newsletter: Confirms that the 'newsletter' field is optional and does not
         affect form validity when omitted.
       - test_password_missmatch: Checks that the form is invalid if the password confirmation
         does not match the initial password.
       """
    def setUp(self):
        User.objects.create_user(email="existing@test.com", password="SomePassword123!")

    def test_correct_signup(self):
        # Test with valid form data
        form_data = {
            "email": "test@test12.com",
            "firstname": "Test",
            "lastname": "User",
            "password1": "3/lS30v8}7Of",
            "password2": "3/lS30v8}7Of",
            "newsletter": True
        }
        form = CustomSignupForm(data=form_data)
        self.assertTrue(form.is_valid(), "Form should be valid with correct data.")

    def test_email_uniqueness(self):
        # Test with an email that already exists
        form_data = {
            "email": "existing@test.com",
            "firstname": "Test",
            "lastname": "User",
            "password1": "3/lS30v8}7Of",
            "password2": "3/lS30v8}7Of",
        }
        form = CustomSignupForm(data=form_data)
        self.assertFalse(form.is_valid(), "Form should be invalid if the email is already registered.")
        self.assertIn("email", form.errors, "Form should have an error on the 'email' field.")
        self.assertEqual(form.errors["email"][0], "A user is already registered with this email address.")

    def test_optional_newsletter(self):
        # Test without the newsletter field
        form_data = {
            "email": "optional@test.com",
            "firstname": "Optional",
            "lastname": "User",
            "password1": "3/lS30v8}7Of",
            "password2": "3/lS30v8}7Of",
        }
        form = CustomSignupForm(data=form_data)
        self.assertTrue(form.is_valid(), "Form should be valid even if 'newsletter' is not specified.")

    def test_password_missmatch(self):
        form_data = {
            "email": "optional@test.com",
            "firstname": "Optional",
            "lastname": "User",
            "password1": "3/lS30v8}7Of",
            "password2": "wrongpassword",
        }
        form=CustomSignupForm(data=form_data)
        self.assertFalse(form.is_valid(), "Form should be valid even if 'password' is missmatch.")

class PasswordChangeFormTest(TestCase):
    def setUp(self):
        # Create a user and store it as self.user for easy reference
        self.user = User.objects.create_user(email="existing@test.com", password="AEZAKMI123!")

    def test_correct_password_change(self):
        # Test with valid form data
        form_data = {
            "current_password": "AEZAKMI123!",
            "new_password1": "4b'^JKH2tpV7",
            "new_password2": "4b'^JKH2tpV7",
        }
        form = PasswordChangeForm(data=form_data, user=self.user)  # Pass user
        self.assertTrue(form.is_valid(), "Form should be valid with correct data.")

    def test_incorrect_current_password(self):
        # Test with an incorrect current password
        form_data = {
            "current_password": "WrongPassword!",
            "new_password1": "4b'^JKH2tpV7",
            "new_password2": "4b'^JKH2tpV7",
        }
        form = PasswordChangeForm(data=form_data, user=self.user)  # Pass user
        self.assertFalse(form.is_valid(), "Form should be invalid with an incorrect current password.")
        self.assertIn("current_password", form.errors, "Form should have an error on 'current_password' field.")

    def test_new_password_complexity(self):
        # Test with a new password that does not meet complexity requirements
        form_data = {
            "current_password": "AEZAKMI123!",
            "new_password1": "short",
            "new_password2": "short",
        }
        form = PasswordChangeForm(data=form_data, user=self.user)  # Pass user
        self.assertFalse(form.is_valid(), "Form should be invalid if the new password does not meet complexity requirements.")
        self.assertIn("new_password1", form.errors, "Form should have an error on 'new_password1' field.")