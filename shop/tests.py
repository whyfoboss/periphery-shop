from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Category, Brand, Product

User = get_user_model()


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Мишки', slug='mishky', audience='gaming')
        self.brand = Brand.objects.create(name='Logitech', slug='logitech')
        self.product = Product.objects.create(
            category=self.category, brand=self.brand,
            name='Тестова мишка', slug='testova-myshka',
            price=999, stock=10
        )

    def test_product_created(self):
        self.assertEqual(self.product.name, 'Тестова мишка')
        self.assertTrue(self.product.available)

    def test_product_str(self):
        self.assertEqual(str(self.product), 'Тестова мишка')

    def test_get_absolute_url(self):
        url = self.product.get_absolute_url()
        self.assertIn(str(self.product.id), url)


class ProductListViewTest(TestCase):
    def setUp(self):
        category = Category.objects.create(name='Клавіатури', slug='klaviatury')
        Product.objects.create(category=category, name='Клавіатура A', slug='klaviatura-a', price=500, stock=5)

    def test_product_list_status_code(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_product_list_contains_product(self):
        response = self.client.get('/')
        self.assertContains(response, 'Клавіатура A')