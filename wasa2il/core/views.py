from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from core.models import Polity, Topic, Issue, Vote

def home(request):
	ctx = {}

	return render_to_response("home.html", ctx)


class TopicListView(ListView):
	context_object_name = "topics"
	template_name = "core/topic_list.html"

	def get_queryset(self):
		polity = get_object_or_404(Topic, id=self.kwargs["polity"])
		return Topic.objects.filter(polity=polity)


class TopicCreateView(CreateView):
	context_object_name = "topic"
	template_name = "core/topic_form.html"

	def get_queryset(self):
		polity = get_object_or_404(Topic, id=self.kwargs["polity"])
		return Topic.objects.filter(polity=polity)
