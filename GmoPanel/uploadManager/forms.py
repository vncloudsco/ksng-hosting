from django import forms

class UploadForm(forms.Form):
    file = forms.FileField()
    def clean_user_file(self, *args, **kwargs):
        cleaned_data = super(UploadForm,self).clean()
        file = cleaned_data.get("file")

        return file