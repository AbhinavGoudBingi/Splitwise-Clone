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
    return render(request=request, template_name="main/duplicate.html",
                  context={"ftrans": FriendT.objects.filter(urname=user.username).order_by('time'),
                           "users": MyUser.objects.all})


def thokka(request, name):
    user = MyUser.objects.get(username=request.user)
    return render(request=request, template_name="main/FTlist.html",
                  context={"ftrans": FriendT.objects.filter(urname=user.username, fdname=name).order_by('time'),
                           "users": MyUser.objects.all, "friend": name,
                           "groups": GroupTable.objects.filter(username=user.username)})


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
                user = request.user
                friend = MyUser.objects.get(username=name)
                FriendT.add_friend(user.username, friend.username)
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
            user = request.user
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
            FriendT.add_transaction(user.username, friend, money, notes, tag)
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
        kavali = FriendT.objects.filter(time__lte=end, time__gte=start, urname=user.username).exclude(
            tag="friend_creation")
        atlast = GroupTable.objects.filter(username=user.username)
        mydata = {}
        piedata = {}
        tdata = {}
        ddata = {}
        gdata = {}
        tot = 0
        taken = 0

        for entry in kavali:
            if entry.money > 0:
                if entry.fdname in mydata:
                    mydata[entry.fdname][0] += entry.money
                    tot += entry.money
                else:
                    mydata[entry.fdname] = [entry.money, 0]
                    tot += entry.money
            elif entry.money < 0:
                if entry.fdname in mydata:
                    mydata[entry.fdname][1] -= entry.money
                    tot -= entry.money
                    taken -= entry.money
                else:
                    mydata[entry.fdname] = [0, -entry.money]
                    tot -= entry.money
                    taken -= entry.money

        for entry in atlast:
            if entry.money > 0:
                if entry.gpname in gdata:
                    gdata[entry.gpname][0] += entry.money
                else:
                    gdata[entry.gpname] = [entry.money, 0]
            elif entry.money < 0:
                if entry.gpname in gdata:
                    gdata[entry.gpname][1] -= entry.money
                else:
                    gdata[entry.gpname] = [0, -entry.money]

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
        gcat = list()
        survived_series_data = list()
        not_survived_series_data = list()
        series_data = list()
        not_series_data = list()
        friends = list()
        tags = list()
        timedata = {}
        timedata1 = {}
        time_list = list()

        def get_model_fields(model):
            return FriendT._meta.fields

        with open('history.csv', 'w') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Transaction_id', 'username', 'friendname', 'money', 'description', 'tag', 'date'])
            # write your header first
            for obj in kavali:
                writer.writerow(getattr(obj, field.name) for field in get_model_fields(FriendT))

        data = pd.read_csv('history.csv')
        data_html = data.to_html()

        for entry, mon in mydata.items():
            categories.append(entry)
            survived_series_data.append(mon[0])
            not_survived_series_data.append(mon[1])

        for entry, mon in gdata.items():
            gcat.append(entry)
            series_data.append(mon[0])
            not_series_data.append(mon[1])

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

        survived = {
            'name': 'Lent',
            'data': series_data,
            'color': 'green'
        }

        not_survived = {
            'name': 'Borrowed',
            'data': not_series_data,
            'color': 'red'
        }

        gchart = {
            'chart': {'type': 'bar'},
            'plotOptions': {
                'series': {
                    'stacking': 'normal'
                }
            },
            'title': {'text': 'Lent and Borrowed amounts group wise'},
            'xAxis': {'categories': gcat},
            'series': [survived, not_survived]
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
            'title': {'text': 'Pie chart for expenditure with tags'},
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

        perc = taken * 100 // tot
        dump = json.dumps(chart)
        dump1 = json.dumps(chart1)
        dump2 = json.dumps(chart2)
        dump3 = json.dumps(chart3)
        dumpg = json.dumps(gchart)

        response = render(request=request,
                          template_name="main/insight.html",
                          context={"chart1": dump1, "chart2": dump2, "chart": dump, "chart3": dump3,
                                   'loaded_data': data_html,
                                   "chart4": perc, "gchart": dumpg})

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


def groupslistpage(request):
    user = MyUser.objects.get(username=request.user)
    return render(request=request, template_name="main/groups.html",
                  context={"grouptrans": GroupTrans.objects.filter(username=user.username).values().annotate(
                      netmoney_owed=Sum('money_gave'), netmoney_owes=Sum('money_took')),
                      "current_user": MyUser.objects.get(username=user.username)})


# check grouppage once
def grouppage(request, group_name):
    user = MyUser.objects.get(username=request.user)
    group_members = list()
    values = {}
    gain = []
    loss = []
    query1 = GroupTable.objects.filter(gpname=group_name, username=user.username, checkmember=True)
    for members in query1:
        if members.frname not in group_members:
            group_members.append(members.frname)
    group_members.append(user.username)
    for mem in group_members:
        query = GroupTable.objects.filter(gpname=group_name, username=mem, checkmember=True)
        for entry in query:
            if mem in values:
                values[mem] += entry.money
            else:
                values[mem] = entry.money

    reducedtransc = []
    for x, y in values.items():
        if y > 0:
            gain += [[x, y]]
        elif y < 0:
            loss += [[x, y]]
    gain = sorted(gain, key=lambda x: int(x[1]))
    loss = sorted(loss, key=lambda x: int(x[1]))

    while len(gain) != 0:
        if gain[0][1] > -loss[0][1]:
            reducedtransc += [(gain[0][0], loss[0][0], -loss[0][1])]
            gain[0][1] += loss[0][1]
            loss = loss[1:]
        elif gain[0][1] < -loss[0][1]:
            reducedtransc += [(gain[0][0], loss[0][0], gain[0][1])]
            loss[0][1] += gain[0][1]
            gain = gain[1:]
        else:
            reducedtransc += [(gain[0][0], loss[0][0], gain[0][1])]
            gain = gain[1:]
            loss = loss[1:]

    deal = {}
    for tup in reducedtransc:
        if tup[0] == user.username:
            deal[tup[1]] = tup[2]

    return render(request=request, template_name="main/GTlist.html",
                  context={
                      "gtrans": GroupTrans.objects.filter(gpname=group_name).order_by('time'),
                      "group_members": group_members,
                      "groupname": group_name,
                      "gtable": GroupTable.objects.filter(gpname=group_name, username=user.username).annotate(
                          netmoney=Sum('money')).order_by('time'), "nets": values, "use": deal})


def group_form(request):
    user = request.user
    data = FriendT.objects.filter(urname=user.username)
    friend = list()
    for entry in data:
        if entry.fdname not in friend:
            friend.append(entry.fdname)
    return render(request, "main/new_group.html", context={"friendslist": friend})


def process_group_form(request):
    if request.method == "POST":
        user = request.user
        group = request.POST['name']
        data = FriendT.objects.filter(urname=user.username)
        member_list = list()
        friend = list()
        for entry in data:
            if entry.fdname not in friend:
                friend.append(entry.fdname)
        for key, val in request.POST.items():
            if key in friend:
                member_list.append(key)
        GroupTrans.add_group(user.username, group, member_list)
        member_list.append(user.username)
        for member1 in member_list:
            # member1a=MyUser.objects.get(username=member1)
            for member2 in member_list:
                if member1 != member2:
                    # member2a=MyUser.objects.get(username=member2)
                    # print(member1a.username)
                    GroupTable.add_group(group, member1, member2)
        return redirect("main:userpage")
    return redirect('main:userpage')


def group_transaction_form(request, thisgroup_name):
    user = request.user
    if request.method == "POST":
        form = ActivityTransactionForm(request.POST)
        if form.is_valid():
            # saveform=form.save()
            # print("possible")
            activity_name = form.cleaned_data.get('activity')
            few_users = form.cleaned_data.get('users')
            money = form.cleaned_data.get('money')
            amount_paid = form.cleaned_data.get('friends_and_money_paid_by_each')
            second_dict = {}
            l1 = amount_paid.split(";")
            l2 = []
            split_choice = form.cleaned_data.get('split')
            for ent in l1:
                dummy1 = ent.split(",")
                dummy1[1] = int(dummy1[1])
                l2.append(dummy1)
            for entry in l2:
                key, value = entry[0], entry[1]
                second_dict[key] = value
            splitting_money = []

            if split_choice == "Split Equally":
                for i in range(0, len(few_users)):
                    splitting_money.append([few_users[i], money / len(few_users)])
            else:
                amount_split = form.cleaned_data.get('amount_string')
                splitting_money = splitunequally(user.username, amount_split,
                                                 money)  # current_user amount entered in the end
            first_dict = {}
            for entry in splitting_money:
                key, value = entry[0], entry[1]
                first_dict[key] = value
            all_users = []
            for lis in splitting_money:
                all_users.append(lis[0])
            tag = form.cleaned_data.get('tag')
            list_of_tr = sorting_who_to_give(l2, splitting_money)
            money_dict = {}
            for entry in list_of_tr:
                key, value = entry[0], entry[1:]
                money_dict[key] = value
            for user1 in all_users:
                GroupTrans.add_activity_and_user(thisgroup_name, activity_name, user1, tag, money_dict[user1][0],
                                                 money_dict[user1][1])
            return redirect("main:userpage")
    form = ActivityTransactionForm()
    return render(request, "main/add_activity_form.html", {"form": form})


def ouredirect(request, name):
    data = GroupTrans.objects.filter(gpname=name)
    friend = list()
    for entry in data:
        if entry.username not in friend:
            friend.append(entry.username)
    print(friend)
    return render(request, "main/group_trans.html", context={"frlist": friend, "group_name": name})


def process_group_transaction(request, thisgroup_name):
    user = request.user
    if request.method == "POST":
        activity_name = request.POST['name']
        money = request.POST['money']
        amount_paid = list()
        split_amount = list()
        data = GroupTrans.objects.filter(gpname=thisgroup_name)
        few_users = list()
        second_dict = []
        first_dict = []
        hi = {}
        for entry in data:
            if entry.username not in few_users:
                few_users.append(entry.username)
        for member in few_users:
            if int(request.POST[member]) != 0:
                second_dict += [[member, int(request.POST[member])]]
                GroupTrans.add_activity_and_user(thisgroup_name, activity_name, member, request.POST['Tag'],
                                                 int(request.POST[member]),
                                                 int(request.POST[member + ":new"]))
                # first_dict[member] = int(request.POST[member + ":new"])
                # amount_paid.append([member, int(request.POST[member])])
                # split_amount.append([member, int(request.POST[member + ":new"])])
        for member in few_users:
            tempalp = [x[0] for x in second_dict]
            if int(request.POST[member + ":new"]) < int(request.POST[member]):
                if member in tempalp:
                    second_dict[tempalp.index(member)][1] -= int(request.POST[member + ":new"])
                else:
                    first_dict += [[int(request.POST[member])]]
            elif int(request.POST[member + ":new"]) == int(request.POST[member]):
                second_dict.remove([member, int(request.POST[member])])
            else:
                if member in tempalp:
                    second_dict.remove([member, int(request.POST[member])])
                    first_dict += [[member, int(request.POST[member + ":new"]) - int(request.POST[member])]]
                else:
                    first_dict += [[member, int(request.POST[member + ":new"])]]
            print(first_dict)
            print(tempalp)

        # = sorting_who_to_give(amount_paid, split_amount)
        # money_dict = {}
        transA = []
        first_dict = sorted(first_dict, key=lambda x: x[1])
        first_dict = sorted(first_dict, key=lambda x: x[1])
        while len(first_dict) != 0:
            if second_dict[0][1] > first_dict[0][1]:
                transA += [(second_dict[0][0], first_dict[0][0], first_dict[0][1])]
                second_dict[0][1] -= first_dict[0][1]
                first_dict = first_dict[1:]
            elif second_dict[0][1] < first_dict[0][1]:
                transA += [(second_dict[0][0], first_dict[0][0], second_dict[0][1])]
                first_dict[0][1] -= second_dict[0][1]
                second_dict = second_dict[1:]
            else:
                transA += [(second_dict[0][0], first_dict[0][0], second_dict[0][1])]
                second_dict = second_dict[1:]
                first_dict = first_dict[1:]
        tag = request.POST['Tag']
        # transA list of tuples final Tranactions
        for tup in transA:
            GroupTable.add_rows(thisgroup_name, activity_name, tup[0], tup[1], tup[2])

        return redirect("main:userpage")
    return redirect("main:userpage")


def splitunequally(user, amount_split, money):
    n1 = amount_split(';')
    l2 = []
    sum_others = 0
    for ele in n1:
        dummy1 = ele.split(",")
        dummy1[1] = int(dummy1[1])
        sum_others = sum_others + dummy1[1]
        l2.append(dummy1)

    l2.append([user, money - sum_others])
    # amount_split.append([user.username,money-sum_others])
    return l2


def splitequally(users, money):
    size1 = len(users)
    nearest = int(money / size1)
    l1 = []
    for i in range(0, size1 - 1):
        l1.append([users[i], nearest])
    l1.append([users[i], money - (nearest * size1)])
    return l1


# def group_transaction_form(request,thisgroup_name):
#     if request.method=="POST":
#         form=ActivityTransactionForm(request.POST)
#         if form.is_valid():
#             # saveform=form.save()
#             activity_name = form.cleaned_data.get('activity')
#             money = sorting_who_to_give(form.cleaned_data.get('money'))
#             amount_paid=cleaned_data.get('friends_and_money_paid_by_each')
#             split_choice=cleaned_data.get('split')
#             l1 = amount_paid.split(";")
#             l2 = []
#             if split_choice=="Split Equally":
#                 for ele in l1:
#                     dummy1 = ele.split(",")
#                     dummy1[1] = int(dummy1[1])
#                     l2.append(dummy1)
#             # all_users=form.cleaned_data.get('users')
#             else:
#                 splitting_money=splitunequally(user.username,amount_split,money)
#             all_users=[]
#             for lis in splitting_money:
#                 all_users.append()
#             tag=form.cleaned_data.get('tag')
#             # description=form.cleaned_data.get('Description')
#             for user1 in all_users:
#                 GroupTrans.add_activity_and_user(request.user,thisgroup_name,activity_name,user1,typ,description,money_dict[user1][0],money_dict[user1][1])
#             return redirect("main:userpage")
#         else:
#             return render(request,"main/add_activity_form.html",{"form":form})


# def splitunequally(user,amount_split,money):
#     n1=amount_split(';')
#     l2=[]
#     sum_others=0
#     for ele in n1:
#         dummy1 = ele.split(",")
#         dummy1[1] = int(dummy1[1])
#         sum_others=sum_others+dummy1[1]
#         l2.append(dummy1)

#     l2.append([user,money-sum_others])
#     # amount_split.append([user.username,money-sum_others])
#     return l2
#     n1 = self.all_friends_in_activity
#     a = self.amount_list
#     l1 = []
#     if len(a) - len(n1) == 1:
#         sum = 0
#         for num in a:
#             sum = sum + num
#         if sum == self.money:
#             l1.append([currentuser, a[0]])
#             for i in range(1, len(a)):
#                 l1.append([n1[i], amount_list[i]])
#                 return l1
#         else:
#             raise forms.ValidationError("Split the money properly")
#     else:
#         raise forms.ValidationError("Give money spent for each person")


def settleup_ingroup(request, group_name):
    if request.method == "POST":
        form = SettleUpGroup(request.POST)
        if form.is_valid():
            user = request.user
            # saveform=form.save()
            users = form.cleaned_data.get('users')
            users_list = users.split(",")
            addrow = list()
            for member in users_list:
                l1 = GroupTable.objects.filter(gpname=group_name, username=user.username, frname=member).aggregate(
                    money_give_take=Sum('money'))
                if l1['money_give_take'] != 0:
                    if [group_name, "settle up", user.username, member, -(l1['money_give_take'])] not in addrow:
                        print(addrow)
                        addrow.append([group_name, "settle up", user.username, member, -(l1['money_give_take'])])
                        addrow.append([group_name, "settle up", member, user.username, l1['money_give_take']])
                        GroupTable.add_rows(group_name, "settle up", user.username, member, -(l1['money_give_take']))
                        GroupTable.add_rows(group_name, "settle up", member, user.username, l1['money_give_take'])

                    if l1['money_give_take'] < 0:
                        GroupTrans.add_activity_and_user(group_name, "settle up", user.username, "settle up", 0,
                                                         -(l1['money_give_take']))
                    else:
                        GroupTrans.add_activity_and_user(group_name, "settle up", user.username, "settle up",
                                                         l1['money_give_take'], 0)
                    return redirect("main:userpage")  # check once here
                elif l1['money_give_take'] == 0:
                    return redirect("main:userpage")  # check once here
    form = SettleUpGroup()
    return render(request, "main/settleupgroup.html", {"form": form})


def settleup(request, name):
    user = MyUser.objects.get(username=request.user)
    # l1 = GroupTable.objects.filter(username=user.username, frname=name)
    # addrow = list()
    # for entr in l1:
    #     lt = GroupTable.objects.filter(username=user.username, gpname=entr.gpname, frname=name).aggregate(
    #         money_give_take=Sum('money'))
    #     if lt['money_give_take'] != 0:
    #         if [entr, "settle up", user.username, name, -(lt['money_give_take'])] not in addrow:
    #             addrow.append([entr, "settle up", user.username, name, -(lt['money_give_take'])])
    #             addrow.append([entr, "settle up", name, user.username, lt['money_give_take']])
    #             GroupTable.add_rows(entr, "settle up", user.username, name, -(lt['money_give_take']))
    #             GroupTable.add_rows(entr, "settle up", name, user.username, lt['money_give_take'])
    #         if lt['money_give_take'] < 0:
    #             GroupTrans.add_activity_and_user(entr, "settle up", user.username, "settle up", 0,
    #                                              -(lt['money_give_take']))
    #         else:
    #             GroupTrans.add_activity_and_user(entr, "settle up", user.username, "settle up",
    #                                              lt['money_give_take'], 0)
    #     elif lt['money_give_take'] == 0:
    #         continue

    l2 = FriendT.objects.filter(urname=user.username, fdname=name).aggregate(money_set=Sum('money'))
    for entr in l2:
        if l2['money_set'] != 0:
            FriendT.add_transaction(user, name, -(l2['money_set']), "", "settling up")
            FriendT.add_transaction(name, user, l2['money_set'], "", "settling up")
    return redirect("main:userpage")


#
# def sorting_who_to_give(list1,list2):
#     list3=[]#In this list list3[i][0] should get list3[i][2] money from list3[i][1]
#     size1=len(list1)
#     size2=len(list2)
#     p=0
#     for i in range(0, size1):
#         if list1[i][1] != 0:
#             for j in range(p, size2):
#                 if list1[i][0] != list2[j][0]:
#                     m=list1[i][1]-list2[j][1]
#                     if m>=0:
#                         list[i][1] = m
#                         p = p+1
#                         list3.append([list1[i][0],list1[i][1],m])
#                         break
#                     # else if m==0:
#                     #     list[i][1]=0
#                     #     p++
#                     #     break
#                     else:
#                         list2[i][j]=-m
#                         list1[i][1]=0
#                         list3.append([list1[i][0], list1[i][1], -m])
#                         break
#         # else:
#     return list3


# def leave_delete_group(request,group_name,option):
#     user=request.user
#     val1=GroupTable.objects.filter(gpname=group_name,username=user.username).aggregate(netmoney=Sum('money'))
#     val2=GroupTable.objects.filter(gpname=group_name,frname=user.username).aggregate(netmoney=Sum('money'))
#     if option == "leave":
#         if val1['netmoney'] == 0 and val2['netmoney'] == 0:
#             GroupTable.objects.filter(gpname=group_name,username=user.username).update(checkmember=False)
#             GroupTable.objects.filter(gpname=group_name,frname=user.username).update(checkmember=False)
#             GroupTrans.objects.filter(gpname=group_name,username=user.username).update(checkmember=False)
#             return redirect("main:groupslistpage")
#         else:
#             messages.error(request,"You are not settled yet")
#     elif option == "delete":
#         val3=GroupTable.objects.filter(gpname=group_name).aggregate(netmoney=Sum('money'))
#         if val3 == 0:
#             GroupTable.objects.filter(gpname=group_name).update(checkmember=False)
#             GroupTrans.objects.filter(gpname=group_name).update(checkmember=False)
#             return redirect("main:groupslistpage")
#         else:
#             messages.error(request, "Not everyone is settled")
#     return redirect("main:groupslistpage")


def leave_group(request, group_name):
    user = user = request.user
    val1 = GroupTable.objects.filter(gpname=group_name, username=user.username).aggregate(netmoney=Sum('money'))
    val2 = GroupTable.objects.filter(gpname=group_name, frname=user.username).aggregate(netmoney=Sum('money'))
    if val1['netmoney'] == 0 and val2['netmoney'] == 0:
        GroupTable.objects.filter(gpname=group_name, username=user.username).update(checkmember=False)
        GroupTable.objects.filter(gpname=group_name, frname=user.username).update(checkmember=False)
        GroupTrans.objects.filter(gpname=group_name, username=user.username).update(checkmember=False)
        return redirect("main:groupslistpage")
    else:
        messages.error(request, "You are not settled yet")
    return redirect("main:groupslistpage")


def delete_group(request, group_name):
    val3 = GroupTable.objects.filter(gpname=group_name).aggregate(netmoney=Sum('money'))
    if val3 == 0:
        GroupTable.objects.filter(gpname=group_name).update(checkmember=False)
        GroupTrans.objects.filter(gpname=group_name).update(checkmember=False)
        return redirect("main:groupslistpage")
    else:
        messages.error(request, "Not everyone is settled")
    return redirect("main:groupslistpage")
