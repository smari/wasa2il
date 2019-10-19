from django import forms
from django.forms import CharField
from django.forms import ValidationError
from wasa2il.forms import Wasa2ilForm

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
    class Meta:
        model = DocumentContent
        exclude = ('user', 'document', 'order', 'predecessor', 'status')

    def clean_text(self):
        # Make sure that the text isn't identical to the previously active
        # version. Note that we replace \r\n for \n because we only store the
        # texts with Unix-style newlines (\n) and so replace the input text
        # here, so that the comparison is on an equal footing.
        text = self.cleaned_data['text'].replace('\r\n', '\n')
        pred = self.instance.document.preferred_version()
        if pred is not None and pred.id != self.instance.id and pred.text.strip() == text.strip():
            raise ValidationError(_('Content must differ from previous version'))

        return text

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ('issue',)
