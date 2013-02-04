from django.conf.urls.defaults import patterns, include, url
from django.views.generic import ListView, TemplateView, CreateView, UpdateView, DetailView
from django.contrib.auth.decorators import login_required

from forum.views import *
# from forum.json import *
from forum.models import *

urlpatterns = patterns('',
	(r'^polity/(?P<polity>\d+)/forum/new/$',		login_required(ForumCreateView.as_view())),
	(r'^forum/(?P<pk>\d+)/$',				login_required(ForumDetailView.as_view())),
	(r'^forum/(?P<forum>\d+)/discussion/new/$',		login_required(DiscussionCreateView.as_view())),
	(r'^forum/(?P<forum>\d+)/discussion/(?P<pk>\d+)/$',	login_required(DiscussionDetailView.as_view())),
)
