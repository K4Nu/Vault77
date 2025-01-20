from django.db import models
from django.utils.text import slugify
from django.core.validators import FileExtensionValidator

class Category(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    is_gender_category = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ['name']

    def __str__(self):
        full_path = self.name
        k = self
        while k.parent:
            full_path = k.parent.name + ' > ' + full_path
            k = k.parent
        return full_path

    def save(self, *args, **kwargs):
        if not self.slug:
            if self.parent:
                # Include parent name in slug for uniqueness
                self.slug = slugify(f"{self.parent.name}-{self.name}")
            else:
                self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Size(models.Model):
    name = models.CharField(max_length=20)  # S, M, L, XL, etc.
    order = models.PositiveIntegerField(default=0)  # For consistent size ordering

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in EUR")
    stock = models.PositiveIntegerField()
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['created']),
        ]

    def __str__(self):
        return self.name

    @property
    def gender(self):
        """Returns the gender category of the product"""
        return self.category.gender

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    sku = models.CharField(max_length=100, unique=True)
    stock = models.PositiveIntegerField()
    available = models.BooleanField(default=True)

    class Meta:
        unique_together = ['product', 'size']

    def __str__(self):
        return f"{self.product.name} - {self.size.name}"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(
        upload_to='products/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )