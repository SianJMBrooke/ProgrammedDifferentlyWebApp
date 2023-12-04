from django import forms
from .models import UploadModel


class UploadForm(forms.ModelForm):
    class Meta:
        model = UploadModel
        fields = ['name', 'email', 'github']

    file = forms.FileField(label='Upload your Python file', required=True,
                           widget=forms.FileInput(attrs={'accept': '.py'}))
    consent = forms.BooleanField(label='I consent to having my data stored and processed.')
