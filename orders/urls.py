from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout_step1, name='checkout'),
    path('checkout/confirm/', views.checkout_step2, name='checkout_step2'),
    path('created/<int:order_id>/', views.order_created, name='order_created'),
    path('history/', views.order_history, name='order_history'),
]