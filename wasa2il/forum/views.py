from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.template import RequestContext
from django.db.models import Q
from django.contrib.auth.decorators import login_required
import settings

from forum.models import *
from forum.forms import *


class ForumCreateView(CreateView):
	context_object_name = "forum"
	template_name = "forum/forum_form.html"
	form_class = ForumForm
	success_url="/forum/%(id)d/"

	def dispatch(self, *args, **kwargs):
		self.polity = get_object_or_404(Polity, id=kwargs["polity"])
		return super(ForumCreateView, self).dispatch(*args, **kwargs)

	def get_context_data(self, *args, **kwargs):
		context_data = super(ForumCreateView, self).get_context_data(*args, **kwargs)
		context_data.update({'polity': self.polity})
		return context_data

	def form_valid(self, form):
		self.object = form.save(commit=False)
		self.object.polity = self.polity
		self.object.save()

                return HttpResponseRedirect(self.get_success_url())


class ForumDetailView(DetailView):
	model = Forum
	context_object_name = "forum"
	template_name = "forum/forum_detail.html"

	def get_context_data(self, *args, **kwargs):
		context_data = super(ForumDetailView, self).get_context_data(*args, **kwargs)

		context_data.update({'polity': self.object.polity})
		return context_data


class DiscussionCreateView(CreateView):
	context_object_name = "discussion"
	template_name = "forum/discussion_form.html"
	form_class = DiscussionForm
	success_url="/forum/%(forum)d/discussion/%(id)d/"

	def dispatch(self, *args, **kwargs):
		self.forum = get_object_or_404(Forum, id=kwargs["forum"])
		print "FOO:", self.forum
		self.success_url = "/forum/" + str(self.forum.id) + "/discussion/%(id)d/"
		return super(DiscussionCreateView, self).dispatch(*args, **kwargs)

	def get_context_data(self, *args, **kwargs):
		context_data = super(DiscussionCreateView, self).get_context_data(*args, **kwargs)
		context_data.update({'polity': self.forum.polity, 'forum': self.forum})
		return context_data

	def form_valid(self, form):
		self.object = form.save(commit=False)
		self.object.started_by = self.request.user
		self.object.forum = self.forum
		self.object.save()

                return HttpResponseRedirect(self.get_success_url())


class DiscussionDetailView(DetailView):
	model = Discussion
	context_object_name = "discussion"
	template_name = "forum/discussion_detail.html"

	def get_context_data(self, *args, **kwargs):
		context_data = super(DiscussionDetailView, self).get_context_data(*args, **kwargs)
		context_data.update({'polity': self.object.forum.polity, "forum": self.object.forum})
		return context_data

