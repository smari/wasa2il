from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.views.generic import UpdateView

from issue.dataviews import issue_comment_send
from issue.dataviews import issue_poll
from issue.dataviews import issue_vote
#from issue.dataviews import document_propose
from issue.dataviews import document_propose_change
from issue.dataviews import documentcontent_render_diff
from issue.dataviews import render_markdown
from issue.models import Issue
from issue.views import DocumentCreateView
from issue.views import DocumentListView
from issue.views import DocumentDetailView
from issue.views import IssueCreateView
from issue.views import IssueDetailView
from issue.views import IssueOpenListView
from issue.views import SearchListView

urlpatterns = [
    url(r'^issue/(?P<pk>\d+)/edit/$', login_required(UpdateView.as_view(model=Issue, success_url="/issue/%(id)d/"))),
    url(r'^issue/(?P<pk>\d+)/$', IssueDetailView.as_view()),

    url(r'^polity/(?P<polity>\d+)/issues/open/$', IssueOpenListView.as_view(), name='polity_issues_new'),
    url(r'^polity/(?P<polity>\d+)/issue/new/(documentcontent/(?P<documentcontent>\d+)/)?$', login_required(IssueCreateView.as_view())),

    url(r'^search/$', SearchListView.as_view()),

    url(r'^polity/(?P<polity>\d+)/document/$', login_required(DocumentListView.as_view())),
    url(r'^polity/(?P<polity>\d+)/document/new/$', login_required(DocumentCreateView.as_view())),
    url(r'^polity/(?P<polity>\d+)/document/(?P<pk>\d+)/$', DocumentDetailView.as_view()),

    url(r'^api/issue/comment/send/$', never_cache(issue_comment_send)),
    url(r'^api/issue/poll/$', never_cache(issue_poll)),
    url(r'^api/issue/vote/$', never_cache(issue_vote)),

    url(r'^api/document/propose-change/$', document_propose_change),
    url(r'^api/document/render-markdown/$', render_markdown),

    url(r'^api/documentcontent/render-diff/$', documentcontent_render_diff),
]
