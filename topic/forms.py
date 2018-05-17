from wasa2il.forms import Wasa2ilForm

from topic.models import Topic


class TopicForm(Wasa2ilForm):
    class Meta:
        model = Topic
        exclude = ('polity', 'slug')
