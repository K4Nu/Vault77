from django.test import TestCase, Client
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModels(TestCase):
    def setUp(self):
        # Create an initial user and set up the test client
        self.user = User.objects.create_user(email='test@test.com', password='QWERTY1234$')
        self.client = Client()

    def test_user_creation(self):
        # Create a new user
        new_user = User.objects.create_user(email="admin@admin.com", password="G|QPTv49]S2A")

        # Assertions to check user creation
        self.assertIsNotNone(new_user.pk, "New user should have an ID assigned.")
        self.assertEqual(new_user.email, "admin@admin.com")
        self.assertTrue(new_user.check_password("G|QPTv49]S2A"), "Password should match the hashed password.")

    def test_user_login(self):
        # Attempt to log in with the client using the created user's credentials
        user_login = self.client.login(email="test@test.com", password="QWERTY1234$")
        self.assertTrue(user_login, "User should be able to log in with correct credentials.")

    def test_user_email_uniqueness(self):
        with self.assertRaises(Exception, msg="Creating a user with a duplicate email should raise an error."):
            User.objects.create_user(email='test@test.com', password='AnotherPass123!')

    def test_user_invalid_login(self):
        invalid_login = self.client.login(email="test@test.com", password="asdASDASDAS")
        self.assertFalse(invalid_login,"User should not be able to log in with incorrect password.")

    def test_user_change_password(self):
        self.user.set_password("<.tcXH771]Y>")
        self.user.save()

        old_password_login=self.client.login(email="test@test.com", password="QWERTY1234$")
        self.assertFalse(old_password_login,"Old password should no longer work after password change.")

        new_password_login=self.client.login(email="test@test.com", password="<.tcXH771]Y>")
        self.assertTrue(new_password_login,"New password should be able to change password.")

    def test_user_default_properties(self):
        # Check default user properties
        self.assertTrue(self.user.is_active, "Newly created user should be active by default.")
        self.assertFalse(self.user.is_staff, "Newly created user should not be staff by default.")

    def test_user_delete(self):
        self.user.delete()
        login_after=self.client.login(email="test@test.com", password="QWERTY1234$")
        self.assertFalse(login_after,"User should not be able to log in with incorrect password.")