from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response

from products.models import ProductItem
from serializers import ProductItemSerializer

# Create your views here.
class ProductItemViewSet(viewsets.ModelViewSet):
    
    queryset = ProductItem.objects.all()
    serializer_class = ProductItemSerializer

