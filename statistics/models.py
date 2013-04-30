from django.contrib.auth.models import User
from django.db import models

class PointTour(models.Model):
	user = models.ForeignKey(User)
	point = models.IntegerField()
	id_tour = models.IntegerField()
	def __unicode__(self):
		return u'%s %s %s' % (self.user.username, str(self.id_tour), str(self.point))
