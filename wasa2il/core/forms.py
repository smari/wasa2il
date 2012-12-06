from django.forms import ModelForm
from core.models import Topic, Issue, Comment, Document, Polity, Meeting

class TopicForm(ModelForm):
	class Meta:
		model = Topic
		exclude = ('polity', 'slug')


class IssueForm(ModelForm):
	class Meta:
		model = Issue
		exclude = ('slug', 'topics', 'options')


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
		exclude = ('user', 'polity', 'attendees', 'time_started', 'time_ended')
