from django.contrib import admin
from products.models import (
    Product,
    ProductItem,
    ProductImage,
    Size,
    SizeGroup,
    ProductVariant,
    Color,
    Category,
)
from mptt.admin import DraggableMPTTAdmin

# Register Category with a tree admin display
@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    mptt_indent_field = "name"
    list_display = (
        'tree_actions',
        'indented_title',
        # Optional: you could show slug or other fields too
        'slug',
    )
    list_display_links = ('indented_title',)
    # Optionally control indentation width:
    mptt_level_indent = 30

# Register the Product model
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category',)
    prepopulated_fields = {"slug": ("name",)}

# Register the ProductItem model
@admin.register(ProductItem)
class ProductItemAdmin(admin.ModelAdmin):
    list_display = ('get_product_name', 'get_product_category', 'product', 'color', 'price', 'product_code', 'slug',)
    prepopulated_fields = {"slug": ("product_code",)}

    def get_product_name(self,obj):
        return obj.product.name
    get_product_name.short_description = 'Product name'

    def get_product_category(self, obj):
        return obj.product.category
    get_product_category.short_description = 'Category'

# Register the ProductImage model
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('name', 'item', 'order', 'created_at', 'updated_at',)
    prepopulated_fields = {"slug": ("name",)}

# Register the Size model
@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'size_group', 'order',)

# Register the SizeGroup model
@admin.register(SizeGroup)
class SizeGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    prepopulated_fields = {"slug": ("name",)}

# Register the ProductVariant model
@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product_item', 'size', 'quantity',)

# Register the Color model
@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name',)
