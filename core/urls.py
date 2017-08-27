from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.views.decorators.cache import never_cache
from django.views.decorators.vary import vary_on_headers
from django.views.generic import ListView, UpdateView, DetailView

from django.conf import settings

from core.ajax.issue import issue_comment_send, issue_poll, issue_vote
from core.ajax.document import (
    document_propose, document_propose_change, render_markdown,
    documentcontent_render_diff
)
from core.ajax.topic import topic_poll
from core.views import *
from core import views as core_views
from core.ajax import *
from core.models import Polity, Topic, Issue


urlpatterns = [
    url(r'^$', core_views.home),
    url(r'^polities/$', PolityListView.as_view()),
    url(r'^polity/new/$', login_required(PolityCreateView.as_view())),

    url(r'^issue/(?P<pk>\d+)/edit/$', login_required(UpdateView.as_view(model=Issue, success_url="/issue/%(id)d/"))),
    url(r'^issue/(?P<pk>\d+)/$', IssueDetailView.as_view()),

    url(r'^polity/(?P<polity>\d+)/issues/open/$', IssueOpenListView.as_view(), name='polity_issues_new'),
    url(r'^polity/(?P<polity>\d+)/issue/new/(documentcontent/(?P<documentcontent>\d+)/)?$', login_required(IssueCreateView.as_view())),

    url(r'^search/$', SearchListView.as_view()),

    url(r'^polity/(?P<polity>\d+)/document/$', login_required(DocumentListView.as_view())),
    url(r'^polity/(?P<polity>\d+)/document/new/$', login_required(DocumentCreateView.as_view())),
    url(r'^polity/(?P<polity>\d+)/document/(?P<pk>\d+)/$', DocumentDetailView.as_view()),
    # (r'^polity/(?P<polity>\d+)/document/(?P<pk>\d+)/edit/$', login_required(DocumentUpdateView.as_view())),

    url(r'^polity/(?P<polity>\d+)/election/$',
        cache_page(60*1)(vary_on_headers('Cookie')(
            ElectionListView.as_view()))),
    url(r'^polity/(?P<polity>\d+)/election/new/$',
        login_required(ElectionCreateView.as_view())),
    url(r'^polity/(?P<polity>\d+)/election/(?P<pk>\d+)/$', never_cache(ElectionDetailView.as_view())),
    url(r'^polity/(?P<polity>\d+)/election/(?P<pk>\d+)/stats-dl/(?P<filename>.+)$',
        election_stats_download),
#   (r'^polity/(\d+)/election/(?P<pk>\d+)/ballots/$', election_ballots),

    url(r'^polity/(?P<pk>\d+)/edit/$', login_required(UpdateView.as_view(model=Polity, success_url="/polity/%(id)d/"))),
    url(r'^polity/(?P<pk>\d+)/(?P<action>\w+)/$', login_required(PolityDetailView.as_view())),
    url(r'^polity/(?P<pk>\d+)/$',
        cache_page(60*5)(vary_on_headers('Cookie')(
            PolityDetailView.as_view())), name='polity_detail'),
    url(r'^polity/(?P<polity>\d+)/topic/new/$', login_required(TopicCreateView.as_view())),
    url(r'^polity/(?P<polity>\d+)/topic/(?P<pk>\d+)/edit/$', login_required(UpdateView.as_view(model=Topic, success_url="/polity/%(polity__id)d/topic/%(id)d/"))),
    url(r'^polity/(?P<polity>\d+)/topic/(?P<pk>\d+)/$', TopicDetailView.as_view(), name='polity_topic_detail'),

    url(r'^api/topic/star/$', topic_star),
    url(r'^api/topic/showstarred/$', topic_showstarred),

    url(r'^api/issue/comment/send/$', never_cache(issue_comment_send)),
    url(r'^api/issue/poll/$', never_cache(issue_poll)),
    url(r'^api/issue/vote/$', never_cache(issue_vote)),

    url(r'^api/topic/poll/$', never_cache(topic_poll)),

    url(r'^api/election/poll/$', never_cache(election_poll)),
    url(r'^api/election/vote/$', never_cache(election_vote)),
    url(r'^api/election/candidacy/$', never_cache(election_candidacy)),
    url(r'^api/election/showclosed/$', election_showclosed),

    url(r'^api/document/propose/(?P<document>\d+)/(?P<state>\d+)/$', document_propose),
    url(r'^api/document/propose-change/$', document_propose_change),
    url(r'^api/document/render-markdown/$', render_markdown),

    url(r'^api/documentcontent/render-diff/$', documentcontent_render_diff),
]
