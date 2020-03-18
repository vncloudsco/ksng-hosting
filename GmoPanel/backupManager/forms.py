from django import forms
from .models import BackupLog
import validators

TYPE_CHOICES =(
    ("0", "Localhost"),
    ("1", "Remote SSH"),
    ("2", "Google Drive"),
)

class BackupForm(forms.Form):
    id = forms.IntegerField(  # A hidden input for internal use
        widget=forms.HiddenInput(
            attrs={
                'id': 'pro_id'
            }
        ),
        required=True,
    )
    type = forms.ChoiceField(
        required=True,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'id': 'type_backup',
            },
        ),
        choices = TYPE_CHOICES,
    )
    host = forms.CharField(
        max_length=200,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control',
                'disabled': True,
                'id': 'host'
            },
        ),
        label='Host',
        required=False,
    )
    port = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'disabled': True,
                'id': 'port'
            }
        ),
        label='Port',
        required=False,
    )
    user = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'disabled': True,
                'id': 'user'
            }
        ),
        label='User Name',
        required=False,
    )
    password = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'disabled': True,
                'id': 'pasword'
            }
        ),
        label='Password',
        required=False,
    )
    path = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'disabled': True,
                'id': 'path'
            }
        ),
        label='Root Path',
        required=False,
    )
    path_drive = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'disabled': True,
                'id': 'path_drive'
            }
        ),
        label='Root Path',
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        type = int(cleaned_data.get("type"))
        host = cleaned_data.get("host")
        port = cleaned_data.get("port")
        user = cleaned_data.get("user")
        password = cleaned_data.get("password")
        path = cleaned_data.get("path")
        path_drive = cleaned_data.get("path_drive")

        if type == 0:
            pass
        elif type == 1:
            if host == '':
                self.add_error('host', 'Field is not empty!')
            if port == '':
                self.add_error('port', 'Field is not empty!')
            if user == '':
                self.add_error('user', 'Field is not empty!')
            if password == '':
                self.add_error('password', 'Field is not empty!')
            if path == '':
                self.add_error('path', 'Field is not empty!')
        elif type == 2:
            if path_drive == '':
                self.add_error('path_drive', 'Field is not empty!')
        else:
            self.add_error('type', 'Type is not correct!')

class AccessForm(forms.Form):
    token = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'id': 'token'
            }
        ),
        label='Token',
    )

    def clean(self):
        cleaned_data = super().clean()
        token = cleaned_data.get("token")

        if token == '':
            self.add_error('token', 'Token Google Authenticator is required!')

