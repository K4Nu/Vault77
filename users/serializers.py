# users/serializers.py
from dj_rest_auth.serializers import LoginSerializer
from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from django.contrib.auth import authenticate

class CustomLoginSerializer(LoginSerializer):
    # remove the old username…
    username = None

    # …and add an email field
    email = serializers.EmailField(required=True)

    def get_fields(self):
        """
        Take the parent fields, pop out `username`, and ensure `email` is present.
        """
        fields = super().get_fields()
        fields.pop('username', None)
        fields['email'] = serializers.EmailField()
        return fields

    def validate(self, attrs):
        email    = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError("Must include email and password.")

        # authenticate() still wants `username=…` so we pass email here
        user = authenticate(request=self.context.get('request'),
                            username=email,
                            password=password)
        if not user:
            raise serializers.ValidationError(
                "Invalid email or password.",
                code='authorization'
            )

        attrs['user'] = user
        return attrs

class CustomRegisterSerializer(RegisterSerializer):
    username = None  # Make sure username isn't used

    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)

    def get_cleaned_data(self):
        return {
            "email": self.validated_data.get("email", ""),
            "password1": self.validated_data.get("password1", ""),
            "first_name": self.validated_data.get("first_name", ""),
            "last_name": self.validated_data.get("last_name", ""),
        }

    def save(self, request):
        user = super().save(request)
        user.first_name = self.validated_data.get('first_name', '')
        user.last_name = self.validated_data.get('last_name', '')
        user.save()
        return user