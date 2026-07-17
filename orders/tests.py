from django.test import TestCase
from django.contrib.auth import get_user_model
from shop.models import Category, Product
from .models import Order, OrderItem, ShippingAddress

User = get_user_model()


class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123', email='test@test.com')
        category = Category.objects.create(name='Мікрофони', slug='mikrofony')
        self.product = Product.objects.create(
            category=category, name='Мікрофон Y', slug='mikrofon-y', price=1500, stock=5
        )
        self.address = ShippingAddress.objects.create(
            user=self.user, full_name='Тест Тестович', phone='+380001112233',
            city='Київ', address_line='вул. Тестова, 1'
        )

    def test_order_total_cost(self):
        order = Order.objects.create(user=self.user, shipping_address=self.address)
        OrderItem.objects.create(order=order, product=self.product, price=1500, quantity=2)
        self.assertEqual(order.get_total_cost(), 3000)

    def test_stock_decreases_after_order_item(self):
        initial_stock = self.product.stock
        order = Order.objects.create(user=self.user, shipping_address=self.address)
        OrderItem.objects.create(order=order, product=self.product, price=1500, quantity=2)
        self.product.stock -= 2
        self.product.save()
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, initial_stock - 2)