from rest_framework import serializers
from products.models import (
    ProductItem, Size, ProductVariant, ProductImage, Color
)
from django.core.files.storage import default_storage

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ("name",)


class ProductVariantSerializer(serializers.ModelSerializer):
    size = SizeSerializer(read_only=True)

    class Meta:
        model = ProductVariant
        fields = ("size", "quantity",)


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ("name", "hex_code")


class SimpleProductItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    image        = serializers.SerializerMethodField()
    color        = ColorSerializer(read_only=True)
    class Meta:
        model  = ProductItem
        fields = (
            'product_name',
            'color',
            'price',
            'product_code',
            'slug',
            'image',
        )

    def get_image(self, obj):
        # `first_image_url` is the annotation holding e.g. 'products_images/abc.jpg'
        path = getattr(obj, 'first_image_url', None)
        if not path:
            return None

        # Use default_storage.url() to get the proper MEDIA_URL-prefixed path
        relative_url = default_storage.url(path)  # e.g. '/media/products_images/abc.jpg'

        # If we have a request, build absolute URI; otherwise return the relative URL
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(relative_url)
        return relative_url


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('filename', 'order')


class ProductItemSerializer(serializers.ModelSerializer):
    product_name   = serializers.CharField(source='product.name', read_only=True)
    color          = ColorSerializer(read_only=True)
    variants       = ProductVariantSerializer(many=True, read_only=True)
    images         = ProductImageSerializer(many=True, read_only=True)
    related_items  = serializers.SerializerMethodField()

    class Meta:
        model  = ProductItem
        fields = (
            'product_name',
            'color',
            'price',
            'product_code',
            'slug',
            'variants',
            'related_items',
            'images',
        )

    def get_related_items(self, obj):
        # uses the `to_attr='prefetched_related_items'` you defined in the view’s Prefetch
        prefetched = getattr(obj.product, 'prefetched_related_items', [])
        related = [item for item in prefetched if item.pk != obj.pk]
        return SimpleProductItemSerializer(related, many=True, context=self.context).data

class VariantProductItem(serializers.ModelSerializer):
    last_image=serializers.SerializerMethodField()
    color = ColorSerializer(read_only=True)

    class Meta:
        model = ProductItem

    def get_last_image(self, obj):
