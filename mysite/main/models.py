from django.db import models
from datetime import datetime
from django.conf import settings
# Create your models here.
class Tutorial(models.Model):
	name = models.CharField(max_length = 25)
	description = models.TextField()
	fig = models.ImageField(blank=True,null=True);
	Date  = models.DateTimeField("date published", default=datetime.now())

	def __str__(self):
		return self.name

