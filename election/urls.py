from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.views.decorators.cache import never_cache
from django.views.decorators.vary import vary_on_headers

from election.dataviews import election_candidacy
from election.dataviews import election_poll
from election.dataviews import election_vote
from election.dataviews import election_showclosed
from election.dataviews import election_stats_download
from election.views import ElectionCreateView
from election.views import ElectionListView
from election.views import ElectionDetailView


urlpatterns = [

    url(r'^polity/(?P<polity>\d+)/election/$', cache_page(60*1)(vary_on_headers('Cookie')(ElectionListView.as_view()))),
    url(r'^polity/(?P<polity>\d+)/election/new/$', login_required(ElectionCreateView.as_view())),
    url(r'^polity/(?P<polity>\d+)/election/(?P<pk>\d+)/$', never_cache(ElectionDetailView.as_view())),
    url(r'^polity/(?P<polity>\d+)/election/(?P<pk>\d+)/stats-dl/(?P<filename>.+)$', election_stats_download),

    url(r'^api/election/poll/$', never_cache(election_poll)),
    url(r'^api/election/vote/$', never_cache(election_vote)),
    url(r'^api/election/candidacy/$', never_cache(election_candidacy)),
    url(r'^api/election/showclosed/$', election_showclosed),
]
