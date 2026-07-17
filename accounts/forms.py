from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, UserProfile


class RegisterForm(UserCreationForm):
    REG_METHOD_CHOICES = [
        ('email', 'Електронна пошта'),
        ('phone', 'Телефон'),
    ]

    reg_method = forms.ChoiceField(
        choices=REG_METHOD_CHOICES,
        widget=forms.RadioSelect,
        initial='email',
    )
    email = forms.EmailField(required=False, label='Email')
    phone = forms.CharField(max_length=20, required=False, label='Телефон')

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'password1', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        method = cleaned_data.get('reg_method')
        email = cleaned_data.get('email')
        phone = cleaned_data.get('phone')

        if method == 'email':
            if not email:
                raise forms.ValidationError('Для реєстрації через пошту вкажіть email.')
            if CustomUser.objects.filter(email=email).exists():
                raise forms.ValidationError('Користувач з таким email вже існує.')
        elif method == 'phone':
            if not phone:
                raise forms.ValidationError('Для реєстрації через телефон вкажіть номер.')
            if CustomUser.objects.filter(phone=phone).exists():
                raise forms.ValidationError('Користувач з таким телефоном вже існує.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        method = self.cleaned_data.get('reg_method')
        if method == 'phone':
            user.email = ''
        else:
            user.phone = ''
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['birth_date', 'address', 'city']
