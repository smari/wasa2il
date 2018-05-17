from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

from tasks.models import Task
from tasks.views import (task_list, task_add_edit, task_detail,
                         task_applications, task_user_tasks)

urlpatterns = [
    url(r'^polity/(?P<polity_id>\d+)/tasks/$', task_list, name='tasks'),
    url(r'^polity/(?P<polity_id>\d+)/tasks/(?P<task_id>\d+)/edit/$', task_add_edit, name='task_edit'),
    url(r'^polity/(?P<polity_id>\d+)/tasks/new/$', task_add_edit, name='task_add'),
    url(r'^polity/(?P<polity_id>\d+)/tasks/(?P<task_id>\d+)/$', task_detail, name='task_detail'),
    url(r'^polity/(?P<polity_id>\d+)/tasks/applications/$', task_applications, name='task_applications'),

    url(r'^accounts/profile/(?:(?P<username>[^/]+)/tasks/)?$', task_user_tasks, name='profile_tasks'),
]
