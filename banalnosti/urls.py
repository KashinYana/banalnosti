from django.conf.urls import patterns, include, url
from django.template import RequestContext

from views import home, start, write_words, send_words, results, standings, standings_tour, rules, recount, lock
from users import register, login, logout, profile

from game_views import main
from manage_views import management, create, change_game, add_titles, rejudge, ban
from history_views import history, history_tour, test

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

import settings



urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'banalnosti.views.home', name='home'),
    # url(r'^banalnosti/', include('banalnosti.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
                 {'document_root': settings.MEDIA_ROOT}),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^home/$', home),
    url(r'^$', home),
    url(r'^start/$', start),
    url(r'^write.words/$', write_words),
    url(r'^send.words/$', send_words),
    url(r'^results/$', results),
    url(r'^register/$', register),
    url(r'^login/$', login),
    url(r'^logout/$', logout),
    url(r'^standings/$', standings),
    url(r'^tour/(\d{1,2})$', standings_tour),
    url(r'^profile/$', profile),
    url(r'^rules/$', rules),
    url(r'^history/$', history),
    url(r'^history/(\d{1,600})/(\d{1,600})/$', history_tour),
    url(r'^recount/$', recount),
    url(r'^lock/$', lock),
    url(r'^management/$', management),
    url(r'^create/$', create),
    url(r'^main/$', main),
    url(r'^change_game/(\d{1,600})/$', change_game),
    url(r'^add_titles/(\d{1,600})/$', add_titles),
    url(r'^rejudge/(\d{1,600})/$', rejudge),
    url(r'^ban/(\d{1,600})/$', ban),
    url(r'^test/$', test),
    #url(r'^accounts/login/$',  login),
    #url(r'^accounts/login/$',  login),
    #url(r'^accounts/logout/$', logout),
)
