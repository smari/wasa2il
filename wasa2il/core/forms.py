from django.forms import ModelForm
from core.models import Topic, Issue, Comment

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
