from django import forms

TYPE_CHOICES =(
    ("php53", "PHP 5.3"),
    ("php", "PHP 5.6"),
    ("php70", "PHP 7.0"),
    ("php71", "PHP 7.1"),
    ("php72", "PHP 7.2"),
    ("php73", "PHP 7.3"),
)

class PhpForm(forms.Form):
    php_version = forms.ChoiceField(
        required=True,
        widget=forms.Select(
            attrs={
                'class': 'select2',
                'id': 'php-ver',
                'style': 'display: block'
            },
        ),
        choices=TYPE_CHOICES,
    )

    def clean(self):
        cleaned_data = super().clean()
        php_ver = cleaned_data.get('php_version')

        if php_ver not in ['php53', 'php', 'php70', 'php71', 'php72', 'php72']:
            self.add_error('php_version', 'Value is incorrect!')

class NginxHttpForm(forms.Form):
    domain = forms.CharField(
        required=True,
        widget=forms.HiddenInput()
    )
    type = forms.CharField(
        required=True,
        widget=forms.HiddenInput()
    )
    config_content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'summernote form-control',
                'id': 'summernote_http',
                'rows': "15"
            },
        )
    )

class NginxSslForm(forms.Form):
    domain = forms.CharField(
        required=True,
        widget=forms.HiddenInput()
    )
    type = forms.CharField(
        required=True,
        widget=forms.HiddenInput()
    )
    config_content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                'class': 'summernote form-control',
                'id': 'summernote_https',
                'rows': "15"
            },
        )
    )

    def clean(self):
        cleaned_data = super().clean()
        domain = cleaned_data.get('domain')
        type = cleaned_data.get('type')
        content = cleaned_data.get('config_content')
