import json
import datetime

import pandas as pd
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.db.models import *
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db.models import Func, F
import csv

from .forms import *
from .models import *


# Create your views here.
def homepage(request):
    return render(request=request, template_name="main/home.html")


def userpage(request):
    user = MyUser.objects.get(username=request.user)
    return render(request=request, template_name="main/user.html",
                  context={"friendtrans": FriendT.objects.filter(urname=user.username).values('fdname').annotate(
                      netmoney=Sum('money')), "users": MyUser.objects.all})


def friendspage(request):
    user = MyUser.objects.get(username=request.user)
    return render(request=request, template_name="main/friends.html",
                  context={"friendtrans": FriendT.objects.filter(urname=user.username).values('fdname').annotate(
                      netmoney=Sum('money')), "users": MyUser.objects.all})


def flist(request):
    user = MyUser.objects.get(username=request.user)
    return render(request=request, template_name="main/FTlist.html",
                  context={"ftrans": FriendT.objects.filter(urname=user.username).order_by('time'),
                           "users": MyUser.objects.all})


def thokka(request, name):
    user = MyUser.objects.get(username=request.user)
    return render(request=request, template_name="main/FTlist.html",
                  context={"ftrans": FriendT.objects.filter(urname=user.username, fdname=name).order_by('time'),
                           "users": MyUser.objects.all})


def register(request):
    if request.method == "POST":
        form = MyForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"New Account Created : {username}")
            # login(request,user)
            # messages.info(request,f"You are logged in as : {username}")
            return redirect("main:homepage")

        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")

    form = MyForm
    return render(request,
                  "main/input.html",
                  context={"form": form})


def logout_request(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("main:homepage")


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are logged in as : {username}")
                return redirect("main:userpage")
            else:
                messages.error(request, "Invalid username or password")
        else:
            messages.error(request, "Invalid username or password")
    form = AuthenticationForm()
    return render(request,
                  "main/login.html",
                  {"form": form})


def account(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect("main:homepage")

        else:
            for msg in form.error_messages:
                messages.error(request, f"{msg}: {form.error_messages[msg]}")

    form = PasswordChangeForm(request.user)
    return render(request,
                  "main/account.html",
                  context={"form": form})


def get_user_profile(request):
    return render(request, 'main/user_profile.html')


def friends_form(request):
    if request.method == "POST":
        form = FriendForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data.get('name')
            try:
                friend = MyUser.objects.get(username=name)
                FriendT.add_friend(request.user, friend)
                return redirect("main:userpage")
            except MyUser.DoesNotExist:
                messages.error(request, "User doesn't exist")
        else:
            messages.error(request, "Invalid username")
    form = FriendForm()
    return render(request,
                  "main/add_friend.html",
                  {"form": form})


def transaction_form(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            friend = form.cleaned_data.get('friend')
            money = form.cleaned_data.get('money')
            notes = form.cleaned_data.get('notes')
            tag = form.cleaned_data.get('tag')
            display_type = request.POST['paid']
            split_type = form.cleaned_data.get('split')
            ys = form.cleaned_data.get('ys')
            fs = form.cleaned_data.get('fs')
            if display_type == "You paid":
                if split_type:
                    if form.data['fs'] and form.data['ys']:
                        money = fs
                    else:
                        messages.error(request, "Specify the amounts")
                else:
                    if form.data['ys'] or form.data['fs']:
                        messages.error(request, "Please select Split by amounts if you want to specify amounts")
                    else:
                        money = money / 2
            elif display_type == "Paid by friend":
                if split_type:
                    if form.data['fs'] and form.data['ys']:
                        money = -ys
                    else:
                        messages.error(request, "Specify the amounts")
                else:
                    if form.data['ys'] or form.data['fs']:
                        messages.error(request, "Please select Split by amounts if you want to specify amounts")
                    else:
                        money = -money / 2
            FriendT.add_transaction(request.user, friend, money, notes, tag)
            return redirect("main:userpage")
        else:
            messages.error(request, "Invalid Friend")
    form = TransactionForm()
    return render(request,
                  "main/trans.html",
                  {"form": form})


def insight(request):
    if request.method == "POST":
        start = datetime.strptime(request.POST['start'], '%Y-%m-%d').strftime('%x')
        end = datetime.strptime(request.POST['end'], '%Y-%m-%d').strftime('%x')
        user = MyUser.objects.get(username=request.user)
        kavali = FriendT.objects.filter(time__lte=end, time__gte=start, urname=user.username).exclude(tag="friend_creation")
        mydata = {}
        piedata = {}
        tdata = {}
        ddata = {}

        for entry in kavali:
            if entry.money > 0:
                if entry.fdname in mydata:
                    mydata[entry.fdname][0] += entry.money
                else:
                    mydata[entry.fdname] = [entry.money, 0]
            elif entry.money < 0:
                if entry.fdname in mydata:
                    mydata[entry.fdname][1] -= entry.money
                else:
                    mydata[entry.fdname] = [0, -entry.money]

        for entry in kavali:
            if entry.fdname in piedata:
                piedata[entry.fdname] += abs(entry.money)
            else:
                piedata[entry.fdname] = abs(entry.money)

        for entry in kavali:
            if entry.tag in tdata:
                if not (entry.tag == "friend_creation"):
                    tdata[entry.tag] += abs(entry.money)
            else:
                if not (entry.tag == "friend_creation"):
                    tdata[entry.tag] = abs(entry.money)

        for entry in kavali:
            if entry.tag in ddata:
                if not (entry.tag == "friend_creation"):
                    if entry.time in ddata[entry.tag]:
                        ddata[entry.tag][entry.time] += entry.money
                    else:
                        ddata[entry.tag][entry.time] = entry.money
            else:
                if not (entry.tag == "friend_creation"):
                    ddata[entry.tag] = {entry.time: entry.money}

        categories = list()
        categories1 = list()
        categories2 = list()
        survived_series_data = list()
        not_survived_series_data = list()
        friends = list()
        tags = list()
        timedata = {}
        timedata1 = {}
        time_list = list()

        def get_model_fields(model):
            return FriendT._meta.fields

        with open('history.html', 'w') as csvfile:
            writer = csv.writer(csvfile)
            # write your header first
            for obj in kavali:
                writer.writerow(getattr(obj, field.name) for field in get_model_fields(FriendT))

        for entry, mon in mydata.items():
            categories.append(entry)
            survived_series_data.append(mon[0])
            not_survived_series_data.append(mon[1])

        for entry, mon in piedata.items():
            categories1.append(entry)
            friends.append(mon)

        for entry, mon in tdata.items():
            categories2.append(entry)
            tags.append(mon)

        for entry, mon in ddata.items():
            for pi, val in ddata[entry].items():
                if entry in timedata:
                    time_list.append(pi)
                    timedata1[entry].append(val)
                else:
                    time_list.append(pi)
                    timedata1[entry] = [val]

        if not ("Restaurant" in timedata1):
            timedata1["Restaurant"] = [0]
        if not ("Cinema" in timedata1):
            timedata1["Cinema"] = [0]
        if not ("Travel" in timedata1):
            timedata1["Travel"] = [0]
        if not ("Others" in timedata1):
            timedata1["Others"] = [0]

        survived_series = {
            'name': 'Lent',
            'data': survived_series_data,
            'color': 'green'
        }

        not_survived_series = {
            'name': 'Borrowed',
            'data': not_survived_series_data,
            'color': 'red'
        }

        chart = {
            'chart': {'type': 'bar'},
            'plotOptions': {
                'series': {
                    'stacking': 'normal'
                }
            },
            'title': {'text': 'Lent and Borrowed amounts friends wise'},
            'xAxis': {'categories': categories},
            'series': [survived_series, not_survived_series]
        }

        chart1 = {
            'chart': {'type': 'pie'},
            'title': {'text': 'Pie chart for expenditure among friends'},
            'series': [{
                'name': 'Total Transaction Amount',
                'data': list(map(lambda row1, row2: {'name': row1, 'y': row2}, categories1, friends))
            }]
        }

        chart2 = {
            'chart': {'type': 'area'},
            'title': {'text': 'Time series plot for expenditure in different areas'},
            'xAxis': {
                'categories': time_list
            },
            'series': [{
                'name': 'Money spent on Restaurants',
                'data': timedata1["Restaurant"]
            }, {
                'name': 'Money spent on Cinemas',
                'data': timedata1["Cinema"]
            }, {
                'name': 'Money spent on Travels',
                'data': timedata1["Travel"]
            }, {
                'name': 'Miscellaneous Transactions',
                'data': timedata1["Others"]
            }]
        }

        chart3 = {
            'chart': {'type': 'pie'},
            'title': {'text': 'Pie chart for expenditure in different areas'},
            'series': [{
                'name': 'Total Transaction Amount',
                'data': list(map(lambda row1, row2: {'name': row1, 'y': row2}, categories2, tags))
            }]
        }

        dump = json.dumps(chart)
        dump1 = json.dumps(chart1)
        dump2 = json.dumps(chart2)
        dump3 = json.dumps(chart3)

        response = render(request=request,
                          template_name="main/insight.html",
                          context={"chart1": dump1, "chart2": dump2, "chart": dump, "chart3": dump3})

    return response
    # return "%s?%s?%s" % (redirect('insight', args=(start, end,)))

# @login_required(login_url='login_request')
# def insight(request, start, end):
#     # start = datetime.strptime(request.POST['start'], '%Y-%m-%d').strftime('%m/%d/%y')
#     # end = datetime.strptime(request.POST['end'], '%Y-%m-%d').strftime('%m/%d/%y')
#     user = MyUser.objects.get(username=request.user)
#     data = FriendT.objects.filter(urname=user.username)
#     mydata = {}
#     for entry in data:
#         if entry.money > 0:
#             if entry.fdname in mydata:
#                 mydata[entry.fdname][0] += entry.money
#             else:
#                 mydata[entry.fdname] = [entry.money, 0]
#         elif entry.money < 0:
#             if entry.fdname in mydata:
#                 mydata[entry.fdname][1] -= entry.money
#             else:
#                 mydata[entry.fdname] = [0, -entry.money]
#
#     print(mydata)
#
#     categories = list()
#     survived_series_data = list()
#     not_survived_series_data = list()
#
#     for entry, mon in mydata.items():
#         categories.append(entry)
#         survived_series_data.append(mon[0])
#         not_survived_series_data.append(mon[1])
#
#     survived_series = {
#         'name': 'Lent',
#         'data': survived_series_data,
#         'color': 'green'
#     }
#
#     not_survived_series = {
#         'name': 'Borrowed',
#         'data': not_survived_series_data,
#         'color': 'red'
#     }
#
#     chart = {
#         'chart': {'type': 'column'},
#         'title': {'text': 'Lent and Borrowed amounts friends wise'},
#         'xAxis': {'categories': categories},
#         'series': [survived_series, not_survived_series]
#     }
#
#     dump = json.dumps(chart)
#
#     return render(request,
#                   "main/insight.html",
#                   context={"chart": dump})
