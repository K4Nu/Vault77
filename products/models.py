from django.db import models
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey
from mptt.managers import TreeManager
from django.urls import reverse

class Gender(models.Model):
    name= models.CharField(max_length=100,unique=True)
    def __str__(self):
        return self.name

class CategoryManager(TreeManager):
    def get_queryset(self):
        return super().get_queryset().filter(parent=None)


class SizeGroup(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255)

    class Meta:
        ordering = ['name']
        verbose_name = 'Size Group'
        verbose_name_plural = 'Size Groups'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Always generate slug from the name
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Category(MPTTModel):
    name = models.CharField(max_length=100)
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        db_index=True
    )
    gender = models.ForeignKey(
        Gender,
        on_delete=models.CASCADE,
        related_name='categories'  # Unique related name for gender field
    )
    slug = models.SlugField(max_length=255, unique=True)
    size_group = models.ForeignKey(
        SizeGroup,
        on_delete=models.CASCADE,
        related_name='size_group_categories'  # Unique related name for size_group field
    )
    objects = TreeManager()
    all_objects = CategoryManager()

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name_plural = 'categories'
        verbose_name = 'category'
        unique_together = ('parent', 'name')
        ordering = ('name',)
        indexes = [
            models.Index(fields=('slug', 'parent'), name='category_slug_parent_idx')
        ]

    def __str__(self):
        return ' > '.join([ancestor.name for ancestor in self.get_ancestors(include_self=True)])

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)

        # Compute the slug based on gender and ancestors
        ancestors = self.get_ancestors(include_self=True)
        path = str(self.gender) + "-" + '-'.join([p.name for p in ancestors])
        new_slug = slugify(path)

        if self.slug != new_slug:
            self.slug = new_slug
            super().save(update_fields=['slug'])

    """
        @property
    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})
    """

class Size(models.Model):
    name = models.CharField(max_length=100)
    size_group = models.ForeignKey(
        SizeGroup,
        on_delete=models.CASCADE,
        related_name='sizes'
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('size_group', 'name')
        ordering = ['order']
        verbose_name = 'Size'
        verbose_name_plural = 'Sizes'
        indexes = [
            models.Index(fields=('size_group', 'name'), name='size_group_size_group_idx'),
        ]

    def __str__(self):
        return f"{self.size_group.name} - {self.name}"

    def save(self, *args, **kwargs):
        if self.pk is None:
            # Set the order to the number of sizes already in the group
            count = Size.objects.filter(size_group=self.size_group).count()
            self.order = count
        super().save(*args, **kwargs)

class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255, unique=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='products')
    description = models.TextField(blank=True, null=True)
    care_instructions = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        indexes = [
            models.Index(fields=('name', 'slug'), name='product_name_idx'),
        ]

    def __str__(self):
        return f'{self.category.name} - {self.name}'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    """
    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})
    """

class Color(models.Model):
    name=models.CharField(max_length=100)


class ProductItem(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255, unique=True)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='products')
    product_code = models.CharField(max_length=100)
    price=models.DecimalField(max_digits=10, decimal_places=2)


    class Meta:
        ordering = ['name']
        verbose_name = 'Product Item'
        verbose_name_plural = 'Product Items'
        unique_together = (('product', 'product_code'),)
        indexes = [
            models.Index(fields=['product', 'product_code'], name='product_product_code_idx'),
            models.Index(fields=['color'], name='productitem_color_idx'),
        ]

    def __str__(self):
        return f'{self.product.name} - {self.product_code}'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.product_code)
        super().save(*args, **kwargs)

class ProductImage(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255, unique=True)
    item = models.ForeignKey(ProductItem, on_delete=models.CASCADE, related_name='images')
    order = models.PositiveIntegerField(default=0)
    filename = models.ImageField(upload_to='products_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['name']  # or ['order'] if that better suits your needs
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'
        indexes = [
            models.Index(fields=['item', 'name'], name='image_product_code_idx'),
        ]

    def __str__(self):
        return f'{self.item.product_code} - {self.name}'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class ProductVariant(models.Model):
    quantity = models.PositiveIntegerField(default=0)
    size=models.ForeignKey(Size, on_delete=models.CASCADE, related_name='variants')
    product_item = models.ForeignKey(ProductItem, on_delete=models.CASCADE, related_name='variants')

    class Meta:
        unique_together = ('size', 'product_item')
        verbose_name = 'Product Variant'
        verbose_name_plural = 'Product Variants'

    def __str__(self):
        return f'{self.product_item.name} - {self.size.name}'

