
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.timesince import timesince

from core.models import Issue, Vote, Comment
from core.ajax.utils import jsonize
from core.templatetags.wasa2il import thumbnail


@login_required
@jsonize
def issue_vote(request):
    issue = int(request.POST.get("issue", request.GET.get("issue", 0)))
    issue = get_object_or_404(Issue, id=issue)

    if not issue.is_voting():
        return issue_poll(request)

    if not issue.can_vote(user=request.user):
        return issue_poll(request)

    val = int(request.POST.get("vote", request.GET.get("vote", 0)))

    (vote, created) = Vote.objects.get_or_create(user=request.user, issue=issue)
    vote.value = val
    vote.save()

    return issue_poll(request)


@login_required
@jsonize
def issue_comment_send(request):
    issue = get_object_or_404(Issue, id=request.POST.get("issue", 0))
    text = request.POST.get("comment")
    comment = Comment()
    comment.created_by = request.user
    comment.comment = text
    comment.issue = issue
    comment.save()
    return issue_poll(request)


@jsonize
def issue_poll(request):
    issue = int(request.POST.get("issue", request.GET.get("issue", 0)))
    issue = get_object_or_404(Issue, id=issue)
    ctx = {}
    comments = [
        {
            "id": comment.id,
            "created_by": comment.created_by.username,
            "created_by_thumb": thumbnail(
                comment.created_by.userprofile.picture, '40x40'),
            "created": str(comment.created),
            "created_since": timesince(comment.created),
            "comment": comment.comment
        } for comment in issue.comment_set.all().order_by("created")
    ]
    documents = []
    ctx["issue"] = {"comments": comments, "documents": documents}
    ctx["ok"] = True
    ctx["issue"]["votes"] = issue.get_votes()
    if not request.user.is_anonymous():
        try:
            v = Vote.objects.get(user=request.user, issue=issue)
            ctx["issue"]["vote"] = v.get_value()
        except Vote.DoesNotExist:
            pass
    return ctx
