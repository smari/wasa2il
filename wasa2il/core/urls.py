from django.conf.urls.defaults import patterns, include, url
from django.views.generic import ListView, TemplateView, CreateView, UpdateView, DetailView
from django.contrib.auth.decorators import login_required

from models import Polity, Topic, Issue

urlpatterns = patterns('',
	(r'^$', 'core.views.home'),

	(r'^polities/$',						login_required(ListView.as_view(model=Polity, context_object_name="polities"))),
	(r'^polity/new/$',						login_required(CreateView.as_view(model=Polity, success_url="/polity/%(id)d/"))),
	(r'^polity/(?P<pk>\d+)/edit/$',					login_required(UpdateView.as_view(model=Polity, success_url="/polity/%(id)d/"))),
	(r'^polity/(?P<pk>\d+)/$',					login_required(DetailView.as_view(model=Polity, context_object_name="polity"))),

	(r'^polity/(?P<polity__pk>\d+)/topics/$',			login_required(ListView.as_view(model=Topic, context_object_name="topics"))),
	(r'^polity/(?P<polity__pk>\d+)/topic/new/$',			login_required(CreateView.as_view(model=Topic, success_url="/topic/%(id)d/"))),
	(r'^polity/(?P<polity__pk>\d+)/topic/(?P<pk>\d+)/edit/$',	login_required(UpdateView.as_view(model=Topic, success_url="/topic/%(id)d/"))),
	(r'^polity/(?P<polity__pk>\d+)/topic/(?P<pk>\d+)/$',		login_required(DetailView.as_view(model=Topic, context_object_name="topic"))),

	(r'^polity/(?P<polity__pk>\d+)/issues/$',			login_required(ListView.as_view(model=Issue, context_object_name="issues"))),
	(r'^polity/(?P<polity__pk>\d+)/issue/new/$',			login_required(CreateView.as_view(model=Issue, success_url="/issue/%(id)d/"))),
	(r'^polity/(?P<polity__pk>\d+)/issue/(?P<pk>\d+)/edit/$',	login_required(UpdateView.as_view(model=Issue, success_url="/issue/%(id)d/"))),
	(r'^polity/(?P<polity__pk>\d+)/issue/(?P<pk>\d+)/$',		login_required(DetailView.as_view(model=Issue, context_object_name="issue"))),
)
