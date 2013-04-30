from celery import task

from tasks.models import Tasks
from titles.models import Titles
from words.models import Words
from versionTitles.models import VersionTitles
from django.contrib.auth.models import User
from statisticsWords.models import StatisticsWords
from django.db.models import Avg, Max, Min, Count, Sum
from resultTours.models import ResultTours
from players.models import Players
from resultGames.models import ResultGames

@task()
def add(x, y):
    return x + y

@task()
def task_choice_titles(task):
	if len(Titles.objects.filter(gameID = task.gameID, tourID = task.tourID)) > 0 :
		return
	titleCurrent = Titles.objects.filter(gameID = task.gameID, tourID = -1)[0]
	if task.tourID >= 0:
		bestPlayers = ResultTours.objects.filter(gameID = task.gameID, tourID = task.tourID - 1).order_by('-score')
		for player in bestPlayers:
			if len(Titles.objects.filter(gameID = task.gameID, tourID = -1, user = player.user)) > 0:
				titleCurrent = Titles.objects.filter(gameID = task.gameID, tourID = -1, user = player.user)[0]
	titleCurrent.tourID = task.tourID
	titleCurrent.save()
	