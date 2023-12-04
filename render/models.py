from django.db import models
from django import forms

GENDER_CHOICES = (
    ("SELECT", "Please Choose"),
    ("WOMAN", "Woman"),
    ("MAN", "Man"),
    ("NONBINARY", "Non-binary"),
    ("FLUID", "Gender Fluid"),
    ("TRANS", "Transgender"),
    ("NOTSAY", "Prefer not to say")
)


class UploadModel(models.Model):
    name = models.CharField(max_length=100, verbose_name='Your full name')
    gender = models.CharField(max_length=9, choices=GENDER_CHOICES, default='SELECT')
    email = models.EmailField(verbose_name='Your e-mail address')
    github = models.URLField(verbose_name='Your GitHub profile URL')
    file = forms.FileField(label='Upload your Python file', required=True,
                           widget=forms.FileInput(attrs={'accept': '.py'}))
    consent = forms.BooleanField(label='I consent to having my data stored and processed.')
    pylint_score = None

