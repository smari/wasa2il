from django.conf.urls.defaults import patterns, include, url
from django.views.generic import ListView, TemplateView, CreateView, UpdateView
from django.contrib.auth.decorators import login_required


urlpatterns = patterns('',
	(r'^$', 'core.views.home'),

	(r'^polity/$',			login_required(ListView.as_view(model=Polity, context_object_name="polity"))),
	(r'^polity/new/$',		login_required(CreateView.as_view(model=Polity, success_url="/polity/%(id)d/"))),
	(r'^polity/(?P<pk>\d+)/edit/$',	login_required(UpdateView.as_view(model=Polity, success_url="/polity/%(id)d/"))),
	(r'^polity/(?P<pk>\d+)/$',	login_required(DetailView.as_view(model=Polity, context_object_name="polity"))),

	(r'^topic/$',			login_required(ListView.as_view(model=Topic, context_object_name="topic"))),
	(r'^topic/new/$',		login_required(CreateView.as_view(model=Topic, success_url="/topic/%(id)d/"))),
	(r'^topic/(?P<pk>\d+)/edit/$',	login_required(UpdateView.as_view(model=Topic, success_url="/topic/%(id)d/"))),
	(r'^topic/(?P<pk>\d+)/$',	login_required(DetailView.as_view(model=Topic, context_object_name="topic"))),

	(r'^issue/$',			login_required(ListView.as_view(model=Issue, context_object_name="issue"))),
	(r'^issue/new/$',		login_required(CreateView.as_view(model=Issue, success_url="/issue/%(id)d/"))),
	(r'^issue/(?P<pk>\d+)/edit/$',	login_required(UpdateView.as_view(model=Issue, success_url="/issue/%(id)d/"))),
	(r'^issue/(?P<pk>\d+)/$',	login_required(DetailView.as_view(model=Issue, context_object_name="issue"))),
)
