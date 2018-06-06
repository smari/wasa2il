import markdown2

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.timesince import timesince

from diff_match_patch.diff_match_patch import diff_match_patch

from core.ajax.utils import error
from core.ajax.utils import jsonize
from core.templatetags.wasa2il import thumbnail

from issue.models import Comment
from issue.models import Document
from issue.models import DocumentContent
from issue.models import Issue
from issue.models import Vote

from polity.models import Polity

@login_required
@jsonize
def issue_vote(request):
    issue = int(request.POST.get("issue", 0))
    issue = get_object_or_404(Issue, id=issue)

    if issue.issue_state() != 'voting':
        return issue_poll(request)

    if not issue.can_vote(user=request.user):
        return issue_poll(request)

    val = int(request.POST.get("vote", 0))

    try:
        vote = Vote.objects.get(user=request.user, issue=issue)
    except Vote.DoesNotExist:
        vote = Vote(user=request.user, issue=issue)
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
    if issue.issue_state() == 'concluded':
        ctx["issue"]["votecount_abstain"] = issue.votecount_abstain
    ctx["ok"] = True
    if not request.user.is_anonymous():
        try:
            v = Vote.objects.get(user=request.user, issue=issue)
            ctx["issue"]["vote"] = v.value
        except Vote.DoesNotExist:
            pass
    return ctx


@jsonize
def issue_showclosed(request):
    ctx = {}

    polity_id = int(request.GET.get('polity_id', 0))
    showclosed = int(request.GET.get('showclosed', 0)) # 0 = False, 1 = True

    try:
        issues = Issue.objects.select_related('polity')

        if polity_id:
            issues = issues.filter(polity_id=polity_id)
        else:
            issues = issues.order_by('polity__name', '-deadline_votes')

        if not showclosed:
            issues = issues.recent()

        if polity_id:
            polity = get_object_or_404(Polity, id=polity_id)
        else:
            polity = None

        html_ctx = {
            'user': request.user,
            'polity': polity,
            'issues_recent': issues,
        }

        ctx['showclosed'] = showclosed
        ctx['html'] = render_to_string('issue/_issues_recent_table.html', html_ctx)
        ctx['ok'] = True
    except Exception as e:
        ctx['error'] = e.__str__() if settings.DEBUG else 'Error raised. Turn on DEBUG for details.'

    return ctx


@login_required
@jsonize
def document_propose_change(request):
    ctx = {"ok": True}
    version_num = int(request.POST.get('v', 0))
    document = get_object_or_404(Document, id=request.POST.get("document_id", 0))

    try:
        name = request.POST['name']
        text = request.POST['text']
    except KeyError:
        raise Exception('Missing name or text')

    if version_num == 0:
        predecessor = document.preferred_version()
        if predecessor and predecessor.text.strip() == text.strip():
            # This error message won't show anywhere. The same error is caught client-side to produce the error message.
            raise Exception('Change proposal must differ from its predecessor')

        content = DocumentContent()
        content.user = request.user
        content.document = document
        content.predecessor = predecessor
        content.name = name
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
            content.name = name
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


@login_required
@jsonize
def documentcontent_retract(request, documentcontent_id):
    # Only polity officers and the documentcontent's author are allowed to do this.
    try:
        documentcontent = DocumentContent.objects.select_related('issue').distinct().exclude(issue=None).get(
            Q(user_id=request.user.id) | Q(document__polity__officers__id=request.user.id),
            id=documentcontent_id
        )
    except DocumentContent.DoesNotExist:
        return error('Access denied')

    # Short-hands.
    issue = documentcontent.issue
    now = timezone.now()

    # Issues that have already been processed cannot be retracted, since that
    # would give proposers and officers the power to remove accepted policy at
    # their leisure.
    if issue.is_processed or issue.issue_state() == 'concluded':
        return error('Access denied')

    # Set the issue's special process and who's responsible for it.
    issue.special_process = 'retracted'
    issue.special_process_set_by = request.user

    # Let timings make sense.
    if issue.deadline_discussions > now:
        issue.deadline_discussions = now
    if issue.deadline_proposals > now:
        issue.deadline_proposals = now
    if issue.deadline_votes > now:
        issue.deadline_votes = now

    # Set the documencontent's status.
    documentcontent.status = 'retracted'

    # Save the state.
    with transaction.atomic():
        documentcontent.save()
        issue.save()

    ctx = {
        'ok': True,
    }
    return ctx
