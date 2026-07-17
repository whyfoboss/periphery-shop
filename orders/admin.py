from django.contrib import admin
from .models import Order, OrderItem, ShippingAddress, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'payment_method', 'paid', 'created_at']
    list_filter = ['status', 'payment_method', 'paid', 'created_at']
    inlines = [OrderItemInline, OrderStatusHistoryInline]


admin.site.register(ShippingAddress)