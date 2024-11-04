from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from products.models import Category


@receiver(post_save,sender=Category)
@receiver(post_delete,sender=Category)
def update_parent_category_cache(sender,instance,**kwargs):
    Category.set_parent_category()
