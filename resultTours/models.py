from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, time
from dataGame.models import DataGame

# Create your models here.

class ResultTours (models.Model):
	
	gameID = models.ForeignKey(DataGame)
	tourID = models.IntegerField()
	user = models.ForeignKey(User)
	score = models.IntegerField()
	scoreTotal = models.IntegerField()

	def __unicode__(self):
		return u'%s  tour: %s score: %s // %s' % (self.user.get_full_name(), str(self.tourID), str(self.score), str(self.scoreTotal))



