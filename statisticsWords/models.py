from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, time
from dataGame.models import DataGame

# Create your models here.

class StatisticsWords (models.Model):

	gameID = models.ForeignKey(DataGame)
	tourID = models.IntegerField()
	word = models.CharField(max_length = 100)
	count = models.IntegerField()
	score = models.IntegerField()
	legal = models.IntegerField()

	def __unicode__(self):
		return u'%s legal:%s count: %s tour: %s' % (self.word, str(self.legal), str(self.count), str(self.tourID))



