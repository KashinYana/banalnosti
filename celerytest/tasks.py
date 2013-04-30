from celery import task

from versionTitles.models import VersionTitles
from django.contrib.auth.models import User
from statisticsWords.models import StatisticsWords
from django.db.models import Avg, Max, Min, Count, Sum
from resultTours.models import ResultTours
from players.models import Players
from resultGames.models import ResultGames
from titles.models import Titles
from words.models import Words
from forms import WordForm, TitleForm
from lockfile import FileLock
from django.utils import timezone
import datetime

@task()
def add(x, y):
    return x + y

@task()
def task_choice_titles(task):
	if len(Titles.objects.filter(gameID = task.gameID, tourID = task.tourID)) > 0 :
		print "late (((( task_choice_titles "
		return
	titleCurrent = Titles.objects.filter(gameID = task.gameID, tourID = -1)[0]
	if task.tourID >= 0:
		bestPlayers = ResultTours.objects.filter(gameID = task.gameID, tourID = task.tourID - 1).order_by('-score')
		for player in bestPlayers:
			if len(Titles.objects.filter(gameID = task.gameID, tourID = -1, user = player.user)) > 0:
				titleCurrent = Titles.objects.filter(gameID = task.gameID, tourID = -1, user = player.user)[0]
				break
	titleCurrent.tourID = task.tourID
	titleCurrent.save()

@task()
def task_save_words(user, task, wordsInputUnique):
	print "in"
	Words.objects.filter(gameID = task.gameID, tourID = task.tourID, user = user).delete()
	for word in wordsInputUnique:
		wordNew = Words(gameID = task.gameID, tourID = task.tourID, user = user, word = word)
		wordNew.save()
	print "out"


@task()
def task_count_statistics_words(task):
	add_players(task)

	if len(StatisticsWords.objects.filter(gameID = task.gameID, tourID = task.tourID)) == 0:
		currentTimeStart = datetime.datetime.today()
		verbosePlayers = Words.objects.filter(gameID = task.gameID, tourID = task.tourID).values('user').annotate(countWords=Count('user')).order_by()
		for verbosePlayer in verbosePlayers:
			wordsPlayer = Words.objects.filter(gameID = task.gameID, tourID = task.tourID, user = verbosePlayer['user']).order_by('-id')
			if verbosePlayer['countWords'] > 10  or len(set(wordsPlayer)) != len(wordsPlayer):
				wordsPlayer = map(lambda x: x.word, wordsPlayer[:10])
				wordsPlayer = list(set(wordsPlayer))
				print wordsPlayer
				Words.objects.filter(gameID = task.gameID, tourID = task.tourID, user = verbosePlayer['user']).delete()
				listAddWords = []
				for word in wordsPlayer:
					listAddWords.append(Words(gameID = task.gameID, tourID = task.tourID, user = User.objects.get(id = verbosePlayer['user']), word = word))
				Words.objects.bulk_create(listAddWords)
		
		uniqueWords = Words.objects.filter(gameID = task.gameID, tourID = task.tourID).values('word').annotate(count=Count('word')).order_by()
		listAddStatisticsWords = []
		for word in uniqueWords:
			listAddStatisticsWords.append(StatisticsWords(gameID = task.gameID, tourID = task.tourID, word = word['word'], count = word['count'], score = word['count'] - 1, legal = 1))
		StatisticsWords.objects.bulk_create(listAddStatisticsWords)
		currentTimeFinish = datetime.datetime.today()
		print "task_count_statistics_words " + str(currentTimeFinish - currentTimeStart)
	else :
		print "late ((( task_count_statistics_words"		

@task()
def task_count_result(task):
	if len(ResultTours.objects.filter(gameID = task.gameID, tourID = task.tourID)) == 0:
		currentTimeStart = datetime.datetime.today()
		tourLast = ResultTours.objects.filter(gameID = task.gameID).aggregate(max = Max('tourID'))
		tourLast = tourLast.get('max')
		if tourLast == None:
			tourLast = 0
		else:
			tourLast += 1
		currentTimeStart2 = datetime.datetime.today()
		
		
		listAddResultTours = []
		for tourID in range(task.tourID + 1):
			if len(ResultTours.objects.filter(gameID = task.gameID, tourID = tourID)) == 0:
				
				resultPlayersLatestTour = {}
				if tourID > 0:
					resultPlayersLatestTourList = ResultTours.objects.filter(gameID = task.gameID, tourID = tourID - 1)
					for playerResult in resultPlayersLatestTourList:
						resultPlayersLatestTour[playerResult.user.id] = playerResult.scoreTotal

				statisticsWords = {}
				statisticsWordsList = StatisticsWords.objects.filter(gameID = task.gameID, tourID = tourID)
				for word in statisticsWordsList:
					statisticsWords[word.word] = word.score

				resultPlayersCurrentTour = {}
				wordsPlayers = Words.objects.filter(gameID = task.gameID, tourID = tourID)
				for word in wordsPlayers:
					if not resultPlayersCurrentTour.has_key(word.user.id):
						resultPlayersCurrentTour[word.user.id] = 0
					resultPlayersCurrentTour[word.user.id] += statisticsWords[word.word]

				playersAll = Players.objects.filter(gameID = task.gameID)
				for player in playersAll:
					player = player.user
					scorePlayer = resultPlayersCurrentTour.get(player.id, 0)
					scoreTotalPlayer = resultPlayersLatestTour.get(player.id, 0)
					listAddResultTours.append(ResultTours(gameID = task.gameID, tourID = tourID, user = player, score = scorePlayer, scoreTotal = scoreTotalPlayer + scorePlayer))
		currentTimeStart3 = datetime.datetime.today()
		ResultTours.objects.bulk_create(listAddResultTours)
		
		currentTimeFinish = datetime.datetime.today()
		print "task_count_result1 " +  str(currentTimeStart2 - currentTimeStart)
		print "task_count_result2 " +  str(currentTimeStart3 - currentTimeStart2)
		print "task_count_resultall " +  str(currentTimeFinish - currentTimeStart)
	else :
		print "late ((( task_count_result"

@task()
def task_count_final_result(task):
	if len(ResultGames.objects.filter(gameID = task.gameID)) == 0:
		currentTimeStart = datetime.datetime.today()
		listAddResultGames = []
		playerAll = Players.objects.filter(gameID = task.gameID)
		for player in playerAll:
			score = ResultTours.objects.get(gameID = task.gameID, user = player.user, tourID = task.gameID.toursNumber - 1).scoreTotal
			listAddResultGames.append(ResultGames(gameID = task.gameID, user = player.user, score = score))
		ResultGames.objects.bulk_create(listAddResultGames)
		currentTimeFinish = datetime.datetime.today()
		print "task_count_final_result " + str(currentTimeFinish - currentTimeStart)
	else :
		print "late ((( count_final_result "

def add_players(task):
	newPlayers = Words.objects.filter(gameID = task.gameID, tourID = task.tourID).exclude(user__in = Players.objects.filter(gameID = task.gameID).values('user')).values('user')
	newPlayers = map(lambda x: x['user'], newPlayers)
	newPlayers = list(set(newPlayers))
	listAddPlayers = []
	for player in newPlayers:
		listAddPlayers.append(Players(gameID = task.gameID, user = User.objects.get(id = player)))
	Players.objects.bulk_create(listAddPlayers)
	print str(newPlayers) + " add_players"
