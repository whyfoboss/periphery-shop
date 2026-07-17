from django.conf import settings
from django.db import models
from shop.models import Product


class ShippingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    address_line = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f'{self.full_name}, {self.city}'


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'В обробці'),
        ('paid', 'Оплачено'),
        ('shipped', 'Відправлено'),
        ('delivered', 'Доставлено'),
        ('cancelled', 'Скасовано'),
    ]

    PAYMENT_CHOICES = [
        ('cash', 'Готівка при отриманні'),
        ('card', 'Оплата карткою онлайн'),
        ('google_pay', 'Google Pay'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='orders')
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Замовлення №{self.id}'

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def get_cost(self):
        return self.price * self.quantity


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    changed_at = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f'{self.order} → {self.status}'