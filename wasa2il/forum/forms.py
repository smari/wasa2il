
from django.forms import ModelForm

from forum.models import Forum, Discussion


class ForumForm(ModelForm):
    class Meta:
        model = Forum
        exclude = ('polity',)


class DiscussionForm(ModelForm):
    class Meta:
        model = Discussion
        exclude = ('forum', 'started_by')
