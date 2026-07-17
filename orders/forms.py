from django import forms
from .models import ShippingAddress


class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['full_name', 'phone', 'city', 'address_line', 'postal_code']