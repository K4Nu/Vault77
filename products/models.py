from django.db import models
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey
from mptt.managers import TreeManager
from django.urls import reverse

class Gender(models.Model):
    gender_name= models.CharField(max_length=100,unique=True)
    def __str__(self):
        return self.gender_name