from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from products.models import ProductItem, ProductImage, Color, Category, Size, ProductVariant


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ('name','order')

class ProductVariantSerializer(serializers.ModelSerializer):
    name=serializers.CharField(source="product_item.product.name",read_only=True)
    size = SizeSerializer(read_only=True)
    class Meta:
        model = ProductVariant
        fields = ('name','size','quantity')

    def get_sizes(self, obj):
        sizes=getattr(obj,'sizes',None)
        return SizeSerializer(sizes,many=True).data



class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ('id', 'name', 'hex_code')


class ProductItemImageSerializer(serializers.ModelSerializer):
    url = SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ('url',)

    def get_url(self, obj):
        # first get the bare URL (or None if no file)
        try:
            raw_url = obj.filename.url
        except ValueError:
            return None

        request = self.context.get('request')
        if request is None:
            # no request in context — just return the raw URL
            return raw_url
        return request.build_absolute_uri(raw_url)


class SimpleProductItemSerializer(serializers.ModelSerializer):
    color=ColorSerializer(read_only=True)
    img=SerializerMethodField()

    class Meta:
        model = ProductItem
        fields=("id","slug","color","img")

    def get_img(self, obj):
        # prefer the `.all_images` cache if you have it…
        imgs = getattr(obj, 'all_images', obj.images.all())
        first = imgs[0] if imgs else None
        if not first:
            return None
        return ProductItemImageSerializer(first, many=False, context=self.context).data



class ProductItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    colors       = SerializerMethodField()
    images       = SerializerMethodField()
    variants= SerializerMethodField()
    related_items=SerializerMethodField()
    class Meta:
        model  = ProductItem
        fields = ("product_name", "slug", "price", "colors", "images",'variants','related_items')

    def get_colors(self, obj):
        # Prefer the cached list of sibling items, fallback to DB
        siblings = getattr(obj.product, 'all_items', None)
        print(siblings)
        if siblings is None:
            siblings = obj.product.items.select_related('color').all()
        print(siblings)
        seen = {}
        # Always include current item's color first
        if obj.color:
            seen[obj.color.id] = obj.color

        for item in siblings:
            if item.color and item.color.id not in seen:
                seen[item.color.id] = item.color

        return ColorSerializer(list(seen.values()), many=True, context=self.context).data

    def get_images(self, obj):
        # Prefer all_cat_images > all_images > DB fallback
        all_imgs=getattr(obj, 'all_images', [])
        if all_imgs:
            return ProductItemImageSerializer(all_imgs, many=True, context=self.context).data
        cat_imgs=getattr(obj, 'all_cat_images', None)[:2]
        return ProductItemImageSerializer(cat_imgs, many=True, context=self.context).data

    def get_variants(self, obj):
        # use the prefetched `obj.variants`
        variants = getattr(obj, 'all_variants', [])
        return ProductVariantSerializer(
            variants,
            many=True,
            context=self.context
        ).data

    def get_related_items(self, obj):
        # 1) pull the same `.all_items` cache you used for colors…
        siblings = getattr(obj.product, 'all_items', [])
        # 2) drop yourself from the list if you like:
        siblings = [item for item in siblings if item.pk != obj.pk]
        # 3) hand _those_ ProductItem instances to your SimpleProductItemSerializer
        return SimpleProductItemSerializer(
            siblings,
            many=True,
            context=self.context
        ).data

class CategorySerializer(serializers.ModelSerializer):
    children = SerializerMethodField()
    items = SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'children', 'items')

    def get_children(self, obj):
        return CategorySerializer(
            obj.children.all(),
            many=True,
            context=self.context
        ).data

    def get_items(self, obj):
        all_items = []
        for product in obj.products.all():
            all_items.extend(getattr(product, 'all_items', []))
        return CategoryProductItemSerializer(
            all_items,
            many=True,
            context=self.context
        ).data

class CategoryProductItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    colors = SerializerMethodField()
    images = SerializerMethodField()
    variants = SerializerMethodField()

    class Meta:
        model = ProductItem
        fields = ("product_name", "slug", "price", "colors", "images", "variants")

    def get_colors(self, obj):
        siblings = getattr(obj.product, 'all_items', None)
        if siblings is None:
            siblings = obj.product.items.select_related('color').all()

        seen = {}
        if obj.color:
            seen[obj.color.id] = obj.color

        for item in siblings:
            if item.color and item.color.id not in seen:
                seen[item.color.id] = item.color

        return ColorSerializer(list(seen.values()), many=True, context=self.context).data

    def get_images(self, obj):
        # Use prefetched category-specific images
        imgs = getattr(obj, 'all_cat_images', [])
        return ProductItemImageSerializer(imgs[:2], many=True, context=self.context).data

    def get_variants(self, obj):
        variants = getattr(obj, 'all_variants', [])
        return ProductVariantSerializer(variants, many=True, context=self.context).data