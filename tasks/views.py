from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from tasks.models import Task
from polity.models import Polity

def task_list(request, polity_id):
    polity = get_object_or_404(Polity, id=polity_id)
    tasks = polity.task_set.order_by('-created')



    ctx = {
        'polity': polity,
        'tasks': tasks,
        'user_is_member': polity.is_member(request.user),
        'user_is_officer': polity.is_officer(request.user),
        'user_is_wrangler': polity.is_wrangler(request.user),
    }
    return render(request, 'tasks/task_list.html', ctx)
