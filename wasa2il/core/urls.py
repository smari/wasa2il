from django.conf.urls.defaults import patterns, include, url
from django.views.generic import ListView, TemplateView, CreateView, UpdateView, DetailView
from django.contrib.auth.decorators import login_required

from core.views import TopicListView, TopicCreateView, IssueCreateView, IssueDetailView
from core.models import Polity, Topic, Issue

urlpatterns = patterns('',
	(r'^$', 'core.views.home'),

	(r'^polities/$',					login_required(ListView.as_view(model=Polity, context_object_name="polities"))),
	(r'^polity/new/$',					login_required(CreateView.as_view(model=Polity, success_url="/polity/%(id)d/"))),
	(r'^polity/(?P<pk>\d+)/edit/$',				login_required(UpdateView.as_view(model=Polity, success_url="/polity/%(id)d/"))),
	(r'^polity/(?P<pk>\d+)/$',				login_required(DetailView.as_view(model=Polity, context_object_name="polity"))),

	(r'^polity/(?P<polity>\d+)/topic/new/$',		login_required(TopicCreateView.as_view())),
	(r'^polity/(?P<polity>\d+)/topic/(?P<pk>\d+)/edit/$',	login_required(UpdateView.as_view(model=Topic, success_url="/polity/%(polity__id)d/topic/%(id)d/"))),
	(r'^polity/(?P<polity>\d+)/topic/(?P<pk>\d+)/$',	login_required(DetailView.as_view(model=Topic, context_object_name="topic"))),

	(r'^polity/(?P<polity>\d+)/topic/(?P<topic>\d+)/issues/new/$',		login_required(IssueCreateView.as_view())),
	(r'^polity/(?P<polity>\d+)/topic/(?P<topic>\d+)/issue/(?P<pk>\d+)/edit/$',	login_required(UpdateView.as_view(model=Issue, success_url="/issue/%(id)d/"))),
	(r'^polity/(?P<polity>\d+)/topic/(?P<topic>\d+)/issue/(?P<pk>\d+)/$',	login_required(IssueDetailView.as_view())),
)
