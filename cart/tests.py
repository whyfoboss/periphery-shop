from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from shop.models import Category, Product
from .cart import Cart


class CartTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        category = Category.objects.create(name='Навушники', slug='navushnyky')
        self.product = Product.objects.create(
            category=category, name='Навушники X', slug='navushnyky-x', price=1000, stock=10
        )

    def _get_request_with_session(self):
        request = self.factory.get('/')
        middleware = SessionMiddleware(lambda r: None)
        middleware.process_request(request)
        request.session.save()
        return request

    def test_add_to_cart(self):
        request = self._get_request_with_session()
        cart = Cart(request)
        cart.add(self.product, quantity=2)
        self.assertEqual(len(cart), 2)

    def test_cart_total_price(self):
        request = self._get_request_with_session()
        cart = Cart(request)
        cart.add(self.product, quantity=3)
        self.assertEqual(cart.get_total_price(), 3000)

    def test_remove_from_cart(self):
        request = self._get_request_with_session()
        cart = Cart(request)
        cart.add(self.product, quantity=1)
        cart.remove(self.product)
        self.assertEqual(len(cart), 0)