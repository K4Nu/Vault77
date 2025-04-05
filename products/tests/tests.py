import pytest
from products.models import Gender

@pytest.mark.django_db
class TestGenderModel:
    def test_str_method(self):
        gender = Gender.objects.create(gender_name='male')
        assert str(gender) == 'male'