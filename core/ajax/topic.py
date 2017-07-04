from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.timesince import timesince
from django.utils.translation import ugettext as _

from core.models import Topic
from core.ajax.utils import jsonize
from core.templatetags.wasa2il import thumbnail


@login_required
@jsonize
def topic_poll(request):
    topic = int(request.POST.get("topic", request.GET.get("topic", 0)))
    topic = get_object_or_404(Topic, id=topic)
    ctx = {}
    comments = [
        {
            "id": comment.id,
            "created_by": comment.created_by.username,
            "created_by_thumb": thumbnail(
                comment.created_by.userprofile.picture, '40x40'),
            "created": str(comment.created),
            "created_since": timesince(comment.created),
            "comment": comment.comment,
            "in": _("in"),
            "issue_name": comment.issue.name,
            "issue_id": comment.issue.id
        } for comment in topic.new_comments()
    ]
    ctx["topic"] = {"comments": comments}
    ctx["ok"] = True
    return ctx
