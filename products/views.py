# views.py


from django.db.models import OuterRef, Subquery, Prefetch
from rest_framework import viewsets
from .models import ProductItem, ProductImage,Color
from .serializers import ProductItemSerializer

class ProductItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductItem.objects.select_related('product').prefetch_related(
        Prefetch("product__items",queryset=ProductItem.objects.select_related('color'),to_attr="all_items"),
        Prefetch("images",queryset=ProductImage.objects.order_by("order"),to_attr="all_images")
    )
    serializer_class = ProductItemSerializer