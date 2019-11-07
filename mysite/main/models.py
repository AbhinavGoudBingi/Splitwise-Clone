from django.db import models
from datetime import datetime
from django.conf import settings
from django.db.models.signals import post_save
from django.contrib.auth.models import User

# Create your models here.
class Tutorial(models.Model):
    name = models.CharField(max_length = 25)
    description = models.CharField(max_length=25,unique=True)
    fig = models.ImageField(upload_to='images/',blank=True,null=True)

    USERNAME_FIELD = 'description'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.name

def create_profile(sender,**kwargs):
    if kwargs['created']:
        user_profile = Tutorial.objects.create(user=kwargs['instance'])

post_save.connect(create_profile,sender=User)

