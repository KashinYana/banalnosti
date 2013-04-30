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
from statisticsWords.models import StatisticsWords
from words.models import Words
from game_views import count_result, count_final_result
from players.models import Players
from django.utils import timezone
from django.db.models import Max
from django.template import RequestContext
from django.db.models import Avg, Max, Min, Count, Sum


def statistics_game(dataGame):    
    resultGame = ResultGames.objects.filter(gameID = dataGame).order_by('-score')
    statisticsGame = []

    winnersScore = []
    for tour in range(dataGame.toursNumber):
        maxScore = ResultTours.objects.filter(gameID = dataGame, tourID = tour).aggregate(Max('score'))
        maxScore = maxScore['score__max']
        winnersScore.append(maxScore)

    for resultPlayer in resultGame:
        statisticsGame.append([resultPlayer, [] ])
        scoreBase = ResultTours.objects.filter(gameID = dataGame, user = resultPlayer.user).order_by('tourID')
        score = [0]*dataGame.toursNumber
        for x in scoreBase:
            score[x.tourID] = x.score
        for tourID in range(dataGame.toursNumber):
            statisticsGame[-1][1].append([score[tourID], score[tourID] == winnersScore[tourID]])
    return statisticsGame

def titles_game(dataGame):
    titles = Titles.objects.filter(gameID = dataGame, tourID__gte = 0).order_by('tourID')
    return map(lambda x: x.title, titles)

def history(request):
    currentTimeStart = datetime.datetime.today()
    
    currentTime = timezone.now()
    gameAll = DataGame.objects.all().order_by('-start')
    gameFinished = filter(lambda x : Tasks.objects.get(gameID = x, action = 'endGame').taskTime < currentTime, gameAll)
    statisticsGameAll = map(lambda x: [x, range(1, x.toursNumber + 1), statistics_game(x), zip(range(1, x.toursNumber + 1), titles_game(x))], gameFinished)
    currentTimeFinish = datetime.datetime.today()
    print currentTimeFinish - currentTimeStart
    
    return render_to_response('history.html', locals(), context_instance=RequestContext(request))

def history_tour(request, gameID, tourID):
    currentTimeStart = datetime.datetime.today()
    gameID = DataGame.objects.get(id = int(gameID))
    tourID = int(tourID) - 1

    title = Titles.objects.get(gameID = gameID, tourID = tourID)
    messageForTitle = u"Результаты тура " + str(tourID + 1) + u" из " + str(gameID.toursNumber) + ".\n"
    messageForTitle += u"Тема тура была " + title.title + u" от автора " + title.user.get_full_name() + "."
    playersScore = ResultTours.objects.filter(gameID = gameID, tourID = tourID).order_by('-score')
    playersScoreTotal = ResultTours.objects.filter(gameID = gameID, tourID = tourID).order_by('-scoreTotal')
    statisticsWords = StatisticsWords.objects.filter(gameID = gameID, tourID = tourID).order_by('-count')
    
    wordsRequestUser = []
    if request.user.is_authenticated():
        wordsRequestUser = Words.objects.filter(gameID = gameID, tourID = tourID, user = request.user).values('word')
        wordsRequestUser = map(lambda x: x['word'], wordsRequestUser)
    
    players = Players.objects.filter(gameID = gameID)
    playersWords = []   
    for player in players:
        words = Words.objects.filter(gameID = gameID, tourID = tourID, user = player.user).values('word')
        words = map(lambda x: x['word'], words)
        playersWords.append([player.user, StatisticsWords.objects.filter(gameID = gameID, tourID = tourID, word__in = words)])
    
    currentTimeFinish = datetime.datetime.today()
    print "history_tour " + str(currentTimeFinish - currentTimeStart)
    return render_to_response('result.html', locals(), context_instance=RequestContext(request))



def test(request):
    newGameId = DataGame.objects.get(id = '115')
    words = Words.objects.filter(gameID = DataGame.objects.get(id = '104'))
    listAddWords = []
    for i in range(len(words)):
        listAddWords.append(Words(gameID = newGameId, word = words[i].word, user = words[i].user, tourID = words[i].tourID)) 
    Words.objects.bulk_create(listAddWords)   
    return render_to_response('test.html', locals(), context_instance=RequestContext(request))

    currentTimeStart = datetime.datetime.today()
    task = Tasks(gameID = DataGame.objects.get(id = '104'), tourID = 1)
    tourID = task.tourID

    listAddResults = []

    #verbosePlayers = Words.objects.filter(gameID = task.gameID, tourID = task.tourID).values('user').annotate(countWords=Count('user')).order_by()
    #for verbosePlayer in verbosePlayers:
    #    wordsPlayer = Words.objects.filter(gameID = task.gameID, tourID = task.tourID, user = verbosePlayer['user']).order_by('-id')
    #    if verbosePlayer['countWords'] > 10  or len(set(wordsPlayer)) != len(wordsPlayer):
    #        wordsPlayer = map(lambda x: x.word, wordsPlayer[:10])
    #        wordsPlayer = list(set(wordsPlayer))
    #        Words.objects.filter(gameID = task.gameID, tourID = task.tourID, user = verbosePlayer['user']).delete()
    #        for word in wordsPlayer:
    #            wordNew = Words(gameID =  DataGame.objects.get(id = '105'), tourID = task.tourID, user = User.objects.get(id = verbosePlayer['user']), word = word)
    #            wordNew.save()

    #uniqueWords = Words.objects.filter(gameID = task.gameID, tourID = task.tourID).values('word').annotate(count=Count('word')).order_by()
    #for word in uniqueWords:
     #   statisticsWordsNew = StatisticsWords(gameID =  DataGame.objects.get(id = '105'), tourID = task.tourID, word = word['word'], count = word['count'], score = word['count'] - 1, legal = 1)
     #   listAddResults.append(statisticsWordsNew)
    #    statisticsWordsNew.save()
    #StatisticsWords.objects.bulk_create(listAddResults)
    #lenn = len(listAddResults)


    
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
        resultToursNew = ResultTours(gameID = DataGame.objects.get(id = '111'), tourID = tourID, user = player, score = scorePlayer, scoreTotal = scoreTotalPlayer + scorePlayer)
        listAddResults.append(resultToursNew)
        #resultToursNew.save()
    ResultTours.objects.bulk_create(listAddResults)
    currentTimeFinish = datetime.datetime.today()
    message = currentTimeFinish - currentTimeStart
    lenn = len(listAddResults)

    return render_to_response('test.html', locals(), context_instance=RequestContext(request))