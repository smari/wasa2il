from django.shortcuts import render
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import ListView

from topic.forms import TopicForm
from topic.models import Topic


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
    success_url = "/polity/%(polity)d/topic/%(id)d/"

    def dispatch(self, *args, **kwargs):
        self.polity = get_object_or_404(Polity, id=kwargs["polity"])
        self.success_url = "/polity/" + str(self.polity.id) + "/topic/%(id)d/"
        return super(TopicCreateView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context_data = super(TopicCreateView, self).get_context_data(*args, **kwargs)
        context_data.update({'polity': self.polity})
        context_data['user_is_member'] = self.polity.is_member(self.request.user)
        return context_data

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.polity = self.polity
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class TopicDetailView(DetailView):
    model = Topic
    context_object_name = "topic"
    template_name = "core/topic_detail.html"

    def get_context_data(self, *args, **kwargs):
        context_data = super(TopicDetailView, self).get_context_data(*args, **kwargs)
        context_data["polity"] = self.object.polity
        context_data['user_is_member'] = self.object.polity.is_member(self.request.user)
        return context_data

