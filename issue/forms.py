from django import forms
from django.forms import CharField
from wasa2il.forms import Wasa2ilForm
from prosemirror.widgets import ProseMirrorWidget

from issue.models import Comment, Document, DocumentContent, Issue

from django.utils.translation import ugettext as _

class IssueForm(Wasa2ilForm):
    class Meta:
        model = Issue
        exclude = (
            'polity',
            'slug',
            'issue_num',
            'issue_year',
            'documentcontent',
            'deadline_discussions',
            'deadline_proposals',
            'deadline_votes',
            'majority_percentage',
            'is_processed',
            'special_process_set_by',
            'votecount',
            'votecount_yes',
            'votecount_abstain',
            'votecount_no',
            'comment_count',
            'archived',
        )


class DocumentForm(Wasa2ilForm):
    class Meta:
        model = Document
        exclude = ('user', 'polity', 'slug', 'issues')


class DocumentContentForm(Wasa2ilForm):
    text = CharField(label=_('Proposal'), widget=ProseMirrorWidget, required=True)
    comments = CharField(label=_('Explanation'), widget=ProseMirrorWidget, required=False)

    class Meta:
        model = DocumentContent
        exclude = ('user', 'document', 'order', 'predecessor', 'status')

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ('issue',)
