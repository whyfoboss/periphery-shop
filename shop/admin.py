from django.contrib import admin
from .models import Category, Brand, Product, ProductImage, Review, ProductSpec


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductSpecInline(admin.TabularInline):
    model = ProductSpec
    extra = 3


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'audience', 'slug']
    list_filter = ['audience']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'brand', 'price', 'stock', 'available']
    list_filter = ['available', 'category', 'brand', 'created_at']
    list_editable = ['price', 'stock', 'available']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductSpecInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating']