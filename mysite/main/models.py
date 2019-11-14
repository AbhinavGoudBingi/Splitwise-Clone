from django.db import models
from datetime import datetime
from django.conf import settings
from django.contrib.auth.models import AbstractUser 
# Create your models here.
class Tutorial(models.Model):
	name = models.CharField(max_length = 25)
	description = models.TextField()
	fig = models.ImageField(blank=True,null=True);
	Date  = models.DateTimeField("date published", default=datetime.now())

	def __str__(self):
		return self.name

class MyUser(AbstractUser):
    image = models.FileField()
    pass

    def __str__(self):
        return self.username

