from django.conf.urls import patterns
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.views.generic import ListView
from django.views.generic import UpdateView
from django.views.generic import DetailView

from django.conf import settings

from core.ajax.issue import issue_comment_send
from core.ajax.issue import issue_poll
from core.ajax.issue import issue_vote
from core.ajax.document import document_propose
from core.ajax.document import document_propose_change
from core.ajax.document import render_markdown
from core.ajax.document import documentcontent_render_diff
from core.views import *
from core.ajax import *
from core.models import Polity
from core.models import Topic
from core.models import Issue
from core.models import Delegate


urlpatterns = patterns('',
    (r'^$', 'core.views.home'),
    (r'^polities/$', ListView.as_view(model=Polity, context_object_name="polities")),
    (r'^polity/new/$', login_required(PolityCreateView.as_view())),

    (r'^issue/(?P<pk>\d+)/edit/$', login_required(UpdateView.as_view(model=Issue, success_url="/issue/%(id)d/"))),
    (r'^issue/(?P<pk>\d+)/$', IssueDetailView.as_view()),

    url(r'^polity/(?P<polity>\d+)/issues/open/$', IssueOpenListView.as_view(), name='polity_issues_new'),
    (r'^polity/(?P<polity>\d+)/issue/new/(documentcontent/(?P<documentcontent>\d+)/)?$', login_required(IssueCreateView.as_view())),

    (r'^search/$', SearchListView.as_view()),

    (r'^polity/(?P<polity>\d+)/document/$', login_required(DocumentListView.as_view())),
    (r'^polity/(?P<polity>\d+)/document/new/$', login_required(DocumentCreateView.as_view())),
    (r'^polity/(?P<polity>\d+)/document/(?P<pk>\d+)/$', DocumentDetailView.as_view()),
    # (r'^polity/(?P<polity>\d+)/document/(?P<pk>\d+)/edit/$', login_required(DocumentUpdateView.as_view())),

    (r'^polity/(?P<polity>\d+)/election/$',
        cache_page(60*1)(vary_on_headers('Cookie')(
            ElectionListView.as_view()))),
    (r'^polity/(?P<polity>\d+)/election/new/$',
        login_required(ElectionCreateView.as_view())),
    (r'^polity/(?P<polity>\d+)/election/(?P<pk>\d+)/$',
        ElectionDetailView.as_view()),
    (r'^polity/(?P<polity>\d+)/election/(?P<pk>\d+)/stats-dl/(?P<filename>.+)$',
        election_stats_download),
#   (r'^polity/(\d+)/election/(?P<pk>\d+)/ballots/$', election_ballots),

    (r'^polity/(?P<pk>\d+)/edit/$', login_required(UpdateView.as_view(model=Polity, success_url="/polity/%(id)d/"))),
    (r'^polity/(?P<pk>\d+)/(?P<action>\w+)/$', login_required(PolityDetailView.as_view())),
    (r'^polity/(?P<pk>\d+)/$',
        cache_page(60*5)(vary_on_headers('Cookie')(
            PolityDetailView.as_view()))),
    (r'^polity/(?P<polity>\d+)/topic/new/$', login_required(TopicCreateView.as_view())),
    (r'^polity/(?P<polity>\d+)/topic/(?P<pk>\d+)/edit/$', login_required(UpdateView.as_view(model=Topic, success_url="/polity/%(polity__id)d/topic/%(id)d/"))),
    (r'^polity/(?P<polity>\d+)/topic/(?P<pk>\d+)/$', TopicDetailView.as_view()),

#   (r'^delegation/(?P<pk>\d+)/$', login_required(DetailView.as_view(model=Delegate, context_object_name="delegation"))),

    (r'^api/topic/star/$', topic_star),
    (r'^api/topic/showstarred/$', topic_showstarred),

    (r'^api/issue/comment/send/$', issue_comment_send),
    (r'^api/issue/poll/$', issue_poll),
    (r'^api/issue/vote/$', issue_vote),

    (r'^api/election/poll/$', election_poll),
    (r'^api/election/vote/$', election_vote),
    (r'^api/election/candidacy/$', election_candidacy),
    (r'^api/election/showclosed/$', election_showclosed),

    (r'^api/document/propose/(?P<document>\d+)/(?P<state>\d+)/$', document_propose),
    (r'^api/document/propose-change/$', document_propose_change),
    (r'^api/document/render-markdown/$', render_markdown),

    (r'^api/documentcontent/render-diff/$', documentcontent_render_diff),
)

