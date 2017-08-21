from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from forum.views import *
from forum.json import *
from forum.models import *

urlpatterns = [
    url(r'^polity/(?P<polity>\d+)/forum/new/$',        login_required(ForumCreateView.as_view())),
    url(r'^forum/(?P<pk>\d+)/$',                login_required(ForumDetailView.as_view())),
    url(r'^forum/(?P<forum>\d+)/discussion/new/$',        login_required(DiscussionCreateView.as_view())),
    url(r'^forum/(?P<forum>\d+)/discussion/(?P<pk>\d+)/$',    login_required(DiscussionDetailView.as_view())),

    url(r'^api/discussion/comment/send/$', discussion_comment_send),
    url(r'^api/discussion/poll/$', discussion_poll),
]
