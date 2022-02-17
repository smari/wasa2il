from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch
from django.db.models import Count
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.urls import reverse

from core.models import User
from tasks.models import Task, TaskRequest
from polity.models import Polity
from tasks.forms import TaskForm

def task_main(request, polity_id):
    polity = get_object_or_404(Polity, id=polity_id)

    # Basic attributes of tasks we're interested in.
    tasks = Task.objects.filter(is_recruiting=True, is_done=False)

    # Front polity's tasks are always shown.
    front_tasks = tasks.filter(
        polity__is_front_polity=True
    )

    # Sub-polity's tasks are only shown if they exist.
    sub_polity_tasks = tasks.filter(
        polity_id=polity_id,
        polity__is_front_polity=False
    )

    total_task_count = len(front_tasks) + len(sub_polity_tasks)

    ctx = {
        'front_tasks': front_tasks,
        'sub_polity_tasks': sub_polity_tasks,
        'total_task_count': total_task_count,
    }
    return render(request, 'tasks/task_main.html', ctx)


@login_required
def task_user_tasks(request, username):
    # Username is an optional parameter in anticipation of a future feature
    # where a user can, at least under some circumstances (having gained
    # permission, for example, or if a user chooses to make his/her
    # participation public) can view the tasks of another user. It is
    # currently not used but still required to make sure that links are
    # created with this specification in mind.

    taskrequests = TaskRequest.objects.select_related(
        'task'
    ).prefetch_related(
        'task__skills',
        'task__categories'
    ).filter(
        user_id=request.user.id
    )

    tasks = [req.task for req in taskrequests]

    ctx = {
        'tasks': tasks,
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
        'task': task,
        'form': form,
    }
    return render(request, 'tasks/task_add_edit.html', ctx)


@login_required
def task_delete(request, polity_id, task_id):
    if not request.globals['user_is_wrangler']:
        raise PermissionDenied()

    if request.method == 'POST':
        task = Task.objects.get(polity_id=polity_id, id=task_id)
        task.delete()
        return redirect(reverse('task_main', args=(polity_id,)))
    else:
        raise Http404


def task_detail(request, polity_id, task_id):
    task = get_object_or_404(Task, id=task_id, polity_id=polity_id)
    user = request.user

    # Defaults. Altered if logged in.
    has_applied = False
    phone_required = False

    if user.is_authenticated:

        polity = get_object_or_404(Polity, id=polity_id)

        has_applied = task.taskrequest_set.filter(user=user).count() > 0
        phone_required = task.require_phone and not user.userprofile.phone

        if request.method == 'POST' and not has_applied and not phone_required:
            whyme = request.POST.get('whyme')
            available_time = request.POST.get('available_time')
            if whyme.strip() != '':
                tr = TaskRequest()
                tr.task = task
                tr.user = request.user
                tr.whyme = whyme
                tr.available_time = available_time
                tr.save()
                has_applied = True

    ctx = {
        'task': task,
        'has_applied': has_applied,
        'phone_required': phone_required,
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

    tasks = polity.task_set.prefetch_related(
        # Prefetch the data for the User model that we need to determine statistics and such.
        Prefetch(
            'taskrequest_set__user',
            queryset=User.objects.annotate_task_stats()
        ),
        'taskrequest_set__user__userprofile'
    ).order_by('-created')
    if not show_done:
        tasks = tasks.filter(is_done=False)

    ctx = {
        'polity': polity,
        'tasks': tasks,
        'show_done': show_done,
    }
    return render(request, 'tasks/task_applications.html', ctx)
