from django import forms
from .models import Account
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from plogical import  hashPassword
import  re

def checkPassword(value):
    """
    validate password
    :param value:
    :return:
    """
    rex = re.search("^(?=.*\d)(?=.*[A-Z])(?=.*[@%+*\'!#$^?:\(\)\{\}\[\]~.-])[0-9A-Za-z@%+*\'!#$^?:\(\)\{\}\[\]~.-]{8,32}$",value)
    if rex is None:
        raise ValidationError(
            _("""The password has minimum 8 characters and must be contain 
                 a minimum of 1 lower case letter [a-z] and 
                 a minimum of 1 upper case letter [A-Z] and 
                 a minimum of 1 numeric character [0-9] and 
                 a minimum of 1 special character: {}
            """.format('~`!@#$%^&*()-_+={}[]|\;:"<>,./?')),
        )

class ChangePassForm(forms.Form):
    user_id = forms.CharField(
        widget=forms.HiddenInput()
    )
    cur_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Current Password',
                'class': 'form-control',
                'id': 'cur_password'
            }
        ),
        label='Current Password'
    )
    password = forms.CharField(
        validators =[checkPassword],
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'New Password',
                'class': 'form-control',
                'id': 'password'
            }
        ),
        label='New password'
    )
    re_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Retype Password',
                'class': 'form-control',
                'id': 're_password'
            }
        ),
        label='Retype new password'
    )


    def clean(self):
        cleaned_data = super().clean()
        user_id = cleaned_data.get('user_id')
        cur_password = cleaned_data.get('cur_password')
        password = cleaned_data.get('password')
        re_password = cleaned_data.get('re_password')
        try:
            account = Account.objects.get(pk=user_id)
            if not hashPassword.check_password(account.password,cur_password):
                self.add_error('cur_password', 'Current Password is not correct!')
            if password == cur_password:
                self.add_error('password', 'The new password matches the current password')
            if password != re_password:
                self.add_error('re_password', 'Confirm Password entered incorrectly!')
        except ObjectDoesNotExist:
            self.add_error('user_id', 'User is not exits!')
