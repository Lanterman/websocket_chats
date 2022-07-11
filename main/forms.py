import re

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class AbstractForm(forms.Form):
    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        re_value = re.findall(r'\d|\W', first_name)
        invalid_list = []
        if len(first_name) > 20:
            invalid_list.append(ValidationError('Максимальное число символов 20, у вас %(value)s',
                                                params={'value': len(first_name)}))
        if len(first_name) < 3 and first_name:
            invalid_list.append(ValidationError('Минимальное число символов 3, у вас %(value)s',
                                                params={'value': len(first_name)}))
        if re_value:
            invalid_list.append(ValidationError('Имя должно содержать только буквы'))
        if invalid_list:
            raise ValidationError(invalid_list)
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        re_value = re.findall(r'\d|\W', last_name)
        invalid_list = []
        if len(last_name) > 25:
            invalid_list.append(ValidationError('Максимальное число символов 25, у вас %(value)s',
                                                params={'value': len(last_name)}))
        if len(last_name) < 3 and last_name:
            invalid_list.append(ValidationError('Минимальное число символов 3, у вас %(value)s',
                                                params={'value': len(last_name)}))
        if re_value:
            invalid_list.append(ValidationError('Имя должно содержать только буквы'))
        if invalid_list:
            raise ValidationError(invalid_list)
        return last_name


class RegisterUserForm(AbstractForm, UserCreationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'placeholder': 'Логин'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}))
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'placeholder': 'Повтор пароль'}))
    first_name = forms.CharField(label='Имя', widget=forms.TextInput(attrs={'placeholder': 'Имя'}))
    last_name = forms.CharField(label='Фамилия', widget=forms.TextInput(attrs={'placeholder': 'Фамилия'}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'placeholder': 'Электронная почта'}))

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'first_name', 'last_name', 'email')


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя', widget=forms.TextInput(attrs={'placeholder': 'Логин'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}))
