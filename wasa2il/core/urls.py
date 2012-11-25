from django.conf.urls.defaults import patterns, include, url
from django.views.generic import ListView, TemplateView, CreateView, UpdateView, DetailView
from django.contrib.auth.decorators import login_required

from core.views import *
from core.json import *
from core.models import Polity, Topic, Issue

urlpatterns = patterns('',
	(r'^$', 'core.views.home'),

	(r'^polities/$',					ListView.as_view(model=Polity, context_object_name="polities")),
	(r'^polity/new/$',					login_required(PolityCreateView.as_view())),

	(r'^polity/(?P<polity>\d+)/document/$',				login_required(DocumentListView.as_view())),
	(r'^polity/(?P<polity>\d+)/document/new/$',			login_required(DocumentCreateView.as_view())),
	(r'^polity/(?P<polity>\d+)/document/(?P<pk>\d+)/$',		login_required(DocumentDetailView.as_view())),
	(r'^polity/(?P<polity>\d+)/document/(?P<pk>\d+)/edit/$',	login_required(DocumentUpdateView.as_view())),

	(r'^polity/(?P<pk>\d+)/edit/$',				login_required(UpdateView.as_view(model=Polity, success_url="/polity/%(id)d/"))),
	(r'^polity/(?P<pk>\d+)/(?P<action>\w+)/$',		login_required(PolityDetailView.as_view())),
	(r'^polity/(?P<pk>\d+)/$',				login_required(PolityDetailView.as_view())),

	(r'^polity/(?P<polity>\d+)/topic/new/$',		login_required(TopicCreateView.as_view())),
	(r'^polity/(?P<polity>\d+)/topic/(?P<pk>\d+)/edit/$',	login_required(UpdateView.as_view(model=Topic, success_url="/polity/%(polity__id)d/topic/%(id)d/"))),
	(r'^polity/(?P<polity>\d+)/topic/(?P<pk>\d+)/$',	login_required(DetailView.as_view(model=Topic, context_object_name="topic"))),

	(r'^polity/(?P<polity>\d+)/topic/(?P<topic>\d+)/issues/new/$',		login_required(IssueCreateView.as_view())),
	(r'^polity/(?P<polity>\d+)/topic/(?P<topic>\d+)/issue/(?P<pk>\d+)/edit/$',	login_required(UpdateView.as_view(model=Issue, success_url="/issue/%(id)d/"))),
	(r'^polity/(?P<polity>\d+)/topic/(?P<topic>\d+)/issue/(?P<pk>\d+)/$',	login_required(IssueDetailView.as_view())),

	(r'^api/document/statement/new/(?P<document>\d+)/(?P<type>\d+)/$', document_statement_new),
	(r'^api/document/propose/(?P<document>\d+)/(?P<val>\d+)/$', document_propose),
	# (r'^api/document/$',

)
