from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, time
from dataGame.models import DataGame

# Create your models here.

class Players (models.Model):
	
	gameID = models.ForeignKey(DataGame)
	user = models.ForeignKey(User)
	
	def __unicode__(self):
		return u'%s ' % (self.user.get_full_name())



