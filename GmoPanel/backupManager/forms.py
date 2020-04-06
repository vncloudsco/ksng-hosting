from django import forms
from .models import BackupLog
from django.core.validators import MinValueValidator, MaxValueValidator

TYPE_CHOICES =(
    ("0", "Localhost"),
    ("1", "Remote SSH"),
    ("2", "Google Drive"),
)
CHOICES_WEEK = [
    (0, 'Sunday'),
    (1, 'Monday'),
    (2, 'Tuesday'),
    (3, 'Wednesday'),
    (4, 'Thurday'),
    (5, 'Friday'),
    (6, 'Saturday'),

]
def check_value_retention(value):
    if int(value) >= 0 and int(value) <= 9999:
        pass

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

class CronJobForm(forms.Form):
    id = forms.IntegerField(  # A hidden input for internal use
        widget=forms.HiddenInput(

        ),
        required=False,
    )
    backup_schedu = forms.MultipleChoiceField(
        choices=[('daily', 'Backup Daily'), ('weekly', 'Backup Weekly'), ('monthly', 'Backup Monthly')],
        widget=forms.CheckboxSelectMultiple
    )
    backup_day = forms.MultipleChoiceField(
        choices=CHOICES_WEEK,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    backup_week = forms.ChoiceField(
        choices=CHOICES_WEEK,
        widget=forms.RadioSelect(
            attrs={
                'class': 'checkbox-inline icheckbox',
            }
        ),
        required=False,
    )
    backup_type = forms.ChoiceField(
        required=True,
        widget=forms.RadioSelect(
            attrs={
                'class': 'checkbox-inline icheckbox',
            },
        ),
        choices = TYPE_CHOICES,
    )
    host = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
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

    def clean(self):
        cleaned_data = super().clean()
        backup_type = cleaned_data.get("backup_type")
        host = cleaned_data.get("host")
        port = cleaned_data.get("port")
        user = cleaned_data.get("user")
        password = cleaned_data.get("password")
        path = cleaned_data.get("path")
        if backup_type and int(backup_type) == 1:
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


class RetentionForm(forms.Form):
    backup_schedu = forms.MultipleChoiceField(
        choices=[('daily', 'Backup Daily'), ('weekly', 'Backup Weekly'), ('monthly', 'Backup Monthly')],
        widget=forms.CheckboxSelectMultiple
    )
    backup_daily_retention = forms.IntegerField(
        validators=[MinValueValidator(0),MaxValueValidator(9999)],
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'disabled': True,
            }
        ),
        label='',
        required=False,
    )
    backup_weekly_retention = forms.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(9999)],
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'disabled': True,
            }
        ),
        label='',
        required=False,
    )
    backup_monthly_retention = forms.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(9999)],
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'disabled': True,
            }
        ),
        label='',
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        backup_schedu = cleaned_data.get("backup_schedu")
        daily = cleaned_data.get("backup_daily_retention")
        week = cleaned_data.get("backup_weekly_retention")
        month = cleaned_data.get("backup_monthly_retention")
        if backup_schedu is not None and 'daily' in backup_schedu and daily is None:
            self.add_error('backup_daily_retention', 'Retention is not empty!')
        if backup_schedu is not None and 'weekly' in backup_schedu and week is None:
            self.add_error('backup_weekly_retention', 'Retention is not empty!')
        if backup_schedu is not None and 'monthly' in backup_schedu and month is None:
            self.add_error('backup_monthly_retention', 'Retention is not empty!')





