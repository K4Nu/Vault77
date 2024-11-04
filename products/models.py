from django.db import models
import json
from django.core.cache import cache


class Category(models.Model):
    name = models.CharField(max_length=100)
    parent_category = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True)
    sizes = models.JSONField(blank=True, null=True, help_text="List of sizes applicable for this category.")

    def get_full_category_path(self):
        categories = []
        category = self
        while category:
            categories.append(category.name)
            category = category.parent_category
        return "/".join(reversed(categories))

    def __str__(self):
        return f'{self.get_full_category_path()}'
