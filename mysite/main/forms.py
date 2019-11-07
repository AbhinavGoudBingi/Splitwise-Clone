from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import models
from .models import Tutorial
from django.contrib.auth.models import AbstractUser

from django import forms 
from .models import *
  
class Form(forms.ModelForm): 
  
    class Meta: 
        model = Tutorial 
        fields = ['name', 'description','fig'] 