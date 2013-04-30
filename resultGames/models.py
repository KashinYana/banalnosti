from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, time
from dataGame.models import DataGame

# Create your models here.

class ResultGames (models.Model):

	gameID = models.ForeignKey(DataGame)
	user = models.ForeignKey(User)
	score = models.IntegerField()

	def __unicode__(self):
		return u'%s %s' % (self.user.get_full_name(), str(self.score))



