from __future__ import absolute_import

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.timesince import timesince
import json

from forum.models import Discussion, DiscussionPost
from core.templatetags.wasa2il import thumbnail


def jsonize(f):
    def wrapped(*args, **kwargs):
        m = f(*args, **kwargs)
        if isinstance(m, HttpResponse):
            return m
        return HttpResponse(json.dumps(m), content_type='application/json')

    return wrapped


def error(msg, ctx={}):
    ctx['ok'] = False
    ctx['error'] = msg
    return ctx


@login_required
@jsonize
def discussion_comment_send(request):
    discussion = get_object_or_404(Discussion, id=request.POST.get("discussion", 0))
    text = request.POST.get("comment")
    if request.user not in discussion.forum.polity.members.all():
        return discussion_poll(request)

    comment = DiscussionPost()
    comment.user = request.user
    comment.text = text
    comment.discussion = discussion
    comment.save()
    return discussion_poll(request)


@login_required
@jsonize
def discussion_poll(request):
    discussion_id = request.POST.get("discussion", request.GET.get("discussion", 0))
    discussion = get_object_or_404(Discussion, id=discussion_id)
    ctx = {}
    comments = [
        {
            "id": comment.id,
            "created_by": comment.user.username,
            "created_by_thumb": thumbnail(
                comment.user.userprofile.picture, '40x40'),
            "created": str(comment.timestamp),
            "created_since": timesince(comment.timestamp),
            "comment": comment.format()
        } for comment in discussion.discussionpost_set.all().order_by("timestamp")
    ]
    ctx["discussion"] = {"comments": comments}
    ctx["ok"] = True

    return ctx
