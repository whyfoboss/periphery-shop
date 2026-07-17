from django.core.management.base import BaseCommand
from django.utils.text import slugify
from shop.models import Category, Brand, Product

CATEGORIES = [
    ('Мишки', 'gaming'),
    ('Клавіатури', 'gaming'),
    ('Навушники', 'universal'),
    ('Мікрофони', 'universal'),
    ('Вебкамери', 'office'),
    ('Килимки для миші', 'gaming'),
]

BRANDS = ['Logitech', 'Razer', 'HyperX', 'SteelSeries', 'A4Tech']

PRODUCTS = [
    ('Ігрова мишка G502', 'Мишки', 'Logitech', 1299),
    ('Бездротова мишка MX Master 3', 'Мишки', 'Logitech', 2599),
    ('Ігрова мишка DeathAdder V3', 'Мишки', 'Razer', 1899),
    ('Механічна клавіатура Alloy Origins', 'Клавіатури', 'HyperX', 2999),
    ('Бездротова клавіатура K380', 'Клавіатури', 'Logitech', 999),
    ('Ігрова клавіатура BlackWidow', 'Клавіатури', 'Razer', 3299),
    ('Навушники Cloud II', 'Навушники', 'HyperX', 1999),
    ('Ігрові навушники Arctis 7', 'Навушники', 'SteelSeries', 4299),
    ('Навушники Kraken X', 'Навушники', 'Razer', 1799),
    ('USB мікрофон Blue Yeti', 'Мікрофони', 'Logitech', 3499),
    ('Стрімерський мікрофон QuadCast', 'Мікрофони', 'HyperX', 3999),
    ('Вебкамера C920', 'Вебкамери', 'Logitech', 1699),
    ('Вебкамера Brio 500', 'Вебкамери', 'Logitech', 2899),
    ('Килимок QcK Large', 'Килимки для миші', 'SteelSeries', 499),
    ('Килимок Goliathus', 'Килимки для миші', 'Razer', 599),
]


class Command(BaseCommand):
    help = 'Наповнює магазин тестовими товарами'

    def handle(self, *args, **kwargs):
        for name, audience in CATEGORIES:
            Category.objects.get_or_create(name=name, slug=slugify(name), audience=audience)

        for b in BRANDS:
            Brand.objects.get_or_create(name=b, slug=slugify(b))

        for name, cat_name, brand_name, price in PRODUCTS:
            category = Category.objects.get(name=cat_name)
            brand = Brand.objects.get(name=brand_name)
            Product.objects.get_or_create(
                name=name,
                slug=slugify(name),
                defaults={
                    'category': category,
                    'brand': brand,
                    'price': price,
                    'stock': 25,
                    'description': f'{name} — якісна периферія від {brand_name}.',
                }
            )

        self.stdout.write(self.style.SUCCESS('Товари додано!'))