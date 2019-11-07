from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import Tutorial
from django.contrib.auth.forms import UserCreationForm , AuthenticationForm , PasswordChangeForm
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required

# Create your views here.
def homepage(request):
    return render(request = request,template_name="main/home.html",
        context={"tutorials": Tutorial.objects.all})

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username=form.cleaned_data.get('username')
            messages.success(request,f"New Account Created : {username}")
            login(request,user)
            messages.info(request,f"You are logged in as : {username}")
            return redirect("main:homepage")

        else:
            for msg in form.error_messages:
                messages.error(request,f"{msg}: {form.error_messages[msg]}")


    form = UserCreationForm
    return render(request,
                "main/register.html",
                context={"form":form})

def logout_request(request):
    logout(request)
    messages.info(request,"Logged out successfully!")
    return redirect("main:homepage")

def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request,data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username,password=password)
            if user is not None:
                login(request,user)
                messages.info(request,f"You are logged in as : {username}")
                return redirect("main:homepage")
            else:
                messages.error(request,"Invalid username or password")
        else:
            messages.error(request,"Invalid username or password")
    form = AuthenticationForm()
    return render(request,
                "main/login.html",
                {"form":form})

@login_required
def account(request):from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import Tutorial
from django.contrib.auth.forms import UserCreationForm , AuthenticationForm , PasswordChangeForm
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash

# Create your views here.
def homepage(request):
    return render(request = request,template_name="main/home.html",
        context={"tutorials": Tutorial.objects.all})

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username=form.cleaned_data.get('username')
            messages.success(request,f"New Account Created : {username}")
            login(request,user)
            messages.info(request,f"You are logged in as : {username}")
            return redirect("main:homepage")

        else:
            for msg in form.error_messages:
                messages.error(request,f"{msg}: {form.error_messages[msg]}")


    form = UserCreationForm
    return render(request,
                "main/register.html",
                context={"form":form})

def logout_request(request):
    logout(request)
    messages.info(request,"Logged out successfully!")
    return redirect("main:homepage")

def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request,data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username,password=password)
            if user is not None:
                login(request,user)
                messages.info(request,f"You are logged in as : {username}")
                return redirect("main:homepage")
            else:
                messages.error(request,"Invalid username or password")
        else:
            messages.error(request,"Invalid username or password")
    form = AuthenticationForm()
    return render(request,
                "main/login.html",
                {"form":form})

def account(request):
    if request.method == 'POST':
        form = PasswordChangeForm( data=request.POST, user=request.user)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect("main:homepage")

        else:
            for msg in form.error_messages:
                messages.error(request,f"{msg}: {form.error_messages[msg]}")


    form = PasswordChangeForm(request.user)
    return render(request,
                "main/account.html",
                context={"form":form})



    if request.method == 'POST':
        form = PasswordChangeForm( data=request.POST, user=request.user)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, form.user)
            return redirect("main:homepage")

        else:
            for msg in form.error_messages:
                messages.error(request,f"{msg}: {form.error_messages[msg]}")


    form = PasswordChangeForm(request.user)
    return render(request,
                "main/account.html",
                context={"form":form})

