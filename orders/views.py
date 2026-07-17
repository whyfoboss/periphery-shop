from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django_ratelimit.decorators import ratelimit
from cart.cart import Cart
from .forms import ShippingAddressForm
from .models import Order, OrderItem, ShippingAddress, OrderStatusHistory


DELIVERY_COST = 0


def _cart_to_session(request):
    cart = Cart(request)
    if len(cart) == 0:
        return None
    session = request.session
    if 'checkout' not in session:
        session['checkout'] = {}
    session['checkout']['items'] = [
        {
            'product_id': item['product'].id,
            'name': item['product'].name,
            'price': str(item['price']),
            'quantity': item['quantity'],
            'total': str(item['total_price']),
        }
        for item in cart
    ]
    session['checkout']['total'] = str(cart.get_total_price())
    session.modified = True
    return cart


@ratelimit(key='ip', rate='10/m', block=True)
@login_required
def checkout_step1(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect('cart:cart_detail')

    saved_addresses = ShippingAddress.objects.filter(user=request.user)

    if request.method == 'POST':
        form = ShippingAddressForm(request.POST)
        address_id = request.POST.get('address_id')
        payment_method = request.POST.get('payment_method', 'cash')

        if address_id:
            try:
                address = saved_addresses.get(id=address_id)
                request.session['checkout'] = {
                    'address_id': address.id,
                    'payment_method': payment_method,
                }
                return redirect('orders:checkout_step2')
            except ShippingAddress.DoesNotExist:
                pass

        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()

            if request.POST.get('save_address') == 'on':
                pass

            request.session['checkout'] = {
                'address_id': address.id,
                'payment_method': payment_method,
            }
            return redirect('orders:checkout_step2')
    else:
        initial = {}
        if saved_addresses.exists():
            last = saved_addresses.first()
            initial = {
                'full_name': last.full_name,
                'phone': last.phone,
                'city': last.city,
                'address_line': last.address_line,
                'postal_code': last.postal_code,
            }
        form = ShippingAddressForm(initial=initial)

    total = cart.get_total_price()
    return render(request, 'orders/checkout_step1.html', {
        'cart': cart,
        'form': form,
        'saved_addresses': saved_addresses,
        'total': total,
        'delivery_cost': DELIVERY_COST,
    })


@login_required
def checkout_step2(request):
    checkout_data = request.session.get('checkout')
    if not checkout_data or 'address_id' not in checkout_data:
        return redirect('orders:checkout_step1')

    cart = Cart(request)
    if len(cart) == 0:
        return redirect('cart:cart_detail')

    try:
        address = ShippingAddress.objects.get(id=checkout_data['address_id'], user=request.user)
    except ShippingAddress.DoesNotExist:
        return redirect('orders:checkout_step1')

    payment_method = checkout_data.get('payment_method', 'cash')
    payment_display = dict(Order.PAYMENT_CHOICES).get(payment_method, payment_method)

    total = cart.get_total_price()
    grand_total = total + DELIVERY_COST

    if request.method == 'POST':
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                shipping_address=address,
                payment_method=payment_method,
            )

            for item in cart:
                product = item['product']
                if product.stock < item['quantity']:
                    messages.error(request, f'Недостатньо товару "{product.name}" на складі')
                    return redirect('orders:checkout_step2')
                OrderItem.objects.create(
                    order=order, product=product,
                    price=item['price'], quantity=item['quantity']
                )
                product.stock -= item['quantity']
                product.save()

            OrderStatusHistory.objects.create(order=order, status='pending', comment='Замовлення створено')

        cart.clear()
        request.session.pop('checkout', None)
        send_order_email(order)
        return redirect('orders:order_created', order_id=order.id)

    return render(request, 'orders/checkout_step2.html', {
        'cart': cart,
        'address': address,
        'payment_display': payment_display,
        'total': total,
        'delivery_cost': DELIVERY_COST,
        'grand_total': grand_total,
    })


def send_order_email(order):
    subject = f'Замовлення №{order.id} прийнято'
    html_message = render_to_string('orders/email/order_confirmation.html', {'order': order})
    send_mail(
        subject, '', settings.DEFAULT_FROM_EMAIL,
        [order.user.email], html_message=html_message
    )


@login_required
def order_created(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    payment_info = ''
    if order.payment_method == 'card':
        payment_info = 'Оплату буде здійснено онлайн після підтвердження.'
    elif order.payment_method == 'google_pay':
        payment_info = 'Оплату буде здійснено через Google Pay.'
    else:
        payment_info = 'Оплата готівкою при отриманні.'
    return render(request, 'orders/order_created.html', {
        'order': order,
        'payment_info': payment_info,
    })


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_history.html', {'orders': orders})