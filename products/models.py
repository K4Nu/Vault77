from django.db import models
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey
from mptt.managers import TreeManager
from django.urls import reverse

class Gender(models.Model):
    gender_name= models.CharField(max_length=100,unique=True)
    def __str__(self):
        return self.gender_name

class CategoryManager(TreeManager):
    def get_queryset(self):
        return super().get_queryset().filter(parent=None)

class Category(MPTTModel):
    name=models.CharField(max_length=100)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children',db_index=True)
    gender=models.ForeignKey(Gender,on_delete=models.CASCADE)
    slug=models.SlugField(max_length=255,unique=True)

    objects=TreeManager()
    all_objects=CategoryManager()

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name_plural = 'categories'
        verbose_name = 'category'
        unique_together=('parent', 'name')
        ordering = ('name',)
        indexes=[
            models.Index(fields=('slug','parent'), name='category_slug_parent_idx')
        ]

    def __str__(self):
        return ' > '.join([ancestor.name for ancestor in self.get_ancestors(include_self=True)])

    def save(self, *args, **kwargs):
        if not self.pk:
            super().save(*args, **kwargs)

        # Now compute the slug based on the ancestors
        ancestors = self.get_ancestors(include_self=True)
        path = '-'.join([p.name for p in ancestors])
        new_slug = slugify(path)

        # If the slug has changed (or wasn’t set), update it
        if self.slug != new_slug:
            self.slug = new_slug
            # Update only the slug field; this prevents duplicate insertion
            super().save(update_fields=['slug'])
    """
        @property
    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})
    """

class SizeGroup(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=255)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='size_groups'
    )

    class Meta:
        unique_together = ('category', 'slug')
        ordering = ['name']
        verbose_name = 'Size Group'
        verbose_name_plural = 'Size Groups'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Always generate slug from the name
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

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
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    """
    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})
    """
