from django import forms
from .models import Account

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    last_name = forms.CharField(widget=forms.TextInput())
    first_name = forms.CharField(widget=forms.TextInput())
    class Meta():
        model = Account
        fields = ('username','password','email','first_name','last_name','site','avatar')