from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from topic.dataviews import topic_showstarred
from topic.dataviews import topic_star
from topic.views import topic_add_edit
from topic.views import topic_view
from topic.views import topic_list


urlpatterns = [
    url(r'^polity/(?P<polity_id>\d+)/topic/new/$', topic_add_edit, name='topic_add'),
    url(r'^polity/(?P<polity_id>\d+)/topic/(?P<topic_id>\d+)/edit/$', topic_add_edit, name='topic_edit'),
    url(r'^polity/(?P<polity_id>\d+)/topic/(?P<topic_id>\d+)/$', topic_view, name='topic'),
    url(r'^polity/(?P<polity_id>\d+)/topics/$', topic_list, name='topics'),


    url(r'^api/topic/star/$', topic_star),
    url(r'^api/topic/showstarred/$', topic_showstarred),
]
