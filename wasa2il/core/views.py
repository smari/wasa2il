from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from core.models import Polity, Topic, Issue, Vote
from core.forms import *

def home(request):
	ctx = {}
	if request.user.is_authenticated():
		# Get some context vars (tempoarily just fetch the first one)
		ctx['mainPolity'] = Polity.objects.all()[0]
		ctx['polities'] = Polity.objects.filter(members=request.user)
		ctx['topics' ] = ctx['mainPolity'].topic_set.all()
		return render_to_response("home.html", ctx)
	else:
	

		return render_to_response("hom01.html", ctx)


def profile(request):
	ctx = {}

	return render_to_response("profile.html", ctx)


class TopicListView(ListView):
	context_object_name = "topics"
	template_name = "core/topic_list.html"

	def get_queryset(self):
		polity = get_object_or_404(Polity, polity=self.kwargs["polity"])
		return Topic.objects.filter(polity=polity)


class TopicCreateView(CreateView):
	context_object_name = "topic"
	template_name = "core/topic_form.html"
	form_class = TopicForm
	success_url="/polity/%(polity)d/topic/%(id)d/"

	def dispatch(self, *args, **kwargs):
		self.polity = get_object_or_404(Topic, id=kwargs["polity"])
		self.success_url = "/polity/" + str(self.polity.id) + "/topic/%(id)d/"
		return super(TopicCreateView, self).dispatch(*args, **kwargs)

	def get_context_data(self, *args, **kwargs):
		context_data = super(TopicCreateView, self).get_context_data(*args, **kwargs)
		context_data.update({'polity': self.topic.polity})
		return context_data

	def form_valid(self, form):
		self.object = form.save(commit=False)
		self.object.polity = self.polity
		self.object.save()
		return HttpResponseRedirect(self.get_success_url())


class IssueCreateView(CreateView):
	context_object_name = "issue"
	template_name = "core/issue_form.html"
	form_class = IssueForm
	success_url="/polity/%(polity)d/topic/%(id)d/"

	def dispatch(self, *args, **kwargs):
		self.polity = get_object_or_404(Polity, id=kwargs["polity"])
		self.topic = get_object_or_404(Topic, id=kwargs["topic"])
		self.success_url = "/polity/" + str(self.polity.id) + "/topic/" + str(self.topic.id) + "/issue/%(id)d/"
		return super(IssueCreateView, self).dispatch(*args, **kwargs)

	def get_context_data(self, *args, **kwargs):
		context_data = super(IssueCreateView, self).get_context_data(*args, **kwargs)
		context_data.update({'polity': self.topic.polity, 'topic': self.topic})
		return context_data

	def form_valid(self, form):
		self.object = form.save(commit=False)
		self.object.save()
		self.object.topics.add(self.topic)
		return HttpResponseRedirect(self.get_success_url())


class IssueDetailView(DetailView):
	model = Issue
	context_object_name = "issue"
	template_name = "core/issue_detail.html"

	def get_context_data(self, *args, **kwargs):
		context_data = super(IssueDetailView, self).get_context_data(*args, **kwargs)
		context_data.update({'comment_form': CommentForm()})
		return context_data

