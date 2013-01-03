from django.forms import ModelForm
from django.forms import EmailField

from core.models import Topic, Issue, Comment, Document, Polity, Meeting, UserProfile

class TopicForm(ModelForm):
	class Meta:
		model = Topic
		exclude = ('polity', 'slug')


class IssueForm(ModelForm):
	class Meta:
		model = Issue
		exclude = ('polity', 'slug', 'options', 'deadline_proposals', 'deadline_votes')


class CommentForm(ModelForm):
	class Meta:
		model = Comment
		exclude = ('issue')


class DocumentForm(ModelForm):
	class Meta:
		model = Document
		exclude = ('is_adopted', 'is_proposed', 'user', 'polity', 'slug')

class PolityForm(ModelForm):
	class Meta:
		model = Polity
		exclude = ('slug', 'parent', 'members', 'image')


class MeetingForm(ModelForm):
	class Meta:
		model = Meeting
		exclude = ('user', 'polity', 'is_agenda_open', 'managers', 'attendees', 'time_started', 'time_ended')


class UserProfileForm(ModelForm):
	email = EmailField(help_text="The email address you'd like to use for the site.")

	class Meta:
		model = UserProfile
		fields = ('displayname', 'email', 'email_visible', 'picture', 'bio')
