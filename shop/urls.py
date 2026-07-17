from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product/<int:product_id>/review/', views.add_review, name='add_review'),
    path('product/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('api/search-suggestions/', views.search_suggestions, name='search_suggestions'),
]