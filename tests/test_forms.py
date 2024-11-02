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
    """
        Unit tests for PasswordChangeForm, which allows users to update their password.

        This form includes validation for:
        - Correct entry of the current password
        - Ensuring the new password meets complexity requirements (length and character mix)
        - Matching new password fields

        Test Cases:
        - test_correct_password_change: Valid data with the correct current password and matching new passwords should result in a valid form.
        - test_incorrect_current_password: An incorrect current password should invalidate the form, with an error on the 'current_password' field.
        - test_new_password_complexity: A new password that does not meet complexity criteria (e.g., too short) should invalidate the form, with an error on the 'new_password1' field.
    """
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

class EmailChangeFormTest(TestCase):
    """
    Unit tests for EmailChangeForm, which allows users to change their email address.

    This form includes validation for:
    - Matching new emails
    - Ensuring the new email is not already in use

    Test Cases:
    - test_correct_email_change: Valid data with matching emails should result in a valid form.
    - test_incorrect_email_change: Non-matching emails should invalidate the form.
    - test_used_email_change: Using an already registered email should raise a validation error.
    """

    def setUp(self):
        # Create a user for reference and another for the "used email" test case
        self.user = User.objects.create_user(email="existing@test.com", password="8jSSY7(i1g5&")
        self.other_user = User.objects.create_user(email="admin@test.com", password="i&*U@|412DK#")

    def test_correct_email_change(self):
        # Test with valid form data and matching emails
        form_data = {
            "email1": "new_email@test.com",
            "email2": "new_email@test.com",
        }
        form = EmailChangeForm(data=form_data)
        self.assertTrue(form.is_valid(), "Form should be valid with matching and unused email addresses.")

    def test_incorrect_email_change(self):
        # Test with non-matching emails
        form_data = {
            "email1": "new_email@test.com",
            "email2": "different_email@test.com",
        }
        form = EmailChangeForm(data=form_data)
        self.assertFalse(form.is_valid(), "Form should be invalid if the emails do not match.")
        self.assertIn("__all__", form.errors, "Form should have a non-field error for mismatched emails.")

    def test_used_email_change(self):
        # Test with an email already in use
        form_data = {
            "email1": "admin@test.com",
            "email2": "admin@test.com",
        }
        form = EmailChangeForm(data=form_data)
        self.assertFalse(form.is_valid(), "Form should be invalid if the new email is already registered.")
        self.assertIn("email1", form.errors, "Form should have an error on 'email1' if the email is already used.")
        self.assertEqual(form.errors["email1"][0], "This email is already in use.")


class UserInfoFormTest(TestCase):
    """
    Tests for UserInfoForm, which collects basic user information.

    Test Cases:
    - test_form_valid_data: Valid data should make the form valid.
    - test_form_exceeds_max_length: Data exceeding max_length should invalidate the form.
    - test_form_missing_data: Missing required fields should invalidate the form.
    """

    def test_form_valid_data(self):
        form_data = {
            "firstname": "John",
            "lastname": "Doe",
            "phone_number": "1234567890"
        }
        form = UserInfoForm(data=form_data)
        self.assertTrue(form.is_valid(), "Form should be valid with correct data.")

    def test_form_exceeds_max_length(self):
        form_data = {
            "firstname": "J" * 101,  # Exceeds max_length of 100
            "lastname": "Doe",
            "phone_number": "1234567890"
        }
        form = UserInfoForm(data=form_data)
        self.assertFalse(form.is_valid(), "Form should be invalid if firstname exceeds max_length.")
        self.assertIn("firstname", form.errors, "Form should have an error on 'firstname' if it exceeds max_length.")

    def test_form_missing_data(self):
        form_data = {
            "firstname": "John",
            # Missing lastname and phone_number
        }
        form = UserInfoForm(data=form_data)
        self.assertFalse(form.is_valid(), "Form should be invalid if required fields are missing.")
        self.assertIn("lastname", form.errors, "Form should have an error on 'lastname' if missing.")
        self.assertIn("phone_number", form.errors, "Form should have an error on 'phone_number' if missing.")