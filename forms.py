# -*- coding: utf-8 -*-

from django import forms

class TitleForm(forms.Form):
    title = forms.CharField(label='Тема', required=False) 

class WordForm(forms.Form):
    word1 = forms.CharField(label='1', required=False)    
    word2 = forms.CharField(label='2', required=False)    
    word3 = forms.CharField(label='3', required=False)    
    word4 = forms.CharField(label='4', required=False)    
    word5 = forms.CharField(label='5', required=False)    
    word6 = forms.CharField(label='6', required=False)    
    word7 = forms.CharField(label='7', required=False)    
    word8 = forms.CharField(label='8', required=False)    
    word9 = forms.CharField(label='9', required=False)    
    word10 = forms.CharField(label='10', required=False)  
    
class ContactForm(forms.Form):
    word1 = forms.CharField(label='1', required=False)    
    word2 = forms.CharField(label='2', required=False)    
    word3 = forms.CharField(label='3', required=False)    
    word4 = forms.CharField(label='4', required=False)    
    word5 = forms.CharField(label='5', required=False)    
    word6 = forms.CharField(label='6', required=False)    
    word7 = forms.CharField(label='7', required=False)    
    word8 = forms.CharField(label='8', required=False)    
    word9 = forms.CharField(label='9', required=False)    
    word10 = forms.CharField(label='10', required=False)  
    
class RegisterForm(forms.Form):
    username = forms.CharField(label='Логин')
    email = forms.CharField(label='Почта')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    first_name = forms.CharField(label='Имя')
    last_name = forms.CharField(label='Фамилия')

class UserProfileForm(forms.Form):
    first_name = forms.CharField(label='Имя', required=True)
    last_name = forms.CharField(label='Фамилия', required=True)
    new_password = forms.CharField(label='Новый пароль', widget=forms.PasswordInput,
        help_text="Заполните, чтобы поменять пароль, или оставьте поле пустым", required=False)
    new_password_repeated = forms.CharField(label='Новый пароль ещё раз', widget=forms.PasswordInput, required=False)

class CreateForm(forms.Form):
    startYear = forms.IntegerField(label = 'Время старта:год', required=True)
    startMonth = forms.IntegerField(label = 'Время старта:месяц', required=True)
    startDay = forms.IntegerField(label = 'Время старта:день', required=True)
    startHour = forms.IntegerField(label = 'Время старта:часы', required=True)
    startMinute = forms.IntegerField(label = 'Время старта:минуты', required=True)

    toursNumber = forms.IntegerField(label = 'Количество туров', required=True)
    lenWriteWords = forms.IntegerField(label = 'Время на написание слов', required=True)
    lenWatchResult = forms.IntegerField(label = 'Время на просмотр результатов', required=True)
    lenChecking = forms.IntegerField(label = 'Время на редакруту', required=True)
    lenWaitWords = forms.IntegerField(label = 'Время на ожидание слов(~5 секунд)', required=True)

    info = forms.IntegerField(label = 'Показать информацию об игре за (минуты)', required=True)