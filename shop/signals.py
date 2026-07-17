from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Product, Category


@receiver([post_save, post_delete], sender=Product)
def clear_product_cache(sender, instance, **kwargs):
    cache.delete(f'product_detail_{instance.id}')
    cache.delete('all_categories')


@receiver([post_save, post_delete], sender=Category)
def clear_category_cache(sender, instance, **kwargs):
    cache.delete('all_categories')