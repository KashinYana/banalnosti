# Create your models here.

from django.contrib.auth.models import User
from dataGame.models import DataGame
from django.db import models

class Player(models.Model):
    name = models.CharField(max_length = 50)
    point = models.IntegerField()
    def __unicode__(self):
        return u'%s %s' % (self.name, self.point)    

class CurrentGame(models.Model):
    id_tour = models.IntegerField()
    name = models.ForeignKey(Player)
    word = models.CharField(max_length = 50)
    validity = models.IntegerField()
    def __unicode__(self):
        return u'%s %s %s' % (self.name, self.id_tour, self.word)

class PointTour(models.Model):
	player = models.ForeignKey(User)
	point = models.IntegerField()
	id_tour = models.IntegerField()
	def __unicode__(self):
		return u'%s %s %s' % (self.player.username, str(self.id_tour), str(self.point))

class Words(models.Model):
    gameID = models.ForeignKey(DataGame)
    tourID = models.IntegerField()
    user = models.ForeignKey(User)
    word = models.CharField(max_length = 100)
    def __unicode__(self):
        return u'tour: %s word:%s user: %s' % (str(self.tourID), self.word, self.user.first_name)

