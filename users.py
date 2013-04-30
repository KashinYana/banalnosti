# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from forms import ContactForm, RegisterForm, UserProfileForm
from words.models import Player, CurrentGame
from django.contrib.auth.models import User
import time


from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.contrib import auth
from django.contrib.auth.views import logout, login

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            if User.objects.filter(username=username):
                error = u'Пользователь с таким логином уже существует'
                return render_to_response("registration/register.html", {'form': form , 'error' : error})

            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']

            user = User.objects.create_user(username, email, password=password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            return render_to_response('base_profile.html', {'info': 'Вы успешно зарегистрированы. Можете войти.'})
    else:
        form = RegisterForm()
    return render_to_response("registration/register.html", { 'form': form, })

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            return HttpResponseRedirect('/home/')
        else:
            return render_to_response("registration/login.html", {'errors' : "true"})    
    else:
        return render_to_response("registration/login.html")

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/home/")

def profile(request):
    errors = []
    messages = []
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if data['new_password']:
                if data['new_password'] != data['new_password_repeated']:
                    errors.append('Новый пароль повторен неправильно')
                else:
                    request.user.set_password(data['new_password'])
                    messages.append('Пароль успешно изменен')
            if data['first_name'] and data['last_name']:
                request.user.first_name = data['first_name']
                request.user.last_name = data['last_name']
            else:
                errors.append('Имя и фамилия не могут быть пустыми')
            request.user.save()
    else:
        form = UserProfileForm(dict(first_name=request.user.first_name, last_name=request.user.last_name))
    return render_to_response('registration/profile.html', locals())

