from django.db import models
from django import forms


class UploadModel(models.Model):
    name = models.CharField(max_length=100, verbose_name='Your full name')
    email = models.EmailField(verbose_name='Your e-mail address')
    github = models.URLField(verbose_name='Your GitHub profile URL')

