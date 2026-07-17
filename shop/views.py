from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Min, Max, Count, Avg
from .models import Category, Product, Brand
from .forms import ReviewForm


RECENTLY_VIEWED_LIMIT = 10


def _get_recently_viewed(request):
    ids = request.session.get('recently_viewed', [])
    if not ids:
        return []
    products = list(
        Product.objects.filter(id__in=ids, available=True)
        .select_related('category', 'brand')
        .prefetch_related('images')
    )
    product_map = {p.id: p for p in products}
    return [product_map[pid] for pid in ids if pid in product_map]


def _add_to_recently_viewed(request, product_id):
    ids = request.session.get('recently_viewed', [])
    if product_id in ids:
        ids.remove(product_id)
    ids.insert(0, product_id)
    request.session['recently_viewed'] = ids[:RECENTLY_VIEWED_LIMIT]


def product_list(request, category_slug=None):
    categories = cache.get('all_categories')
    if categories is None:
        categories = list(
            Category.objects.annotate(
                product_count=Count('products', filter=Q(products__available=True))
            )
        )
        cache.set('all_categories', categories, 60 * 60)

    category = None
    base_products = Product.objects.filter(available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        base_products = base_products.filter(category=category)

    price_bounds = base_products.aggregate(min_price=Min('price'), max_price=Max('price'))
    min_price = price_bounds['min_price'] or Decimal('0')
    max_price = price_bounds['max_price'] or Decimal('0')

    products = base_products.select_related('category', 'brand').prefetch_related('images').annotate(
        avg_rating=Avg('reviews__rating'),
        reviews_count=Count('reviews', distinct=True),
    )

    query = request.GET.get('q')
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    brand_id = request.GET.get('brand')
    if brand_id:
        products = products.filter(brand_id=brand_id)

    audience = request.GET.get('audience')
    if audience:
        products = products.filter(category__audience=audience)

    def parse_price(value):
        try:
            return Decimal(value)
        except (InvalidOperation, TypeError):
            return None

    price_min_value = ''
    price_max_value = ''

    price_min_raw = parse_price(request.GET.get('price_min'))
    if price_min_raw is not None:
        price_min_clamped = max(price_min_raw, min_price)
        price_min_clamped = min(price_min_clamped, max_price)
        products = products.filter(price__gte=price_min_clamped)
        price_min_value = price_min_clamped

    price_max_raw = parse_price(request.GET.get('price_max'))
    if price_max_raw is not None:
        price_max_clamped = min(price_max_raw, max_price)
        price_max_clamped = max(price_max_clamped, min_price)
        products = products.filter(price__lte=price_max_clamped)
        price_max_value = price_max_clamped

    sort = request.GET.get('sort')
    sort_options = {
        'price_asc': 'price',
        'price_desc': '-price',
        'name': 'name',
        'newest': '-created_at',
        'popular': '-reviews_count',
    }
    if sort in sort_options:
        products = products.order_by(sort_options[sort])
    else:
        products = products.order_by('-reviews_count')

    total_count = products.count()

    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    recently_viewed = _get_recently_viewed(request)

    wishlist_ids = set()
    if request.user.is_authenticated:
        wishlist_ids = set(
            request.user.wishlist.values_list('product_id', flat=True)
        )

    context = {
        'category': category,
        'categories': categories,
        'brands': Brand.objects.all(),
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'query': query or '',
        'total_count': total_count,
        'min_price': min_price,
        'max_price': max_price,
        'selected_brand': brand_id or '',
        'selected_sort': sort or '',
        'price_min_value': price_min_value,
        'price_max_value': price_max_value,
        'recently_viewed': recently_viewed,
        'wishlist_ids': wishlist_ids,
    }
    return render(request, 'shop/product_list.html', context)


def product_detail(request, id, slug):
    product = get_object_or_404(
        Product.objects.select_related('category', 'brand')
        .prefetch_related('images', 'reviews__user', 'specs')
        .annotate(avg_rating=Avg('reviews__rating'), reviews_count=Count('reviews', distinct=True)),
        id=id, slug=slug, available=True
    )

    _add_to_recently_viewed(request, product.id)

    related_products = Product.objects.filter(category=product.category, available=True).exclude(id=product.id)[:4]

    specs_grouped = {}
    for spec in product.specs.all():
        specs_grouped.setdefault(spec.group, []).append(spec)

    user_has_reviewed = False
    review_form = None
    in_wishlist = False
    if request.user.is_authenticated:
        user_has_reviewed = product.reviews.filter(user=request.user).exists()
        if not user_has_reviewed:
            review_form = ReviewForm()
        in_wishlist = request.user.wishlist.filter(product=product).exists()

    return render(request, 'shop/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'specs_grouped': specs_grouped,
        'reviews': product.reviews.select_related('user').order_by('-created_at'),
        'review_form': review_form,
        'user_has_reviewed': user_has_reviewed,
        'in_wishlist': in_wishlist,
    })


@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if product.reviews.filter(user=request.user).exists():
        messages.info(request, 'Ви вже залишали відгук на цей товар')
    return redirect(product.get_absolute_url())


def search_suggestions(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': []})

    products = Product.objects.filter(
        available=True
    ).filter(
        Q(name__icontains=q) | Q(description__icontains=q)
    ).select_related('category').prefetch_related('images')[:8]

    results = []
    for p in products:
        img = ''
        if p.images.exists():
            img = p.images.first().image.url
        results.append({
            'name': p.name,
            'price': f'{p.price:,.0f}'.replace(',', ' '),
            'url': p.get_absolute_url(),
            'image': img,
            'category': p.category.name if p.category else '',
        })

    return JsonResponse({'results': results})

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, 'Дякуємо за відгук!')

    return redirect(product.get_absolute_url())