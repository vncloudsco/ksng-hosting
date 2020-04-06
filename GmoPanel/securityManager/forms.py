from django import forms
from websiteManager.models import Provision
from django.core.exceptions import ValidationError
from .models import Waf
from django.core.validators import validate_ipv4_address
import re
from django.utils.translation import gettext_lazy as _

def checkUrl(value):
    """
    validate url
    :param value:
    :return:
    """
    rex = re.search("^(\\:\\d+)?([-a-z\\d%_.~+]*)*(\\?[;&a-z\\d%_.~+=-]*)?(\\#[-a-z\\d_]*)?$",value)
    if rex is None:
        raise ValidationError(_("The URL is malformed! (example : wp-admin)!"))

def checkUser(value):
    """
    validate user
    :param value:
    :return:
    """
    rex = re.search("^[0-9a-zA-z.]{4,32}$", value)
    if rex is None:
        raise ValidationError(_("Username must be in a->z, A->Z or 0->9 min 4 max 32 chars!"))

def checkPassword(value):
    """
    validate password
    :param value:
    :return:
    """
    rex = re.search("^[0-9A-za-z!@#$%^&*()-_.]{4,32}$", value)
    if rex is None:
        raise ValidationError(_("Password must be in a->z, A->Z, 0->9 or special characters min 4 max 32 chars!"))

class GoogleForm(forms.Form):
    security_status = forms.BooleanField(
        widget=forms.CheckboxInput(
            attrs={
                'class': 'js-switch'
            }
        ),
        required=False
    )
    security_code = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'id': 'security-code',
            }
        ),
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('security_status')
        code = cleaned_data.get('security_code')

        if status and not code:
            self.add_error('security_code', 'Security Code Id is required!')
        if status and len(code) != 16:
            self.add_error('security_code','Security Code is not correct')

class AuthenRebaForm(forms.ModelForm):
    url = forms.CharField(
        validators=[checkUrl],
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'id': 'url',
                'placeholder': 'wp-admin'
            }
        ),
        label='URL'
    )
    user = forms.CharField(
        validators=[checkUser],
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'id': 'user',
                'placeholder': 'Enter username'
            }
        )
    )
    password = forms.CharField(
        validators=[checkPassword],
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'id': 'password',
                'placeholder': 'Enter password'
            }
        )
    )

    class Meta():
        model = Waf
        fields = ('url','user','password')

class IpRebiForm(forms.ModelForm):
    url = forms.CharField(
        validators=[checkUrl],
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'id': 'url',
                'placeholder': 'wp-admin'
            }
        ),
        label='URL'
    )
    ip = forms.CharField(
        validators=[validate_ipv4_address],
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'id': 'ip',
                'placeholder': 'IPv4'
            }
        )
    )

    class Meta():
        model = Waf
        fields = ('url','ip')

class ChangeAuthForm(forms.Form):
    new_password = forms.CharField(
        validators=[checkPassword],
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'id': 'password',
                'placeholder': 'Enter password'
            }
        )
    )
class ChangeIpForm(forms.Form):
    new_ip = forms.CharField(
        validators=[validate_ipv4_address],
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'id': 'ip',
                'placeholder': 'IPv4'
            }
        )
    )