from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import *
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class MyForm(UserCreationForm):
    class Meta:
        model = MyUser
        fields = ('username', 'first_name', 'image')

    def __init__(self, *args, **kwargs):
        super(MyForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = "User ID"
        self.fields['first_name'].label = "User name"

    # def clean(self):

    # data from the form is fetched using super function
    # super(MyForm, self).clean()

    # extract the username and text field from the data
    # password1 = self.cleaned_data.get('password')
    # password2 = self.cleaned_data.get('passwordcon')

    # conditions to be met for the username length
    # if not(password1 == password2) :
    # raise ValidationError(self.error_messages['password2'], code='password2')
    # if len(text) <10:
    #   self._errors['text'] = self.error_class([
    #      'Post Should Contain minimum 10 characters'])

    # return any errors if found
    # return self.cleaned_data


class MyChangeForm(UserChangeForm):
    class Meta:
        model = MyUser
        fields = ('username', 'first_name', 'image')


class FriendForm(forms.Form):
    name = forms.CharField(label='Friend user id', max_length=100)

    def clean(self):
        cleaned_data = super(FriendForm, self).clean()
        name = cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("I don't think a person exists with no username")


class TransactionForm(forms.Form):
    friend = forms.ModelChoiceField(label='Friend id', queryset=MyUser.objects.all())
    money = forms.IntegerField(label='Amount')
    notes = forms.CharField(label='Description', max_length=250, required=False)
    TAG_CHOICES = [
        ('Restaurant', 'Restaurant'), ('Cinema', 'Cinema'), ('Travel', 'Travel'), ('Others', 'Others')
    ]
    tag = forms.ChoiceField(label='Tag ', choices=TAG_CHOICES)
    DISPLAY_CHOICES = (
        ("You paid", "You paid"),
        ("Paid by friend", "Paid by friend"),
    )
    paid = forms.ChoiceField(widget=forms.RadioSelect, choices=DISPLAY_CHOICES)
    split = forms.BooleanField(label='Split by amounts', required=False)
    ys = forms.IntegerField(label='Money paid by you', required=False)
    fs = forms.IntegerField(label='Money paid by friend', required=False)

    def clean(self):
        cleaned_data = super(TransactionForm, self).clean()
        friend = cleaned_data.get('friend')
        money = cleaned_data.get('money')
        tag = cleaned_data.get('tag')
        ys = cleaned_data.get('ys')
        fs = cleaned_data.get('fs')
        split = cleaned_data.get('split')

        if not(money and friend and tag):
            raise forms.ValidationError("Please don't waste your time by not filling the form properly")

        if split:
            if not(ys and fs) or not (money == ys+fs):
                raise forms.ValidationError("Enter the amounts")
        else:
            if ys or fs:
                raise forms.ValidationError("Select split using amounts for individual amounts")





