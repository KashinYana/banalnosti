from django.db import models
from django.contrib.auth.models import User
from dataGame.models import DataGame
from datetime import datetime, time
from django.contrib import admin

# Create your models here.

class Tasks(models.Model):
	taskTime = models.DateTimeField()
	action = models.CharField(max_length = 100)
	gameID = models.ForeignKey(DataGame)
	tourID = models.IntegerField()
	def __unicode__(self):
		return u'%s %s' % (self.action, str(self.tourID))

