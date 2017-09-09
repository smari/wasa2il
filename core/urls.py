from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.views.decorators.cache import never_cache
from django.views.decorators.vary import vary_on_headers

from django.conf import settings

from core.ajax.issue import issue_comment_send, issue_poll, issue_vote
from core.ajax.document import (
    document_propose, document_propose_change, render_markdown,
    documentcontent_render_diff
)
from core.views import *
from core import views as core_views
from core.ajax import *
from core.models import Issue


urlpatterns = [
    url(r'^$', core_views.home),

    url(r'^issue/(?P<pk>\d+)/edit/$', login_required(UpdateView.as_view(model=Issue, success_url="/issue/%(id)d/"))),
    url(r'^issue/(?P<pk>\d+)/$', IssueDetailView.as_view()),

    url(r'^polity/(?P<polity>\d+)/issues/open/$', IssueOpenListView.as_view(), name='polity_issues_new'),
    url(r'^polity/(?P<polity>\d+)/issue/new/(documentcontent/(?P<documentcontent>\d+)/)?$', login_required(IssueCreateView.as_view())),

    url(r'^search/$', SearchListView.as_view()),

    url(r'^polity/(?P<polity>\d+)/document/$', login_required(DocumentListView.as_view())),
    url(r'^polity/(?P<polity>\d+)/document/new/$', login_required(DocumentCreateView.as_view())),
    url(r'^polity/(?P<polity>\d+)/document/(?P<pk>\d+)/$', DocumentDetailView.as_view()),
    # (r'^polity/(?P<polity>\d+)/document/(?P<pk>\d+)/edit/$', login_required(DocumentUpdateView.as_view())),

    url(r'^api/issue/comment/send/$', never_cache(issue_comment_send)),
    url(r'^api/issue/poll/$', never_cache(issue_poll)),
    url(r'^api/issue/vote/$', never_cache(issue_vote)),

    url(r'^api/document/propose/(?P<document>\d+)/(?P<state>\d+)/$', document_propose),
    url(r'^api/document/propose-change/$', document_propose_change),
    url(r'^api/document/render-markdown/$', render_markdown),

    url(r'^api/documentcontent/render-diff/$', documentcontent_render_diff),
]
