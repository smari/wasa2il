from django.forms import ModelForm
from django.forms import EmailField
from django.utils.translation import ugettext as _

from core.models import Topic, Issue, Comment, Document, Polity, UserProfile, Election


class TopicForm(ModelForm):
    class Meta:
        model = Topic
        exclude = ('polity', 'slug')


class IssueForm(ModelForm):
    class Meta:
        model = Issue
        exclude = ('polity', 'slug', 'documentcontent', 'deadline_discussions', 'deadline_proposals', 'deadline_votes', 'majority_percentage', 'is_processed')


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        exclude = ('issue',)


class DocumentForm(ModelForm):
    class Meta:
        model = Document
        exclude = ('is_adopted', 'is_proposed', 'user', 'polity', 'slug', 'issues')


class PolityForm(ModelForm):
    class Meta:
        model = Polity
        exclude = ('slug', 'parent', 'members')


class ElectionForm(ModelForm):
    class Meta:
        model = Election
        exclude = ('polity', 'slug')


class UserProfileForm(ModelForm):
    email = EmailField(label=_("E-mail"), help_text=_("The email address you'd like to use for the site."))

    class Meta:
        model = UserProfile
        fields = ('displayname', 'email', 'picture', 'bio', 'language')
