from django import forms

from topic.models import Topic


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        exclude = ('polity', 'slug')
