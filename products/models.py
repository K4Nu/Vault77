from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)

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
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    name=models.CharField(max_length=150)
    slug=models.SlugField(max_length=150, unique=True)
    description=models.TextField()
    price=models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in EUR")
    stock=models.PositiveIntegerField()
    available=models.BooleanField(default=True)
    created=models.DateTimeField(auto_now_add=True)
    updated=models.DateTimeField(auto_now=True)
    category=models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        indexes=[
            models.Index(fields=['name']),
            models.Index(fields=['created']),
        ]