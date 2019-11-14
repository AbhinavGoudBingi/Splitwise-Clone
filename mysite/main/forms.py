from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import MyUser
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

class MyForm(UserCreationForm):
    class Meta:
        model = MyUser
        fields = ('username','first_name','image')

        #def clean(self): 
  
        # data from the form is fetched using super function 
            #super(MyForm, self).clean() 
          
        # extract the username and text field from the data 
            #password1 = self.cleaned_data.get('password')
            #password2 = self.cleaned_data.get('passwordcon')
  
        # conditions to be met for the username length 
            #if not(password1 == password2) : 
                #raise ValidationError(self.error_messages['password2'], code='password2')
        #if len(text) <10: 
         #   self._errors['text'] = self.error_class([ 
          #      'Post Should Contain minimum 10 characters']) 
  
        # return any errors if found 
            #return self.cleaned_data

class MyChangeForm(UserChangeForm):
    class Meta:
        model = MyUser
        fields = ('username','first_name','image')