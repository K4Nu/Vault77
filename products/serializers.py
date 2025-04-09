from rest_framework import serializers
from products.models import ProductItem, Size, ProductVariant

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ("name",)

class ProductVariantSerializer(serializers.ModelSerializer):
    size= SizeSerializer(read_only=True)
    class Meta:
        model = ProductVariant
        fields = ("size","quantity",)

class SimpleProductItemSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(read_only=True, many=True)

    class Meta:
        model = ProductItem
        fields = ('product', 'color', 'name', 'price', 'product_code', 'slug', 'variants')

class ProductItemSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(read_only=True,many=True)
    related_items = serializers.SerializerMethodField()

    class Meta:
        model = ProductItem
        fields = ('product', 'color', 'name', 'price', 'product_code', 'slug', 'variants', 'related_items')

    def get_related_items(self, obj):
        related_qs=ProductItem.objects.filter(product=obj.product).exclude(pk=obj.pk)
        return SimpleProductItemSerializer(related_qs, many=True,context=self.context).data

