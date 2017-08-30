from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.views.decorators.vary import vary_on_headers

from election.dataviews import election_candidacy
from election.dataviews import election_poll
from election.dataviews import election_vote
from election.dataviews import election_showclosed
from election.dataviews import election_stats_download
from election.views import election_add_edit
from election.views import election_list
from election.views import election_view


urlpatterns = [
    url(r'^polity/(?P<polity_id>\d+)/elections/$', never_cache(election_list), name='elections'),
    url(r'^polity/(?P<polity_id>\d+)/election/new/$', election_add_edit, name='election_add_edit'),
    url(r'^polity/(?P<polity_id>\d+)/election/(?P<election_id>\d+)/edit/$', election_add_edit, name='election_add_edit'),
    url(r'^polity/(?P<polity_id>\d+)/election/(?P<election_id>\d+)/$', never_cache(election_view), name='election'),
    url(r'^polity/(?P<polity_id>\d+)/election/(?P<election_id>\d+)/stats-dl/(?P<filename>.+)$', election_stats_download),

    url(r'^api/election/poll/$', never_cache(election_poll)),
    url(r'^api/election/vote/$', never_cache(election_vote)),
    url(r'^api/election/candidacy/$', never_cache(election_candidacy)),
    url(r'^api/election/showclosed/$', election_showclosed),
]
