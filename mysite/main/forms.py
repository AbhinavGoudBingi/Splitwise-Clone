from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import *
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from django_select2.forms import Select2MultipleWidget
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

class ActivityTransactionForm(forms.ModelForm):
    activity=forms.CharField(label="Enter a description",max_length=200)
    # all_friends_in_activity=forms.ModelMultipleChoiceField(label='Friend ids',queryset=GroupTrans.objects.filter(gpname=))
    money=forms.IntegerField(label='Amount')
    friends_and_money_paid_by_each = forms.CharField(label="Fill the friends and money paid by each")
    TAG_CHOICES = [
        ('Restaurant', 'Restaurant'), ('Cinema', 'Cinema'), ('Travel', 'Travel'), ('Others', 'Others')
    ]
    tag = forms.ChoiceField(label='Tag ', choices=TAG_CHOICES)
    # DISPLAY_CHOICES = (
    #     ("You paid", "You paid"),
    #     ("Paid by friend", "Paid by friend"),
    # )
    # paid = forms.ChoiceField(widget=forms.RadioSelect, choices=DISPLAY_CHOICES)
    SPLIT_CHOICES=(
        ("Split Equally","Split Equally"),
        ("Split Manually","Split Manually"),
    )
    split =forms.ChoiceField(widget=forms.RadioSelect,choices=SPLIT_CHOICES)
    # amount_string=forms.CharField(label='Enter amount each person spent in order by ","')
    amount_string=forms.CharField(label="Fill the friends who spent the money along with how much they spent")
    def clean(self):
        cleaned_data = super(ActivityTransactionForm, self).clean()
        activity=cleaned_data.get('activity')
        # all_friends_in_activity=cleaned_data.get('all_friends_in_activity')
        friends_and_money_paid_by_each=cleaned_data.get('friends_and_money_paid_by_each')
        money=cleaned_data.get('money')
        # l1=friends_and_money_paid_by_each.split(";")
        # l2=[]
        # if split==
        # for ele in l1:
        #     dummy1=ele.split(",")
        #     dummy1[1]=int(dummy1[1])
        #     l2.append(dummy1)
        # s = []
        # split_chosen=cleaned_data.get('split')
        # for i in range(0, len(all_friends_in_activity)):
        #     s.append(money/len(all_friends_in_activity))


    # def splitunequally(self):
    #     n1=self.all_friends_in_activity
    #     a=self.amount_list
    #     l1=[]
    #     if len(a)-len(n1)==1:
    #         sum=0
    #         for num in a:
    #             sum=sum+num
    #         if sum==self.money:
    #             l1.append([currentuser,a[0]])
    #             for i in range(1,len(a)):
    #                 l1.append([n1[i],amount_list[i]])
    #                 return l1
    #         else:
    #             raise forms.ValidationError("Split the money properly")
    #     else:
    #         raise forms.ValidationError("Give money spent for each person")



class GroupForm(forms.Form):
    group=forms.CharField(label='Group Name',max_length=100)
    # friends=forms.ModelMultipleChoiceField(label='Friend ids',queryset=MyUser.objects.all(),widget=Select2MultipleWidget)
    friends=forms.CharField(label='Usernames of people')
    def clean(self):
        cleaned_data = super(GroupForm, self).clean()
        group_name=cleaned_data.get('group')
        friends_list = cleaned_data.get('friends').split(",")
        for friend in friends_list:
            if MyUser.objects.filter(username=friend).exists():
                continue
            else:
                raise forms.ValidationError('{0} is not there in the list of users,try once again.'.format(friend))
        if len(friends_list)==0:
            raise forms.ValidationError("Select a person or follow the guidelines")



class SettleUpGroup(forms.Form):
    users=forms.CharField(label="People to settle")
    def clean(self):
        cleaned_data = super(SettleUpGroup, self).clean()
        users=cleaned_data.get('users')
        users_list=users.split(",")
        for name in users_list:
            if MyUser.objects.filter(username=name).exists():
                continue
            else:
                raise forms.ValidationError('{0} may not be a user,try again.'.format((name)))
        if len(users_list)==0:
            forms.ValidationError("Please fill the form properly")




