from django.db.models import Prefetch
from rest_framework import viewsets,serializers
from .models import ProductItem, ProductImage, Category,ProductVariant
from .serializers import ProductItemSerializer, CategoryProductItemSerializer,CategorySerializer
from rest_framework.serializers import SerializerMethodField
class ProductItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Each ProductItem is serialized with:
      - product__items → all_items  (all sibling items, color-select_related)
      - images → all_images         (to grab up to two images)
    """
    queryset = ProductItem.objects.select_related('product').prefetch_related(
        Prefetch(
            "product__items",
            queryset=ProductItem.objects.select_related('color'),
            to_attr="all_items"
        ),
        Prefetch("variants",
                 queryset=ProductVariant.objects.select_related("size").order_by('size__order'),to_attr="all_variants"),
        Prefetch(
            "images",
            queryset=ProductImage.objects.order_by("order"),
            to_attr="all_images"
        ),
    )
    serializer_class = ProductItemSerializer
    lookup_field = 'slug'

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Returns categories with their children and all associated product items.
    """
    queryset = Category.objects.prefetch_related(
        "children",
        "products",
        Prefetch(
            "products__items",
            queryset=ProductItem.objects
                .select_related("color")
                .prefetch_related(
                    Prefetch(
                        "images",
                        queryset=ProductImage.objects.order_by("order"),
                        to_attr="all_cat_images"
                    )
                ),
            to_attr="all_items"
        ),
    )
    serializer_class = CategorySerializer
    lookup_field = 'slug'