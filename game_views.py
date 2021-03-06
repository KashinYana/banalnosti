# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from forms import WordForm, TitleForm
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
from lockfile import FileLock
import datetime
from django.utils import timezone
import time, random
from django.template import RequestContext
from celerytest.tasks import task_save_words

def need_login(function):
    #@functools.wraps(function)
    def need_login_wrapper(*args, **kwargs):
        request = args[0]
        if not request.user.is_authenticated():
            return render_to_response('not_login.html', locals())
        return function(*args, **kwargs)
    return need_login_wrapper


def information(request, task):
    titleForm = TitleForm()
    if request.method == 'POST':
        titleForm = TitleForm(request.POST)
        if titleForm.is_valid():
            print "before lock in information " + str(request.user.id)
            lock = FileLock("/home/senderma/projects/banalnosti/lockAddTitle")
            with lock:
                print "in information " + str(request.user.id)
                if(len(titleForm.cleaned_data['title'].split()) > 0):
                    print "count information " + str(request.user.id)
                    titleInput = titleForm.cleaned_data['title']
                    userTitle = Titles.objects.filter(gameID = task.gameID, user = request.user)
                    if(len(userTitle) != 1 or userTitle[0].title != titleInput):
	                    Titles.objects.filter(gameID = task.gameID, user = request.user).delete()
	                    titlesNew = Titles(user = request.user, title = titleInput, gameID = task.gameID, tourID = -1)
	                    titlesNew.save()
                print "out information " + str(request.user.id)
                time.sleep(1)	
    if len(Titles.objects.filter(gameID = task.gameID, user = request.user)) > 0:
        titleYour = Titles.objects.filter(gameID = task.gameID, user = request.user)[0]
    
	#для html    
    peoplesInputTitles = map(lambda x: x.user, Titles.objects.filter(gameID = task.gameID))
    currentTime = timezone.now()
    taskNext = Tasks.objects.filter(taskTime__gt = task.taskTime).order_by('taskTime')[0]   
    NUMBER_SEC_REDIRECT = taskNext.taskTime - currentTime
    NUMBER_SEC_REDIRECT = NUMBER_SEC_REDIRECT.days*60*60*24 + NUMBER_SEC_REDIRECT.seconds + 1
    NEXT_PAGE = '/main/'
    message = "До игры осталось"
    return render_to_response('info.html', locals(), context_instance=RequestContext(request))

def save_words(request, task):
	form = WordForm(request.POST)
	if(form.is_valid()) :
		wordsInput = []
		for i in range(1, 11):
			word = form.cleaned_data["word" + str(i)].split()
			if(len(word) > 0):
				wordsInput.append(' '.join(word))
				wordsInput[-1] = wordsInput[-1].lower()
				wordsInput[-1] = wordsInput[-1].replace(u"ё", u"е")
		if len(wordsInput) > 0:
			wordsInputUnique = []
			for i in range(len(wordsInput)):
				if wordsInput[i] not in wordsInput[0:i]:
					wordsInputUnique.append(wordsInput[i])

			wordsPlayer = Words.objects.filter(gameID = task.gameID, tourID = task.tourID, user = request.user).order_by('id')
			wordsPlayer = map(lambda x: x.word, wordsPlayer)
			if wordsPlayer == wordsInputUnique:
				return

			print "before save_words " + str(request.user.id)
			lock = FileLock("/home/senderma/projects/banalnosti/lockSaveWords3")
			with lock:
				currentTime = timezone.now()
				taskNext = Tasks.objects.filter(taskTime__gt = task.taskTime).order_by('taskTime')[0]
				if (taskNext.action == "sendWords")  or ((taskNext.action == "countStatisticsWords") and (taskNext.taskTime > currentTime + datetime.timedelta(seconds = 2))):
					print "in save_words " + str(request.user.id)
					Words.objects.filter(gameID = task.gameID, tourID = task.tourID, user = request.user).delete()
					listAddWords = []
					for word in wordsInputUnique:
						listAddWords.append(Words(gameID = task.gameID, tourID = task.tourID, user = request.user, word = word))
					Words.objects.bulk_create(listAddWords)
					print "out save_words " + str(request.user.id)
				else :
					print str(request.user.id) + u"not save words decause "+ taskNext.action + u" " + str(taskNext.taskTime) + u" | " + str(currentTime) + u" => " + str(currentTime + datetime.timedelta(seconds = 2))
		    
def choice_titles(request, task):

	while len(Titles.objects.filter(gameID = task.gameID, tourID = task.tourID)) == 0 :
		time.sleep(1)
	return


def write_words(request, task):
	choice_titles(request, task)

	if request.method == "POST":
		save_words(request, task)

	wordsPlayer = Words.objects.filter(user = request.user, gameID = task.gameID, tourID = task.tourID).order_by('id')
	wordsInit = {}
	wordsTest = range(30)
	wordsLatestVersion = []
	#for i in range(10):
	for i in range(min(10, len(wordsPlayer))):
		wordsInit["word" + str(i + 1)] =  wordsPlayer[i].word #str(wordsTest[random.randint(0,29)])
		wordsLatestVersion.append(wordsPlayer[i].word)
	wordForm = WordForm(wordsInit)

	#для html
	title = Titles.objects.get(gameID = task.gameID, tourID = task.tourID)
	tourID = task.tourID + 1
	currentTime = timezone.now()
	taskNext = Tasks.objects.filter(taskTime__gt = task.taskTime).order_by('taskTime')[0]   
	NUMBER_SEC_REDIRECT = taskNext.taskTime - currentTime
	NUMBER_SEC_REDIRECT = NUMBER_SEC_REDIRECT.days*60*60*24 + NUMBER_SEC_REDIRECT.seconds + 1
	print task, taskNext
	print NUMBER_SEC_REDIRECT, currentTime
	NEXT_PAGE = '/main/'
	message = "Время на ввод слов. Осталось "
	return render_to_response('write_words.html', locals(), context_instance=RequestContext(request))

def wait_words(request, task):
	if request.method == "POST":
		save_words(request, task)

	#для html
	currentTime = timezone.now()
	taskNext = Tasks.objects.filter(taskTime__gt = task.taskTime).order_by('taskTime')[0]   
	NUMBER_SEC_REDIRECT = taskNext.taskTime - currentTime
	NUMBER_SEC_REDIRECT = NUMBER_SEC_REDIRECT.days*60*60*24 + NUMBER_SEC_REDIRECT.seconds + 1
	NEXT_PAGE = '/main/'
	message = "Мы ещё ожидаем слов "
	return render_to_response('wait_words.html', locals(), context_instance=RequestContext(request))

def count_statistics_words(request, task):
	
	if len (Words.objects.filter(gameID = task.gameID, tourID = task.tourID)) == 0:
		return

	while len(StatisticsWords.objects.filter(gameID = task.gameID, tourID = task.tourID)) == 0:
		time.sleep(1)

	return

def wait_count_base(request, task):
#для html
	currentTime = timezone.now()
	taskNext = Tasks.objects.filter(taskTime__gt = task.taskTime).order_by('taskTime')[0]   
	NUMBER_SEC_REDIRECT = taskNext.taskTime - currentTime
	NUMBER_SEC_REDIRECT = NUMBER_SEC_REDIRECT.days*60*60*24 + NUMBER_SEC_REDIRECT.seconds + 1
	NEXT_PAGE = '/main/'
	message = "Результаты будут ещё подсчитываться "
	if not request.user.is_superuser and task.action == 'countResult':
		NUMBER_SEC_REDIRECT += random.randint(0, 25)
	return render_to_response('wait_сount_base.html', locals(), context_instance=RequestContext(request))



def save_check_legality(request, task):
	print "before save_check_legality " + str(request.user.id)
	lock = FileLock("/home/senderma/projects/banalnosti/check_legality")
	with lock:
		currentTime = timezone.now()
		taskNext = Tasks.objects.filter(taskTime__gt = task.taskTime).order_by('taskTime')[0]
		if taskNext.action == "countResult" and taskNext.taskTime > currentTime + datetime.timedelta(seconds = 2):
			print "in save_check_legality " + str(request.user.id)
			wordsNotLegality = request.POST.getlist('word')
			statisticsWordsUpdate = StatisticsWords.objects.filter(gameID = task.gameID, tourID = task.tourID, word__in = wordsNotLegality)
			statisticsWordsUpdate.update(legal = 0, score = 0)
			print "out save_check_legality " + str(request.user.id)
	return

def check_legality(request, task):
	count_statistics_words(request, task)
	#для html
	currentTime = timezone.now()
	taskNext = Tasks.objects.filter(taskTime__gt =task.taskTime).order_by('taskTime')[0]   
	NUMBER_SEC_REDIRECT = taskNext.taskTime - currentTime
	NUMBER_SEC_REDIRECT = NUMBER_SEC_REDIRECT.days*60*60*24 + NUMBER_SEC_REDIRECT.seconds + 1

#	NUMBER_SEC_AFTER_LASTEST_TASK = currentTime - task.taskTime 
#	NUMBER_SEC_AFTER_LASTEST_TASK = NUMBER_SEC_AFTER_LASTEST_TASK.days*60*60*24 + NUMBER_SEC_AFTER_LASTEST_TASK.seconds
	
	if request.user.is_superuser and request.method == 'POST':
		save_check_legality(request, task)

	if not request.user.is_superuser:
		NEXT_PAGE = '/main/'
		message = "Редактор ещё будет проверять слова "
		return render_to_response('check.html', locals(), context_instance=RequestContext(request))
	elif request.user.is_superuser and NUMBER_SEC_REDIRECT <= 5:
		NEXT_PAGE = '/main/'
		message = "Редактор ещё будет проверять слова "
		return render_to_response('check.html', locals(), context_instance=RequestContext(request))
	#	NUMBER_SEC_REDIRECT = 4 - NUMBER_SEC_AFTER_LASTEST_TASK
	#	NEXT_PAGE = '/main/'
	#	message = "Вам откроется возможность редактировать слова через"
	#	return render_to_response('check.html', locals())
	else:
		NUMBER_SEC_REDIRECT -= 4
		words = StatisticsWords.objects.filter(gameID = task.gameID, tourID = task.tourID).order_by('-count')
		NEXT_PAGE = '/main/'
		message = "Вам осталось проверять слова слова "
		return render_to_response('check_superuser.html', locals(), context_instance=RequestContext(request))


def count_result(task):
	
	if len(Players.objects.filter(gameID = task.gameID)) == 0:
		return

	while len(ResultTours.objects.filter(gameID = task.gameID, tourID = task.tourID)) == 0:
		time.sleep(1)
	return


def result(request, task):
	currentTimeStart = datetime.datetime.today()
	count_result(task)
	#для html
	currentTime = timezone.now()
	taskNext = Tasks.objects.filter(taskTime__gt = task.taskTime).order_by('taskTime')[0]   
	NUMBER_SEC_REDIRECT = taskNext.taskTime - currentTime
	NUMBER_SEC_REDIRECT = NUMBER_SEC_REDIRECT.days*60*60*24 + NUMBER_SEC_REDIRECT.seconds + 1
	NEXT_PAGE = '/main/'
	isNextTour = False
	if taskNext.action == 'tour':
		isNextTour = True
	title = Titles.objects.get(gameID = task.gameID, tourID = task.tourID)
	message = u"Следующий тур начнется через "
	#messageForTitle = u"Результаты тура " + str(task.tourID + 1) + u" из " + str(task.gameID.toursNumber) + ".\n"
	#messageForTitle += u"Тема тура была " + title.title + u" от автора " + title.user.get_full_name() + "."
	
	tourIDHTML = str(task.tourID + 1)
	toursNumberHTML = str(task.gameID.toursNumber)
	titleHTML = title.title
	autorHTML = title.user.get_full_name()

	playersScore = ResultTours.objects.filter(gameID = task.gameID, tourID = task.tourID).order_by('-score')
	playersScoreTotal = ResultTours.objects.filter(gameID = task.gameID, tourID = task.tourID).order_by('-scoreTotal')
	statisticsWords = StatisticsWords.objects.filter(gameID = task.gameID, tourID = task.tourID).order_by('-count')
	wordsRequestUser = Words.objects.filter(gameID = task.gameID, tourID = task.tourID, user = request.user).values('word')
	wordsRequestUser = map(lambda x: x['word'], wordsRequestUser)
	#players = Players.objects.filter(gameID = task.gameID)
	return render_to_response('result.html', locals(), context_instance=RequestContext(request))
	
	statisticsWordsSet = {}
	for word in statisticsWords:
		statisticsWordsSet[word.word] = word

	nullWord = StatisticsWords(word = "", legal = 1, score = 0)

	tableUserWords = {}
	words = Words.objects.filter(gameID = task.gameID, tourID = task.tourID)
	for word in words:
		if not tableUserWords.has_key(word.user.id):
			tableUserWords[word.user.id] = [ statisticsWordsSet.get(word.word, nullWord) ]
		else:
			tableUserWords[word.user.id] = tableUserWords[word.user.id] + [statisticsWordsSet.get(word.word, nullWord)]

	playersWords = []
	if tableUserWords.has_key(request.user.id):
		playersWords = [(request.user, tableUserWords[request.user.id])]	
		del tableUserWords[request.user.id]
	for x in tableUserWords.items():
		playersWords.append((User.objects.get(id = x[0]), x[1]))
	
	currentTimeFinish = datetime.datetime.today()
	print "count_result " + str(currentTimeFinish - currentTimeStart)
	return render_to_response('result.html', locals(), context_instance=RequestContext(request))

def count_final_result(task):

	if len(Players.objects.filter(gameID = task.gameID)) == 0:
		return
	
	while len(ResultGames.objects.filter(gameID = task.gameID)) == 0 :
		time.sleep(1)
	return 


def final_result(request, task):
	taskDec = task
	taskDec.tourID -= 1
	count_result(taskDec)
	count_final_result(task)
	players = ResultGames.objects.filter(gameID = task.gameID).order_by('-score')
	return render_to_response('final_result.html', locals(), context_instance=RequestContext(request))

@need_login
def main(request):
	currentTime = datetime.datetime.today()
	delta = datetime.timedelta(seconds = 1)
	task = Tasks.objects.filter(taskTime__lte = currentTime).order_by('-taskTime')[0]
	
	print task.action + " | " +  str(task.taskTime)

	if task.action == 'info':
		return information(request, task)
	elif task.action == 'tour':
		return write_words(request, task)
	elif task.action == 'sendWords':
		return wait_words(request, task)
	elif task.action == 'countStatisticsWords':
		return wait_count_base(request, task)
	elif task.action == 'check':
		return check_legality(request, task)
	elif task.action == 'countResult':
		return wait_count_base(request, task)	
	elif task.action == 'watchResult':
		return result(request, task)
	elif task.action == 'endGame':
		return final_result(request, task) 
	error = "А сегодня ничего не поизошло(. Сообщите администратору, если Вы видите это сообщение. Это не правильно."
	return render_to_response('error.html', locals(), context_instance=RequestContext(request))

