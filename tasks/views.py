from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from core.models import User
from tasks.models import Task, TaskRequest
from polity.models import Polity
from tasks.forms import TaskForm

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


def task_user_tasks(request, username):
    user = get_object_or_404(User, username=username)
    ctx = {
        'profile': user.userprofile,
        'profile_user': user,
    }
    return render(request, 'tasks/task_user_tasks.html', ctx)


@login_required
def task_add_edit(request, polity_id, task_id=None):
    polity = get_object_or_404(Polity, id=polity_id)
    if not (polity.is_member(request.user) or polity.is_wrangler(request.user)):
        raise PermissionDenied()

    if task_id:
        task = get_object_or_404(Task, id=task_id, polity=polity)
        # We don't want to edit anything that has already done.
        if task.is_done:
            raise PermissionDenied()
    else:
        task = Task(polity=polity)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save()
            return redirect(reverse('task_detail', args=(polity_id, task.id)))
    else:
        form = TaskForm(instance=task)

    ctx = {
        'polity': polity,
        'form': form,
        'user_is_member': polity.is_member(request.user),
        'user_is_officer': polity.is_officer(request.user),
        'user_is_wrangler': polity.is_wrangler(request.user),
    }
    return render(request, 'tasks/task_add_edit.html', ctx)


def task_detail(request, polity_id, task_id):
    polity = get_object_or_404(Polity, id=polity_id)
    task = get_object_or_404(Task, id=task_id, polity=polity)
    has_applied = TaskRequest.objects.filter(task=task, user=request.user).first() or False

    if request.method == 'POST' and not has_applied:
        whyme = request.POST.get('whyme')
        if whyme.strip() != '':
            tr = TaskRequest()
            tr.task = task
            tr.user = request.user
            tr.whyme = whyme
            tr.save()
            has_applied = True

    ctx = {
        'polity': polity,
        'task': task,
        'has_applied': has_applied,
        'user_is_member': polity.is_member(request.user),
        'user_is_officer': polity.is_officer(request.user),
        'user_is_wrangler': polity.is_wrangler(request.user),
    }
    return render(request, 'tasks/task_detail.html', ctx)


def task_applications(request, polity_id):
    polity = get_object_or_404(Polity, id=polity_id)
    if not (polity.is_member(request.user) or polity.is_wrangler(request.user)):
        raise PermissionDenied()

    done = request.POST.get('done', None)
    notdone = request.POST.get('notdone', None)
    accept = request.POST.get('accept', None)
    reject = request.POST.get('reject', None)
    stoprecruiting = request.POST.get('stoprecruiting', None)
    startrecruiting = request.POST.get('startrecruiting', None)

    if done:
        tr = get_object_or_404(Task, id=done)
        tr.is_done = True
        tr.save()

    if notdone:
        tr = get_object_or_404(Task, id=notdone)
        tr.is_done = False
        tr.save()

    if stoprecruiting:
        tr = get_object_or_404(Task, id=stoprecruiting)
        tr.is_recruiting = False
        tr.save()

    if startrecruiting:
        tr = get_object_or_404(Task, id=startrecruiting)
        tr.is_recruiting = True
        tr.save()

    if accept:
        tr = get_object_or_404(TaskRequest, id=accept)
        tr.is_accepted = True
        tr.save()

    if reject:
        tr = get_object_or_404(TaskRequest, id=reject)
        tr.is_accepted = False
        tr.save()

    show_done = bool(int(request.GET.get('showdone', 0)))

    tasks = polity.task_set.order_by('-created')
    if not show_done:
        tasks = tasks.filter(is_done=False)

    ctx = {
        'polity': polity,
        'tasks': tasks,
        'user_is_member': polity.is_member(request.user),
        'user_is_officer': polity.is_officer(request.user),
        'user_is_wrangler': polity.is_wrangler(request.user),
        'show_done': show_done,
    }
    return render(request, 'tasks/task_applications.html', ctx)
