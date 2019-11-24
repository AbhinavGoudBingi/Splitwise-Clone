from django.db import models
from datetime import datetime
from django.contrib.auth.models import AbstractUser


# Create your models here.

class MyUser(AbstractUser):
    image = models.FileField(default="default.png")
    pass

    def __str__(self):
        return self.username


class FriendT(models.Model):
    urname = models.CharField(max_length=25, default=None)
    fdname = models.CharField(max_length=25, default=None)
    money = models.IntegerField()
    description = models.TextField()
    tag = models.CharField(max_length=25)
    time = models.CharField(default=datetime.now().strftime('%x'), max_length=25)

    @classmethod
    def add_friend(cls, current_user, new_friend):
        friend = cls.objects.get_or_create(
            urname=current_user.username,
            fdname=new_friend.username,
            money=0,
            description="",
            tag="friend_creation"
        )

        revfriend = cls.objects.get_or_create(
            urname=new_friend.username,
            fdname=current_user.username,
            money=0,
            description="",
            tag="friend_creation"
        )

    @classmethod
    def add_transaction(cls, current_user, friend, money, notes, tag):
        transaction = cls.objects.get_or_create(
            urname=current_user.username,
            fdname=friend,
            money=money,
            description=notes,
            tag=tag
        )

        revtransaction = cls.objects.get_or_create(
            urname=friend,
            fdname=current_user,
            money=(-money),
            description=notes,
            tag=tag
        )


class GroupTable(models.Model):
    gpname = models.CharField(max_length=200, default=None)
    activityname=models.CharField(max_length=200,default=None)
    username = models.CharField(max_length=25,default=None)
    frname = models.CharField(max_length=25,default=None)
    money = models.IntegerField()
    time = models.CharField(default=datetime.now().strftime('%x'), max_length=25)
    @classmethod
    def add_group(cls, group_name, user_name, friend_name):
        group1 = cls.objects.get_or_create(
            gpname=group_name,
            username=user_name,
            activityname="group creation",
            frname=friend_name,
            money=0,
        )
        reverse_group1 = cls.objects.get_or_create(
            gpname=group_name,
            username=friend_name,
            activityname="group creation",
            frname=user_name,
            money=0,
        )

    @classmethod
    def add_rows(cls, group_name,activity_name,user_name,friend_name,money1):
        group1 = cls.objects.create(
            gpname=group_name,
            activityname=activity_name,
            username=user_name,
            frname=friend_name,
            money=int(money1),
        )
        revgroup1=cls.objects.create(
            gpname=group_name,
            activityname=activity_name,
            username=friend_name,
            frname=user_name,
            money=-(int(money1)),
        )
    # @classmethod
    # def forsettleup(cls,group_name,user_name,friend_name):




class GroupTrans(models.Model):
    gpname = models.CharField(max_length=200,default=None)
    activityname = models.CharField(max_length=200)
    username = models.CharField(max_length=25,default=None)
    money_gave = models.IntegerField()
    money_took = models.IntegerField()
    tag=models.CharField(max_length=50)
    # description = models.TextField()
    time = models.CharField(default=datetime.now().strftime('%x'), max_length=25)

    @classmethod
    def add_group(cls, current_user, group_name, friends):
        group = cls.objects.get_or_create(
            gpname=group_name,
            activityname="",
            username=current_user,
            money_took=0,
            money_gave=0,
            tag = "group_creation",
            # description = notes,
            )

        for all_users in friends:
            group=cls.objects.get_or_create(
                gpname=group_name,
                activityname="",
                username=all_users,
                money_took = 0,
                money_gave = 0,
                tag="group_creation",
                # description=notes,
                )

    @classmethod
    def add_activity_and_user(cls,group_name,activity_name,user,tagging,money_owed,money_owes):
        activity_add=cls.objects.get_or_create(
            gpname=group_name,
            activityname=activity_name,#if activity_name=="settle up",then settle between the friends
            username=user,
            tag=tagging,
            description=descriptions,
            money_gave=int(money_owed),
            money_took=int(money_owes),
            time=models.DateTimeField(default=timezone.now()))
    # @classmethod
    # def add_transaction(cls,group_name,current_user,friend,notes,money):
    #     transaction_add = cls.objects.get_or_create(
    #         gpname=group_name,
    #         activityname="",
    #         username=current_user,
    #         money_gave=money,
    #         money_took=0,
    #         description=notes,
    #         tag="to friend",
    #         time=models.DateTimeField(default=timezone.now()))
    #
    #     reverse_transaction_add = cls.objects.get_or_create(
    #         gpname=group_name,
    #         activityname="",
    #         username=friend,
    #         money_gave=0,
    #         money_took=money,
    #         description=notes,
    #         tag="from friend",
    #         time=models.DateTimeField(default=timezone.now()))
