from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

from tasks.models import Task
from tasks.views import task_list

urlpatterns = [
    url(r'^polity/(?P<polity_id>\d+)/tasks/$', task_list, name='tasks'),
#    url(r'^polity/(?P<polity_id>\d+)/tasks/(?P<task_id>\d+)/edit/$', issue_add_edit, name='issue_edit'),
#    url(r'^polity/(?P<polity_id>\d+)/issue/new/(documentcontent/(?P<documentcontent_id>\d+)/)?$', issue_add_edit, name='issue_add'),
#    url(r'^polity/(?P<polity_id>\d+)/issue/(?P<issue_id>\d+)/$', never_cache(issue_view), name='issue'),
]
