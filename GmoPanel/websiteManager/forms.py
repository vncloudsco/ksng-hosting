from django import forms
from .models import Provision
import validators

class CreateWebsiteForm(forms.ModelForm):
    app_id = forms.IntegerField(  # A hidden input for internal use
        widget=forms.HiddenInput()
    )
    domain = forms.CharField(
        max_length=200,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter Domain Name',
                'id': 'domain_name'
            },
        ),
        label='Domain Name'
    )
    email = forms.CharField(
        max_length=100,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Enter Email'
            }
        ),
        label='Email Address'
    )
    db_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Database name',
                'id': 'db_name'
            }
        ),
        label='Database Name'
    )
    db_user = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Database username',
                'id': 'db_username'
            }
        ),
        label='Database Username'
    )
    db_password = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Database password',
                'id': 'db_password'
            }
        ),
        label='Database password'
    )

    class Meta:
        model = Provision
        fields = ('app_id', 'domain', 'email', 'db_name', 'db_user', 'db_password')


    def clean(self):
        cleaned_data = super().clean()
        domain = cleaned_data.get("domain")
        app_id = cleaned_data.get("app_id")
        db_name = cleaned_data.get("db_name")
        db_user = cleaned_data.get("db_user")
        db_password = cleaned_data.get("db_password")
        # check domain name
        if validators.domain(domain) != True:
            self.add_error('domain', 'Domain is not correct!')
        # check domain is exits
        pro = Provision.objects.filter(domain=domain,deactive_flg=0)
        if pro:
            self.add_error('domain','Domain is exits!')
        # check db_name is exits
        pro = Provision.objects.filter(db_name=db_name, deactive_flg=0)
        if pro:
            self.add_error('db_name','Database name is exits!')
        # check db_user is exits
        pro = Provision.objects.filter(db_user=db_user, deactive_flg=0)
        if pro:
            self.add_error('db_user', 'Database username is exits!')
        if app_id and app_id not in [1,2,3,4,5]:
            self.add_error('app_id', 'CMS is not correct!')

