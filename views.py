# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from forms import ContactForm, TitleForm
from generalSettings.models import Settings
from words.models import Player, CurrentGame
from statistics.models import PointTour
from versionTitles.models import VersionTitles
from django.contrib.auth.models import User
import time
import random
import threading
from lockfile import FileLock


def need_login_and_enter(function):
    #@functools.wraps(function)
    def need_login_wrapper(*args, **kwargs):
        request = args[0]
        if not request.user.is_authenticated():
            return render_to_response('not_login.html', locals())
        temp = request.user.username
        if len(Player.objects.filter(name = temp)) == 0:
            return render_to_response('not_login.html', locals())
        return function(*args, **kwargs)
    return need_login_wrapper

def need_login(function):
    #@functools.wraps(function)
    def need_login_wrapper(*args, **kwargs):
        request = args[0]
        if not request.user.is_authenticated():
            return render_to_response('not_login.html', locals())
        return function(*args, **kwargs)
    return need_login_wrapper


def settings(name):
    return Settings.objects.get(name = name).valueInt

def settingsString(name):
    return Settings.objects.get(name = name).valueString

def settingsNUM_TOUR() :
    return settings('NUM_TOURS')

def length_game():
    return settings('SEGMENT_GAME') + settings('SEGMENT_WAITING') + settings('WATCHING_RESULT')

def time_start():
    return settings('START_HOURS')*60*60 + settings('START_MIN')*60 + settings('START_SEC')

def cur_time():
    curTime = time.localtime()
    return curTime.tm_hour*60*60 + curTime.tm_min*60 + curTime.tm_sec

def comparatorTitles(x, y):
    return (x.point > y.point) or (x.point == y.point and (x.user.username < y.user.username))

def choice_titles(id_tour, name):
    #lockChoceTitles.acquire()
    print u"in titles " + name 
    try:
        if(settingsString('TITLE').count(',') >= id_tour + 1):
            time.sleep(0.5)
            return
        while settingsString('TITLE').count(',') < id_tour:
            lastTitles = settingsString('TITLE')
            Settings.objects.filter(name = 'TITLE').update(valueString = lastTitles + "empty title,")       
        if(id_tour > 0):
            list_players = PointTour.objects.filter(id_tour = id_tour - 1)
            list_players = sorted(list_players, cmp = comparatorTitles)
            for i in range(len(list_players)):
                if len(VersionTitles.objects.filter(user = list_players[i].user, mark = 0)) > 0 :
                    newTitle = VersionTitles.objects.get(user = list_players[i].user).title
                    lastTitles = settingsString('TITLE')
                    if(lastTitles.count(',') < id_tour + 1):
                        lastTitles +=  newTitle + u" (автор темы: " + list_players[i].user.first_name + " " + list_players[i].user.last_name + u"),"
                    Settings.objects.filter(name = 'TITLE').update(valueString = lastTitles)
                    time.sleep(0.5)
                    VersionTitles.objects.filter(user = list_players[i].user, mark = 0).update(mark = 1)
                    return
        adminTitles = settingsString('ADMIN_TITLES').split(',')
        lastTitles = settingsString('TITLE')
        if(lastTitles.count(',') < id_tour + 1):
            lastTitles += adminTitles[id_tour] + u" (автор темы: робот),"
        Settings.objects.filter(name = 'TITLE').update(valueString = lastTitles)
        time.sleep(0.5)
    finally:
        print u"out titles " + name
        #if lockChoceTitles.locked():
        #    lockChoceTitles.release()

def is_watch_game():
    return settings('WATCH_GAME')

def rules(request):
    return render_to_response('rules.html', locals())

def history(request):
    return render_to_response('history.html', locals())
    
def home(request):
    id_tour = (cur_time() - time_start())/(length_game())
    if is_watch_game() != 1 or id_tour >= settingsNUM_TOUR():
        standings = []
        allPlayers = Player.objects.all()
        for player in allPlayers:
            name_player = User.objects.get(username=player.name).first_name + " " + User.objects.get(username=player.name).last_name
            standings.append([name_player, player.point])
        standings.sort(key = lambda element: element[1], reverse = True)
        return render_to_response('during_game.html', locals())

    if id_tour < 0:
        time = time_start() - settings('CLOSE_REG') #регистрация заканчивается раньше
        NUMBER_SEC_REDIRECT = time - cur_time()
        return render_to_response('home.html', dict({'message': "До начала игры осталось", 'NEXT_PAGE': '/home/'}, **locals() ))
    elif id_tour < settingsNUM_TOUR():
        return render_to_response('try_to_entry.html', dict({'message': "Игра началась. Сейчас идет " + str(id_tour + 1) + " из " + str(settingsNUM_TOUR())+  " туров. Но Вы все равно можете присоединиться."}, **locals() ) )


@need_login
def start(request):
    id_tour = (cur_time() - time_start()) / (length_game())
    time = time_start()
    temp = request.user.username
    formTitle = TitleForm()
    isTitle = False
    if request.method == 'POST':
        formTitle = TitleForm(request.POST)
        if len(Player.objects.filter(name = temp)) == 0:
            player = Player(name = request.user.username, point = 0)
            player.save()
        if  formTitle.is_valid():
            inputTitle = formTitle.cleaned_data['title'].split() 
            if(len(inputTitle) > 0):
                VersionTitles.objects.filter(user = request.user).delete()
                isTitle = formTitle.cleaned_data['title']
                title = VersionTitles(user = request.user, title = formTitle.cleaned_data['title'], mark = 0)
                title.save()
    list_player = Player.objects.all()
    namePlayers = []
    for player in list_player:
        namePlayers.append(User.objects.get(username = player.name).first_name + " " + User.objects.get(username=player.name).last_name)
    NUMBER_SEC_REDIRECT = time - cur_time()
    return render_to_response('start.html', dict({'message': "До игры осталось", 'NEXT_PAGE': '/write.words/', 'NUMBER_SEC_REDIRECT':NUMBER_SEC_REDIRECT}, **locals()))

    
@need_login_and_enter
def write_words(request):
    id_tour = (cur_time() + 1 - time_start())/(length_game())
    if id_tour >= settingsNUM_TOUR() or id_tour < 0 or is_watch_game() != 1:
        return HttpResponseRedirect('/home/')
    
    choice_titles(id_tour, request.user.username)

    form = ContactForm()
    input_words = []
    name_player = request.user.username
    if request.method == 'POST':
        timeStop = time_start() + settings('SEGMENT_GAME') * (id_tour + 1) + settings('SEGMENT_WAITING')*(id_tour + 1) + settings('WATCHING_RESULT') * id_tour
        if(cur_time() > timeStop + 5):
            return HttpResponseRedirect("/results/")
        form = ContactForm(request.POST)
        if(form.is_valid()) :
            for i in range(1, 11):
                word = form.cleaned_data["word" + str(i)].split()
                if(len(word) > 0) :
                    input_words.append(' '.join(word))
                    input_words[-1] = input_words[-1].lower()
                    input_words[-1] = input_words[-1].replace(u"ё", u"е")
            now = 0
            if len(input_words) > 0:
                CurrentGame.objects.filter(name = Player.objects.get(name = name_player), id_tour = id_tour).delete()
                for new_word in input_words:
                    if new_word not in input_words[0:now]:
                        p = CurrentGame(name = Player.objects.get(name = name_player), word = new_word, id_tour = id_tour, validity = 1)
                        p.save()
                    now = now + 1
        if(cur_time() >= timeStop - settings('SEGMENT_WAITING')):
            return HttpResponseRedirect("/send.words/")
    input_words = CurrentGame.objects.filter(name = Player.objects.get(name = name_player), id_tour = id_tour)      

    time = time_start() + settings('SEGMENT_GAME')*(id_tour + 1) + settings('SEGMENT_WAITING')*(id_tour) + settings('WATCHING_RESULT')*(id_tour)
    TITLE = settingsString('TITLE').split(',')
    NUMBER_SEC_REDIRECT = time - cur_time()
    return render_to_response('write_words.html', dict({'message': "Время на ввод слов. Осталось ", 'NEXT_PAGE': '/send.words/', 'numWords' : range(1, 11), 'title': TITLE[id_tour], 'cur_tour': id_tour + 1, 'num_tour': settingsNUM_TOUR()}, **locals()))

    
@need_login_and_enter
def send_words(request):
    id_tour = (cur_time() - time_start())/(length_game())
    if id_tour >= settingsNUM_TOUR() or id_tour < 0 or is_watch_game() != 1:
        return HttpResponseRedirect('/home/')
    time = time_start() + settings('SEGMENT_GAME') * (id_tour + 1) + settings('SEGMENT_WAITING')*(id_tour + 1) + settings('WATCHING_RESULT') * id_tour
    input_words = []
    name_player = request.user.username
    input_words = CurrentGame.objects.filter(name = Player.objects.get(name = name_player), id_tour = id_tour)       
    NUMBER_SEC_REDIRECT = time - cur_time()
    return render_to_response('waiting.html', dict({'message': "Ожидание игроков, и подсчет очков. Осталось ", 'NEXT_PAGE': '/results/'}, **locals()))


@need_login_and_enter
def results(request):
    id_tour = (cur_time() - time_start())/(length_game())
    timeStartResult = time_start() + settings('SEGMENT_GAME') * (id_tour + 1) + settings('SEGMENT_WAITING')*(id_tour + 1) + settings('WATCHING_RESULT') * id_tour
    if id_tour >= settingsNUM_TOUR() or id_tour < 0 or cur_time() < timeStartResult or is_watch_game() != 1:
        return HttpResponseRedirect('/home/')

    standingAllTours = []
    standingDelta = []
    allPlayers = Player.objects.all()
    isCount = False        
    countResults.acquire()
    print u"in results " + request.user.username + " " + str(id_tour)
    try:
        if(len(PointTour.objects.filter(id_tour = id_tour)) < len(allPlayers)):
            isCount = True
            for curPlayer in allPlayers: 
                player_points = 0
                for last_id_tour in range(id_tour + 1): 
                    #обновление баллов для данного игрока
                    his_words = CurrentGame.objects.filter(name = curPlayer, id_tour = last_id_tour, validity = 1)
                    name_player = User.objects.get(username=curPlayer.name).first_name + " " + User.objects.get(username=curPlayer.name).last_name
                    if last_id_tour == id_tour:
                        standingDelta.append([name_player, player_points]);
                    for cur_word in his_words:
                        player_points += len(CurrentGame.objects.filter(word = cur_word.word, id_tour = last_id_tour, validity = 1)) - 1
                standingAllTours.append([name_player, player_points])
                standingDelta[-1][1] = player_points - standingDelta[-1][1]
                Player.objects.filter(name = curPlayer.name).update(point = player_points)
                print str(User.objects.get(username = curPlayer.name).id) + " " + str(standingDelta[-1][1]) + " " + str(player_points)
                if(len(PointTour.objects.filter(user = User.objects.get(username = curPlayer.name), id_tour = id_tour)) == 0):
                    newPointTours = PointTour(user = User.objects.get(username = curPlayer.name), id_tour = id_tour, point = standingDelta[-1][1])
                    newPointTours.save()
    finally:
        print u"out results " + request.user.username + " " + str(id_tour)
        if countResults.locked() :
            countResults.release()

    if isCount == False :
        for curPlayer in allPlayers:
            name_player = User.objects.get(username=curPlayer.name).first_name + " " + User.objects.get(username=curPlayer.name).last_name
            resultPlayer = PointTour.objects.filter(user = User.objects.get(username=curPlayer.name))
            sumAll = 0
            delta = 0
            for result in resultPlayer:
                if(result.id_tour <= id_tour):
                    sumAll += result.point
                if(result.id_tour < id_tour):
                    delta += result.point
            standingDelta.append([name_player, sumAll - delta])
            standingAllTours.append([name_player, sumAll])

    
    standingDelta.sort(key = lambda element: element[1], reverse = True)
    standingAllTours.sort(key = lambda element: element[1], reverse = True)

    #количество одинаковых слов
    statistics_words = CurrentGame.objects.filter(id_tour = id_tour)
    dict_words = {}
    for it in statistics_words:
        dict_words[it.word] = dict_words.get(it.word, 0)
        dict_words[it.word] += 1

    BanWordsTemp = CurrentGame.objects.filter(validity = 0)
    BanWords = []
    for word in BanWordsTemp:
        BanWords.append(word.word)

    #списки участник - его слова
    allPlayers = Player.objects.all()
    listWords = []
    for name in allPlayers:
        name_player = User.objects.get(username=name.name).first_name + " " + User.objects.get(username=name.name).last_name
        listWords.append([name_player, CurrentGame.objects.filter(name = name, id_tour = id_tour)])

    st_words = dict_words.items()
    st_words.sort(key = lambda element: element[1], reverse = True)

    title = settingsString('TITLE').split(",")
    messageForTitle = u"Ситуация в игре после " + str(id_tour + 1)  + u" тура. Тема " + title[id_tour] + "."
    cur_tour = id_tour + 1
    num_tour = settingsNUM_TOUR()
    if id_tour >= settingsNUM_TOUR() - 1:
        return render_to_response('results.html', dict({"standings": Player.objects.all(), "list_words": listWords}, **locals()))
    else:
        time = time_start() + settings('SEGMENT_GAME') * (id_tour + 1) + settings('SEGMENT_WAITING')*(id_tour + 1) + settings('WATCHING_RESULT')*(id_tour + 1)
        NUMBER_SEC_REDIRECT = time - cur_time()
        return render_to_response('results.html', dict({"standings": Player.objects.all(), "list_words": listWords, 'message': "До следующего тура осталось ", 'next': 'yes',  'NEXT_PAGE': '/write.words/'}, **locals()))

def numberToursInResult():
    numTours = 0
    if(is_watch_game() != 1):
        numTours = settingsNUM_TOUR()
    else :
        id_tour = (cur_time() - time_start() + settings('WATCHING_RESULT'))/(length_game())
        if id_tour <= 0:
            numTours = 0
        elif id_tour >= settingsNUM_TOUR():
            numTours = settingsNUM_TOUR()
        else :
            numTours = id_tour
    return numTours

def standings(request):
    return render_to_response('change_tours.html',dict({"listTours": range(1, numberToursInResult() + 1)}, **locals()))

def standings_tour(request, id_tour):
    id_tour = int(id_tour)
    if (id_tour < 1 or id_tour > numberToursInResult()) and (is_watch_game() == 1):
        return HttpResponseRedirect('/home/')

    id_tour = int(id_tour) - 1
    
    standingAllTours = []
    standingDelta = []
    
    standing = []
    allPlayers = Player.objects.all()

    for curPlayer in allPlayers:
        name_player = User.objects.get(username=curPlayer.name).first_name + " " + User.objects.get(username=curPlayer.name).last_name
        resultPlayer = PointTour.objects.filter(user = User.objects.get(username=curPlayer.name))
        sumAll = 0
        delta = 0
        for result in resultPlayer:
            if(result.id_tour <= id_tour):
                sumAll += result.point
            if(result.id_tour < id_tour):
                delta += result.point
        standingDelta.append([name_player, sumAll - delta])
        standingAllTours.append([name_player, sumAll])
        
    standingDelta.sort(key = lambda element: element[1], reverse = True)
    standingAllTours.sort(key = lambda element: element[1], reverse = True)

    #количество одинаковых слов
    statistics_words = CurrentGame.objects.filter(id_tour = id_tour)
    dict_words = {}
    for it in statistics_words:
        dict_words[it.word] = dict_words.get(it.word, 0)
        dict_words[it.word] += 1

    BanWordsTemp = CurrentGame.objects.filter(validity = 0)
    BanWords = []
    for word in BanWordsTemp:
        BanWords.append(word.word)
        
    #списки участник - его слова
    allPlayers = Player.objects.all()
    listWords = []
    for name in allPlayers:
        name_player = User.objects.get(username=name.name).first_name + " " + User.objects.get(username=name.name).last_name
        listWords.append([name_player, CurrentGame.objects.filter(name = name, id_tour = id_tour)])
    
    st_words = dict_words.items()
    st_words.sort(key = lambda element: element[1], reverse = True)
    
    title = settingsString('TITLE').split(",")
    messageForTitle = u"Ситуация в игре после " + str(id_tour + 1)  + u" тура. Тема " + title[id_tour] + "."
    cur_tour = id_tour + 1
    num_tour = settingsNUM_TOUR()
    
    return render_to_response('results.html', dict({"standings": Player.objects.all(),  "list_words": listWords}, **locals()))


def recount(request):    
    standingAllTours = []
    standingDelta = []
    PointTour.objects.all().delete();
    allPlayers = Player.objects.all()
    
    for curPlayer in allPlayers: 
        for last_id_tour in range(settingsNUM_TOUR()): 
            name_player = User.objects.get(username=curPlayer.name).first_name + " " + User.objects.get(username=curPlayer.name).last_name
            his_words = list(set(CurrentGame.objects.filter(name = curPlayer, id_tour = last_id_tour)))
            #CurrentGame.objects.filter(name = curPlayer, id_tour = last_id_tour).delete()
            #for word in his_words:
            #    p = CurrentGame(name = Player.objects.get(name = name_player), word = word, id_tour = last_id_tour)
            #    p.save()   
            
    for curPlayer in allPlayers: 
        player_points = 0
        for last_id_tour in range(settingsNUM_TOUR()): 
            #обновление баллов для данного игрока
            his_words = CurrentGame.objects.filter(name = curPlayer, id_tour = last_id_tour)
            name_player = User.objects.get(username=curPlayer.name).first_name + " " + User.objects.get(username=curPlayer.name).last_name
            if last_id_tour == id_tour:
                standingDelta.append([name_player, player_points]);
            for cur_word in his_words:
                player_points += len(CurrentGame.objects.filter(word = cur_word.word, id_tour = last_id_tour)) - 1
            standingAllTours.append([name_player, player_points])
            standingDelta[-1][1] = player_points - standingDelta[-1][1]
            Player.objects.filter(name = curPlayer.name).update(point = player_points)
            newPointTours = PointTour(user = User.objects.get(username = curPlayer.name), id_tour = id_tour, point = standingDelta[-1][1])
            newPointTours.save()    
    return

def lock(request):
    lock = FileLock("lock.txt")
    with lock:
        print 'is locked.' + str(request.user.id)
        time.sleep(60)
        print 'un locked.' + str(request.user.id)
    return render_to_response('results.html')        

