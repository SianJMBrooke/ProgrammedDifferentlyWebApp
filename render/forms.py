from django import forms


class UploadForm(forms.Form):
    name = forms.CharField(max_length=100, label='Your full name')
    gender = forms.CharField(max_length=20, label='Your gender')
    email = forms.EmailField(label='Your e-mail address')
    github = forms.URLField(label='Your GitHub profile URL')
    file = forms.FileField(label='Upload your Python file', required=True,
                             widget=forms.FileInput(attrs={'accept': '.py'}))
    consent = forms.BooleanField(label='I consent to having my data stored and processed.')




