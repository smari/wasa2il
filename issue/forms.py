from django import forms

from wasa2il.forms import Wasa2ilForm

from issue.models import Comment
from issue.models import Document
from issue.models import Issue

class IssueForm(Wasa2ilForm):
    class Meta:
        model = Issue
        exclude = (
            'polity',
            'slug',
            'documentcontent',
            'deadline_discussions',
            'deadline_proposals',
            'deadline_votes',
            'majority_percentage',
            'is_processed',
            'votecount',
            'votecount_yes',
            'votecount_abstain',
            'votecount_no'
        )


class DocumentForm(Wasa2ilForm):
    class Meta:
        model = Document
        exclude = ('is_adopted', 'is_proposed', 'user', 'polity', 'slug', 'issues')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        exclude = ('issue',)
