from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django_ratelimit.decorators import ratelimit
from .forms import RegisterForm, ProfileForm
from .models import Wishlist
from orders.models import Order
from shop.models import Product


@ratelimit(key='ip', rate='5/m', block=True)
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user, backend=backend)
            messages.success(request, 'Реєстрація пройшла успішно!')
            return redirect('shop:product_list')
    else:
        form = RegisterForm(initial={'reg_method': 'email'})
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профіль оновлено')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=request.user.profile)

    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    total_spent = sum(o.get_total_cost() for o in orders)

    return render(request, 'accounts/profile.html', {
        'form': form,
        'orders': orders,
        'orders_count': orders.count(),
        'total_spent': total_spent,
    })


@login_required
def wishlist_toggle(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        item.delete()
        in_wishlist = False
    else:
        in_wishlist = True
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'in_wishlist': in_wishlist})
    return redirect(request.META.get('HTTP_REFERER', 'shop:product_list'))


@login_required
def wishlist_detail(request):
    items = Wishlist.objects.filter(user=request.user).select_related('product', 'product__category', 'product__brand').prefetch_related('product__images')
    products = [item.product for item in items]
    return render(request, 'accounts/wishlist.html', {'products': products})