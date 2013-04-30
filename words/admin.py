from django.contrib import admin
from words.models import Player, CurrentGame, PointTour, Words

admin.site.register(CurrentGame)
admin.site.register(Player)
admin.site.register(PointTour)
admin.site.register(Words)



