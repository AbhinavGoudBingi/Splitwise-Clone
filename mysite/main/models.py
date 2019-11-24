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
