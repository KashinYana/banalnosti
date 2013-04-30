from django.db import models

class Settings(models.Model):
    name = models.CharField(max_length=50)
    valueInt = models.IntegerField(blank=True, null=True)
    valueString = models.CharField(max_length = 500, blank=True)
    def __unicode__(self):
        return u'%s %s %s' % (self.name, self.valueInt, self.valueString)
