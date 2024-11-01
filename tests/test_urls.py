from django.test import TestCase
from django.urls import reverse

class BaseTestCase(TestCase):
    def test_base(self):
        assert 1==1

