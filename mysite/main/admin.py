from django.contrib import admin

# Register your models here.
from .models import *
from tinymce.widgets import TinyMCE
from django.db import models
from .forms import *
from django.contrib.auth.admin import UserAdmin

class TutorialAdmin(admin.ModelAdmin):
	#fields = ["name","description","Date"]
	fieldsets=[
	("Title/date",{"fields":["name","Date"]}),
	("Content",{"fields":["description"]})
	]

	formfield_overrides = {
	models.TextField: {'widget': TinyMCE()}
	}

class CustomUserAdmin(UserAdmin):
    add_form = MyForm
    form = MyChangeForm
    model = MyUser

admin.site.register(MyUser, CustomUserAdmin)

admin.site.register(Tutorial,TutorialAdmin);
