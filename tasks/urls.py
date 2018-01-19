from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

from tasks.models import Task
from tasks.views import task_list, task_add_edit

urlpatterns = [
    url(r'^polity/(?P<polity_id>\d+)/tasks/$', task_list, name='tasks'),
    url(r'^polity/(?P<polity_id>\d+)/tasks/(?P<task_id>\d+)/edit/$', task_add_edit, name='task_edit'),
    url(r'^polity/(?P<polity_id>\d+)/tasks/new/$', task_add_edit, name='task_add'),
    # url(r'^polity/(?P<polity_id>\d+)/tasks/(?P<issue_id>\d+)/$', never_cache(issue_view), name='issue'),
]
