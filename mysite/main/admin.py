from django.contrib import admin

# Register your models here.
from .models import Tutorial
from tinymce.widgets import TinyMCE
from django.db import models

class TutorialAdmin(admin.ModelAdmin):
	#fields = ["name","description","Date"]
	fieldsets=[
	("Title/date",{"fields":["name","Date"]}),
	("Content",{"fields":["description"]})
	]

	formfield_overrides = {
	models.TextField: {'widget': TinyMCE()}
	}

admin.site.register(Tutorial,TutorialAdmin);