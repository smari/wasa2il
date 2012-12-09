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

	(r'^polity/(?P<polity>\d+)/meeting/$',				login_required(MeetingListView.as_view())),
	(r'^polity/(?P<polity>\d+)/meeting/new/$',			login_required(MeetingCreateView.as_view())),
	(r'^polity/(?P<polity>\d+)/meeting/(?P<pk>\d+)/$',		login_required(MeetingDetailView.as_view())),
	(r'^polity/(?P<polity>\d+)/meeting/(?P<pk>\d+)/edit/$',		login_required(MeetingUpdateView.as_view())),

	(r'^polity/(?P<pk>\d+)/edit/$',				login_required(UpdateView.as_view(model=Polity, success_url="/polity/%(id)d/"))),
	(r'^polity/(?P<pk>\d+)/(?P<action>\w+)/$',		login_required(PolityDetailView.as_view())),
	(r'^polity/(?P<pk>\d+)/$',				login_required(PolityDetailView.as_view())),

	(r'^polity/(?P<polity>\d+)/topic/new/$',		login_required(TopicCreateView.as_view())),
	(r'^polity/(?P<polity>\d+)/topic/(?P<pk>\d+)/edit/$',	login_required(UpdateView.as_view(model=Topic, success_url="/polity/%(polity__id)d/topic/%(id)d/"))),
	(r'^polity/(?P<polity>\d+)/topic/(?P<pk>\d+)/$',	login_required(DetailView.as_view(model=Topic, context_object_name="topic"))),

	(r'^polity/(?P<polity>\d+)/topic/(?P<topic>\d+)/issues/new/$',		login_required(IssueCreateView.as_view())),
	(r'^polity/(?P<polity>\d+)/topic/(?P<topic>\d+)/issue/(?P<pk>\d+)/edit/$',	login_required(UpdateView.as_view(model=Issue, success_url="/issue/%(id)d/"))),
	(r'^polity/(?P<polity>\d+)/topic/(?P<topic>\d+)/issue/(?P<pk>\d+)/$',	login_required(IssueDetailView.as_view())),

	(r'^api/polity/membershipvote/$', polity_membershipvote),
	(r'^api/topic/star/$', topic_star),
	(r'^api/document/statement/new/(?P<document>\d+)/(?P<type>\d+)/$', document_statement_new),
	(r'^api/document/propose/(?P<document>\d+)/(?P<val>\d+)/$', document_propose),
	(r'^api/meeting/attend/(?P<meeting>\d+)/$', meeting_attend),
	(r'^api/meeting/poll/$', meeting_poll),
	(r'^api/meeting/start/$', meeting_start),
	(r'^api/meeting/end/$', meeting_end),
	(r'^api/meeting/agenda/open/$', meeting_agenda_open),
	(r'^api/meeting/agenda/close/$', meeting_agenda_close),
	(r'^api/meeting/agenda/add/$', meeting_agenda_add),
	(r'^api/meeting/agenda/remove/$', meeting_agenda_remove),
	(r'^api/meeting/agenda/reorder/$', meeting_agenda_reorder),
	(r'^api/meeting/agenda/next/$', meeting_agenda_next),
	(r'^api/meeting/agenda/prev/$', meeting_agenda_prev),
	(r'^api/meeting/intervention/next/$', meeting_intervention_next),
	(r'^api/meeting/intervention/prev/$', meeting_intervention_prev),
	(r'^api/meeting/intervention/add/$', meeting_intervention_add),
	# (r'^api/document/$',

)
