from django.db.models import OuterRef, Subquery, Prefetch
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework import permissions, filters, generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from products.models import ProductItem, ProductVariant, ProductImage
from products.serializers import ProductItemSerializer,SimpleProductItemSerializer

# Subquery to grab each item's first-ordered image filename
first_image_qs = (
    ProductImage.objects
    .filter(item=OuterRef('pk'))
    .order_by('order')
    .values('filename')[:1]
)

# Prefetch queryset for related items, also annotated with first_image_url
related_items_qs = (
    ProductItem.objects
    .select_related('color')
    .annotate(first_image_url=Subquery(first_image_qs))
    # Optional: keep full images available if you ever need them
    .prefetch_related(
        Prefetch('images', queryset=ProductImage.objects.order_by('order'))
    )
)

last_image_qs = (ProductImage.objects.filter(item=OuterRef('pk')).order_by('-order').values('filename')[:1])

class ProductItemViewSet(ReadOnlyModelViewSet):
    """
    Read-only API endpoint for product items, optimized to avoid N+1 queries:
    - Top-level annotate first_image_url via Subquery
    - Prefetch variants, images
    - Prefetch related items (to_attr) also annotated for their first_image_url
    """
    serializer_class = ProductItemSerializer
    lookup_field = 'slug'
    queryset = (
        ProductItem.objects
        .select_related('product', 'product__category', 'color')
        # Annotate each item with its first image URL
        .annotate(first_image_url=Subquery(first_image_qs))
        .prefetch_related(
            # Top-level variants (with size)
            Prefetch('variants', queryset=ProductVariant.objects.select_related('size')),
            # Top-level images, ordered
            Prefetch('images',   queryset=ProductImage.objects.order_by('order')),
            # All items on the same product, annotated & to_attr
            Prefetch(
                'product__items',
                queryset=related_items_qs,
                to_attr='prefetched_related_items'
            ),
        )
    )

    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields    = ['product__name', 'color__name']
    filterset_fields = ['product__slug',  'color__name']

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

