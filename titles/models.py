from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, time
from dataGame.models import DataGame
# Create your models here.

class Titles(models.Model):
	gameID = models.ForeignKey(DataGame)
	tourID = models.IntegerField() 
	user = models.ForeignKey(User)
	title = models.CharField(max_length = 100)

	def __unicode__(self):
		return u'%s %s' % (self.title, str(self.tourID))



