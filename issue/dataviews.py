import markdown2

from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.timesince import timesince

from diff_match_patch.diff_match_patch import diff_match_patch

from core.ajax.utils import jsonize
from core.templatetags.wasa2il import thumbnail

from issue.models import Comment
from issue.models import Document
from issue.models import DocumentContent
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
    if issue.is_closed():
        ctx["issue"]["votecount_abstain"] = issue.votecount_abstain
    ctx["ok"] = True
    if not request.user.is_anonymous():
        try:
            v = Vote.objects.get(user=request.user, issue=issue)
            ctx["issue"]["vote"] = v.get_value()
        except Vote.DoesNotExist:
            pass
    return ctx


@login_required
@jsonize
def document_propose_change(request):
    ctx = {"ok": True}
    version_num = int(request.POST.get('v', 0))
    document = get_object_or_404(Document, id=request.POST.get("document_id", 0))

    try:
        text = request.POST['text']
    except KeyError:
        raise Exception('Missing "text"')

    if version_num == 0:
        predecessor = document.preferred_version()
        if predecessor and predecessor.text.strip() == text.strip():
            # This error message won't show anywhere. The same error is caught client-side to produce the error message.
            raise Exception('Change proposal must differ from its predecessor')

        content = DocumentContent()
        content.user = request.user
        content.document = document
        content.predecessor = predecessor
        content.text = text
        content.comments = request.POST.get('comments', '')
        # TODO: Change this to a query that requests the maximum 'order' and adds to it.
        try:
            content.order = DocumentContent.objects.filter(document=document).order_by('-order')[0].order + 1
        except IndexError:
            pass

        content.save()

    else:
        try:
            content = DocumentContent.objects.get(
                document=document,
                user=request.user.id,
                order=version_num,
                status='proposed',
                issue=None
            )
            content.text = text
            content.comments = request.POST.get('comments', '')

            content.save()
        except DocumentContent.DoesNotExist:
            raise Exception('The user "%s" maliciously tried changing document "%s", version %d' % (
                request.user,
                document,
                version_num
            ))

    ctx['order'] = content.order

    return ctx


@login_required
@jsonize
def render_markdown(request):
    text = request.POST.get('text', 'Missing text!')
    ctx = {}
    ctx['content'] = markdown2.markdown(text, safe_mode='escape')

    return ctx


@jsonize
def documentcontent_render_diff(request):
    ctx = {}

    source_id = request.GET.get('source_id')
    target_id = request.GET.get('target_id')

    target = get_object_or_404(DocumentContent, id=target_id)

    ctx['source_id'] = source_id
    ctx['target_id'] = target_id
    ctx['diff'] = target.diff(source_id)

    return ctx
