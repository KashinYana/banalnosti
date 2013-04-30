# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from dataGame.models import DataGame
from tasks.models import Tasks
from django.contrib.auth.models import User
from forms import CreateForm, WordForm
from titles.models import Titles
from django import forms
import datetime
from resultGames.models import ResultGames
from resultTours.models import ResultTours
from game_views import count_result, count_final_result
from django.template import RequestContext
from lockfile import FileLock
from django.db.models import Avg, Max, Min, Count, Sum
from players.models import Players
from words.models import Words
from statisticsWords.models import StatisticsWords
import time
from lockfile import FileLock

from celerytest.tasks import task_choice_titles, task_count_statistics_words, task_count_result, task_count_final_result

def management(request):
    if request.user.is_authenticated() and request.user.is_superuser :
        setInit = {}
        today = datetime.datetime.today()
        setInit['startYear'] = today.year
        setInit['startMonth'] = today.month
        setInit['startDay'] = today.day
        setInit['startHour'] = today.hour
        setInit['startMinute'] = today.minute
        
        setInit['toursNumber'] = 7
        setInit['lenWriteWords'] = 200
        setInit['lenWatchResult'] = 200
        setInit['lenChecking'] = 60
        setInit['lenWaitWords'] = 5

        setInit['info'] = 720

        createForm = CreateForm(setInit)

        gameAll = DataGame.objects.all().order_by('-start')
        return render_to_response('management.html', locals(), context_instance=RequestContext(request))
    else :
        return render_to_response('not_management.html', locals(), context_instance=RequestContext(request))

def add_titles(request, gameID):
    gameID = int(gameID)
    form = WordForm()
    if request.method == 'POST':
        
        form = WordForm(request.POST)
            
        if form.is_valid() :
            if len(Titles.objects.filter(gameID = DataGame.objects.get(id = gameID), user = User.objects.get(id = 92))) > 0 :
                Titles.objects.filter(gameID = DataGame.objects.get(id = gameID), user = User.objects.get(id = 92)).delete()
            titlesInput = []
            for i in range(1, 11):
                titlesInput.append(form.cleaned_data["word" + str(i)])
            for title in titlesInput:
                if len(title.split()) == 0:
                    continue
                titleNew = Titles(gameID = DataGame.objects.get(id = gameID), user = User.objects.get(id = 92), tourID = -1, title = title)
                titleNew.save()
        message = "Темы добавлены в количестве " + str(len(Titles.objects.filter(gameID = DataGame.objects.get(id = gameID), user = User.objects.get(id = 92))))
    return render_to_response('add_titles.html', locals(), context_instance=RequestContext(request))


def count_result_update(task):
    if len(ResultTours.objects.filter(gameID = task.gameID, tourID = task.tourID)) == 0:
        tourLast = ResultTours.objects.filter(gameID = task.gameID).aggregate(max = Max('tourID'))
        tourLast = tourLast.get('max')
        if tourLast == None:
            tourLast = 0
        else:
            tourLast += 1
        for tourID in range(task.tourID + 1):
            if len(ResultTours.objects.filter(gameID = task.gameID, tourID = tourID)) == 0:
                playersAll = Players.objects.filter(gameID = task.gameID)
                for player in playersAll:
                    player = player.user
                    wordsPlayer = Words.objects.filter(gameID = task.gameID, tourID = tourID, user = player).values('word')
                    scorePlayer = StatisticsWords.objects.filter(gameID = task.gameID, tourID = tourID, word__in = wordsPlayer).aggregate(sum = Sum('score'))
                    scorePlayer = scorePlayer.get('sum', 0)
                    if scorePlayer == None:
                        scorePlayer = 0
                    scoreTotalPlayer = 0
                    if tourID > 0 and len(ResultTours.objects.filter(gameID = task.gameID, tourID = tourID - 1, user = player)) > 0 :
                        scoreTotalPlayer = ResultTours.objects.get(gameID = task.gameID, tourID = tourID - 1, user = player).scoreTotal
                    resultToursNew = ResultTours(gameID = task.gameID, tourID = tourID, user = player, score = scorePlayer, scoreTotal = scoreTotalPlayer + scorePlayer)
                    resultToursNew.save()

def count_final_result_update(task):
    lock = FileLock("/home/senderma/projects/banalnosti/count_final_result")
    with lock:
        if len(ResultGames.objects.filter(gameID = task.gameID)) == 0:
            playerAll = Players.objects.filter(gameID = task.gameID)
            for player in playerAll:
                score = ResultTours.objects.get(gameID = task.gameID, user = player.user, tourID = task.gameID.toursNumber - 1).scoreTotal
                resultGamesNew = ResultGames(gameID = task.gameID, user = player.user, score = score)
                resultGamesNew.save()
        
def count_statistics_words_update(task):
    lock = FileLock("/home/senderma/projects/banalnosti/count_statistics_words")
    with lock:
        if len(StatisticsWords.objects.filter(gameID = task.gameID, tourID = task.tourID)) == 0:
            for tourID in range(0, task.tourID + 1):
                verbosePlayers = Words.objects.filter(gameID = task.gameID, tourID = tourID).values('user').annotate(countWords=Count('user')).order_by()
                for verbosePlayer in verbosePlayers:
                    wordsPlayer = Words.objects.filter(gameID = task.gameID, tourID = tourID, user = verbosePlayer['user']).order_by('-id')
                    if verbosePlayer['countWords'] > 10 or len(set(wordsPlayer)) != len(wordsPlayer):
                        wordsPlayer = map(lambda x: x.word, wordsPlayer[:10])
                        wordsPlayer = list(set(wordsPlayer))
                        Words.objects.filter(gameID = task.gameID, tourID = tourID, user = verbosePlayer['user']).delete()
                        for word in wordsPlayer:
                            wordNew = Words(gameID = task.gameID, tourID = tourID, user = User.objects.get(id = verbosePlayer['user']), word = word)
                            wordNew.save()
                uniqueWords = Words.objects.filter(gameID = task.gameID, tourID = tourID).values('word').annotate(count=Count('word')).order_by()
                for word in uniqueWords:
                    statisticsWordsNew = StatisticsWords(gameID = task.gameID, tourID = tourID, word = word['word'], count = word['count'], score = word['count'] - 1, legal = 1)
                    statisticsWordsNew.save()
            
def rejudge(request, gameID):
    gameID = int(gameID)
    ResultTours.objects.filter(gameID = DataGame.objects.get(id = gameID)).delete()
    ResultGames.objects.filter(gameID = DataGame.objects.get(id = gameID)).delete()
    StatisticsWords.objects.filter(gameID = DataGame.objects.get(id = gameID)).delete()
    dataGame = DataGame.objects.get(id = gameID)
    taskDec = Tasks(gameID = dataGame, tourID = dataGame.toursNumber - 1)
    count_statistics_words_update(taskDec)
    count_result_update(taskDec)
    task = Tasks(gameID = dataGame, tourID = dataGame.toursNumber)
    count_final_result_update(task)
    return render_to_response('rejudge.html', locals(), context_instance=RequestContext(request))


def update_ban_words(request, gameID):
    lock = FileLock("/home/senderma/projects/banalnosti/check_legality")
    with lock:
        tourID = int(request.POST.get('tourID')) - 1
        wordsNotLegality = request.POST.getlist('word')
        statisticsWordsUpdate = StatisticsWords.objects.filter(gameID = gameID, tourID = tourID, word__in = wordsNotLegality)
        statisticsWordsUpdate.update(legal = 0, score = 0)
        statisticsWordsUpdate = StatisticsWords.objects.filter(gameID = gameID, tourID = tourID).exclude(word__in = wordsNotLegality)
        map(lambda x: StatisticsWords.objects.filter(gameID = gameID, tourID = tourID, word = x.word).update(legal = 1, score = x.count - 1), statisticsWordsUpdate)
    return

def ban(request, gameID):
    gameID = int(gameID)
    gameID = DataGame.objects.get(id = gameID)

    if request.method == 'POST' and request.POST.has_key('tourID'):
        update_ban_words(request, gameID)
        tourID = int(request.POST.get('tourID'))-1
        ResultTours.objects.filter(gameID = DataGame.objects.get(id = gameID.id)).delete()
        task = Tasks(gameID = gameID, tourID = gameID.toursNumber - 1)
        count_result_update(task)
        isUpdateFinalResult = request.POST.getlist('isUpdateFinalResult')
        if isUpdateFinalResult:
            ResultGames.objects.filter(gameID = gameID).delete()
            task = Tasks(gameID = gameID, tourID = gameID.toursNumber)
            count_final_result_update(task)

    wordsTours = []
    for tourID in range(gameID.toursNumber):
        wordsTour = StatisticsWords.objects.filter(gameID = gameID, tourID = tourID)
        wordsTours.append([tourID + 1, Titles.objects.get(gameID = gameID, tourID = tourID),wordsTour])
    return render_to_response('ban.html', locals(), context_instance=RequestContext(request))        


def change_game(request, gameID):
    gameID = int(gameID)
    game = DataGame.objects.get(id = gameID)
    
    setInit = {}
    setInit['startYear'] = game.start.year
    setInit['startMonth'] = game.start.month
    setInit['startDay'] = game.start.day
    setInit['startHour'] = game.start.hour
    setInit['startMinute'] = game.start.minute
    
    setInit['toursNumber'] = game.toursNumber
    setInit['lenWriteWords'] = game.lenWriteWords
    setInit['lenWatchResult'] = game.lenWatchResult
    setInit['lenChecking'] = game.lenChecking
    setInit['lenWaitWords'] = game.lenWaitWords

    setInit['info'] = 720

    createForm = CreateForm(setInit)
    game.delete()
    gameAll = DataGame.objects.all().order_by('-start')
    return render_to_response('management.html', locals(), context_instance=RequestContext(request)) 


def create(request):
    if request.method == 'POST':
        form = CreateForm(request.POST)
        if form.is_valid() :
            startYear = form.cleaned_data['startYear']
            startMonth = form.cleaned_data['startMonth']
            startDay = form.cleaned_data['startDay']
            startHour = form.cleaned_data['startHour']
            startMinute = form.cleaned_data['startMinute']
            toursNumber = form.cleaned_data['toursNumber']
            lenWriteWords = form.cleaned_data['lenWriteWords']
            lenWatchResult = form.cleaned_data['lenWatchResult']
            lenChecking = form.cleaned_data['lenChecking']
            lenWaitWords = form.cleaned_data['lenWaitWords']
            lenCountStatisticsWords = 10
            lenCountResult = 10

            lenGame = lenWriteWords + lenWaitWords + lenCountStatisticsWords + lenChecking + lenCountResult + lenWatchResult

            info = form.cleaned_data['info']

            start = datetime.datetime(startYear, startMonth, startDay, startHour, startMinute)
            
            newGame = DataGame(start = start, toursNumber = toursNumber, lenWriteWords = lenWriteWords, lenWatchResult = lenWatchResult, lenChecking = lenChecking, lenWaitWords = lenWaitWords)
            newGame.save()
            
            delta = datetime.timedelta(minutes=info)
            action = Tasks(taskTime = start - delta, action = "info", gameID = newGame, tourID = -1)
            action.save()
            listToChain = []
                
            for i in range(toursNumber):
                delta = datetime.timedelta(seconds = i*(lenGame))	
            
                countdownTime =  start + delta - datetime.datetime.today() - datetime.timedelta(seconds = 1)
                task_choice_titles.apply_async((Tasks(gameID = newGame, tourID = i),), countdown = countdownTime.seconds)
                #listToChain.append(task_choice_titles.subtask((Tasks(gameID = newGame, tourID = i),), countdown = countdownTime.seconds))
            
                action = Tasks(taskTime = start + delta, action = "tour", gameID = newGame, tourID = i)
                action.save()
                
                delta = datetime.timedelta(seconds = i*(lenGame) + lenWriteWords)  
                action = Tasks(taskTime = start + delta, action = "sendWords", gameID = newGame, tourID = i)
                action.save()
                
                delta = datetime.timedelta(seconds = i*(lenGame) + lenWriteWords + lenWaitWords)  
                countdownTime =  start + delta - datetime.datetime.today()
                task_count_statistics_words.apply_async((Tasks(gameID = newGame, tourID = i),), countdown = countdownTime.seconds)
                action = Tasks(taskTime = start + delta, action = "countStatisticsWords", gameID = newGame, tourID = i)
                action.save()
                
                delta = datetime.timedelta(seconds = i*(lenGame) + lenWriteWords + lenWaitWords + lenCountStatisticsWords)  
                action = Tasks(taskTime = start + delta, action = "check", gameID = newGame, tourID = i)
                action.save()

                delta = datetime.timedelta(seconds = i*(lenGame) + lenWriteWords + lenWaitWords + lenCountStatisticsWords + lenChecking)  
                countdownTime =  start + delta - datetime.datetime.today()
                task_count_result.apply_async((Tasks(gameID = newGame, tourID = i),), countdown = countdownTime.seconds)
                action = Tasks(taskTime = start + delta, action = "countResult", gameID = newGame, tourID = i)
                action.save()

                delta = datetime.timedelta(seconds = i*(lenGame) + lenWriteWords + lenWaitWords + lenCountStatisticsWords +lenChecking + lenCountResult)  
                action = Tasks(taskTime = start + delta, action = "watchResult", gameID = newGame, tourID = i)
                action.save()
            
            delta = datetime.timedelta(seconds = toursNumber*(lenGame))
            countdownTime =  start + delta - datetime.datetime.today() - datetime.timedelta(seconds = 1)
            task_count_final_result.apply_async((Tasks(gameID = newGame, tourID = toursNumber),), countdown = countdownTime.seconds)
            action = Tasks(taskTime = start + delta, action = "endGame", gameID = newGame, tourID = toursNumber)
            action.save()
            
            return render_to_response('ok_create.html', locals(), context_instance=RequestContext(request))	

    error = u"Не удалось создать игру. Произошла ошибка."
    return render_to_response('error.html', locals(), context_instance=RequestContext(request))	
			