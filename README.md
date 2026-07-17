# PeripheryShop — Інтернет-магазин периферії

Інтернет-магазин комп'ютерної периферії (клавіатури, миші, навушники, веб-камери тощо) з темною кіберпанк-темою.

## Технології

- Python 3.14 / Django 6.0.6
- PostgreSQL (хостинг Railway)
- Cloudinary (зображення товарів)
- Bootstrap 5.3.3
- Django Allauth (реєстрація, вхід через Google)

## Основний функціонал

- Каталог товарів із фільтрацією та сортуванням (за ціною, назвою, популярністю)
- Детальна сторінка товару з характеристиками
- Пошук із автокомплітом
- Кошик та оформлення замовлення
- Реєстрація/вхід через email, телефон або Google-аккаунт
- Список бажань (вishlist)
- Історія замовлень
- Адмін-панель для керування товарами та замовленнями
- Темна/світла тема (перемикач)
- Адаптивний дизайн (мобільна версія з нижньою навігацією)
- Відправка email-повідомлень при оформленні замовлення

## Як запустити локально

```bash
git clone https://github.com/whyfoboss/periphery-shop.git
cd periphery-shop
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata data_fixture.json
python manage.py createsuperuser
python manage.py runserver
```

