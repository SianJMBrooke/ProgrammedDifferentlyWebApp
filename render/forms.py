from django import forms
from .models import UploadModel


class UploadForm(forms.ModelForm):
    class Meta:
        model = UploadModel
        fields = ['name', 'email', 'github']
    name = forms.CharField(max_length=100, label='Your full name')
    email = forms.EmailField(label='Your e-mail address')
    github = forms.URLField(label='Your GitHub profile URL')
    file = forms.FileField(label='Upload your Python file', required=True,
                             widget=forms.FileInput(attrs={'accept': '.py'}))
    consent = forms.BooleanField(label='I consent to having my data stored and processed.')




