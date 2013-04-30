from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class VersionTitles(models.Model):
	title = models.CharField(max_length = 50)
	user = 	models.ForeignKey(User)
	mark = models.IntegerField()
	def __unicode__(self):
		return u'%s %s' % (self.title, str(self.mark))

