
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.timesince import timesince
import simplejson as json
import settings

from forum.models import *
from forum.forms import *


def jsonize(f):
	def wrapped(*args, **kwargs):
		m = f(*args, **kwargs)
		if isinstance(m, HttpResponse):
			return m
		return HttpResponse(json.dumps(m))

	return wrapped


def error(msg, ctx={}):
	ctx['ok'] = False
	ctx['error'] = msg
	return ctx


@login_required
@jsonize
def discussion_comment_send(request):
	discussion = get_object_or_404(Discussion, id=request.REQUEST.get("discussion", 0))
	text = request.REQUEST.get("comment")
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
	discussion = get_object_or_404(Discussion, id=request.REQUEST.get("discussion", 0))
	ctx = {}
	comments = [{"id": comment.id, "created_by": comment.user.username, "created": str(comment.timestamp), "created_since": timesince(comment.timestamp), "comment": comment.format()} for comment in discussion.discussionpost_set.all().order_by("timestamp")]
	ctx["discussion"] = {"comments": comments}
	ctx["ok"] = True

	return ctx
