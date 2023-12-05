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
    name = models.CharField(max_length=1000, verbose_name='Your full name')
    gender = models.CharField(max_length=9, choices=GENDER_CHOICES, default='SELECT')
    email = models.EmailField(max_length=1000, verbose_name='Your e-mail address')
    github = models.URLField(max_length=1000, verbose_name='Your GitHub profile URL')

    file = forms.FileField(label='Upload your Python file', required=True,
                           widget=forms.FileInput(attrs={'accept': '.py'}))
    consent = forms.BooleanField(label='I consent to having my data stored and processed.')

    pylint_score = models.CharField(max_length=1000, verbose_name='Pylint score', null=True)
    gender_guess = models.CharField(max_length=1000, verbose_name="Gender Guess", null=True)
    gender_guess_proba = models.CharField(max_length=1000, verbose_name="Gender Guess Probability", null=True)
    components = models.CharField(max_length=1000, verbose_name="Components", null=True)

