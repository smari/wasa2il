
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.timesince import timesince

from core.ajax.utils import jsonize
from core.templatetags.wasa2il import thumbnail

from issue.models import Comment
from issue.models import Issue
from issue.models import Vote

@login_required
@jsonize
def issue_vote(request):
    issue = int(request.POST.get("issue", 0))
    issue = get_object_or_404(Issue, id=issue)

    if not issue.is_voting():
        return issue_poll(request)

    if not issue.can_vote(user=request.user):
        return issue_poll(request)

    val = int(request.POST.get("vote", 0))

    (vote, created) = Vote.objects.get_or_create(user=request.user, issue=issue)
    vote.value = val
    vote.save()

    # Update vote counts
    issue.votecount = issue.votecount_yes = issue.votecount_abstain = issue.votecount_no = 0
    votes = issue.vote_set.all()
    for vote in votes:
        if vote.value == 1:
            issue.votecount += 1
            issue.votecount_yes += 1
        elif vote.value == 0:
            # We purposely skip adding one to the total vote count.
            issue.votecount_abstain += 1
        elif vote.value == -1:
            issue.votecount += 1
            issue.votecount_no += 1
    issue.save()

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
    ctx["issue"] = {"comments": comments, "votecount": issue.votecount }
    ctx["ok"] = True
    if not request.user.is_anonymous():
        try:
            v = Vote.objects.get(user=request.user, issue=issue)
            ctx["issue"]["vote"] = v.get_value()
        except Vote.DoesNotExist:
            pass
    return ctx
