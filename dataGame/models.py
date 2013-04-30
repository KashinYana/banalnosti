from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, time

# Create your models here.

class DataGame(models.Model):
	start = models.DateTimeField()
	toursNumber = models.IntegerField()
	lenWriteWords = models.IntegerField()
	lenWatchResult = models.IntegerField()
	lenChecking = models.IntegerField()
	lenWaitWords = models.IntegerField()

	
	def __unicode__(self):
		return u'%s' % (self.start.ctime())



