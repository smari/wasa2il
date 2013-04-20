from django.forms import ModelForm
from django.forms import EmailField

from forum.models import Forum, Discussion, DiscussionPost

class ForumForm(ModelForm):
    class Meta:
        model = Forum
        exclude = ('polity',)


class DiscussionForm(ModelForm):
    class Meta:
        model = Discussion
        exclude = ('forum', 'started_by')

