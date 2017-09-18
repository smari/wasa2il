from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.generic import UpdateView

from topic.dataviews import topic_showstarred
from topic.dataviews import topic_star
from topic.models import Topic
from topic.views import TopicDetailView
from topic.views import TopicCreateView


urlpatterns = [
    url(r'^polity/(?P<polity>\d+)/topic/new/$', login_required(TopicCreateView.as_view())),
    url(r'^polity/(?P<polity>\d+)/topic/(?P<pk>\d+)/edit/$', login_required(UpdateView.as_view(model=Topic, success_url="/polity/%(polity__id)d/topic/%(id)d/"))),
    url(r'^polity/(?P<polity>\d+)/topic/(?P<pk>\d+)/$', TopicDetailView.as_view(), name='polity_topic_detail'),

    url(r'^api/topic/star/$', topic_star),
    url(r'^api/topic/showstarred/$', topic_showstarred),
]
