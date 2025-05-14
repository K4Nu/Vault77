from django.db.models import Prefetch
from rest_framework import viewsets

from .models import ProductItem, ProductImage, Category
from .serializers import ProductItemSerializer, CategorySerializer

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
        Prefetch(
            "images",
            queryset=ProductImage.objects.order_by("order"),
            to_attr="all_images"
        ),
    )
    serializer_class = ProductItemSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Each Category is serialized with:
      - children
      - products
      - products__items → all_items  (so every ProductItem under a category
        has .product.all_items populated for get_colors())
      - images on those items → all_images
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
                        to_attr="all_images"
                    )
                ),
            to_attr="all_items"
        ),
    )
    serializer_class = CategorySerializer
    lookup_field = 'slug'
