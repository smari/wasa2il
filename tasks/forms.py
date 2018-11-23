from wasa2il.forms import Wasa2ilForm
from django.forms import CharField
from prosemirror.widgets import ProseMirrorWidget

from tasks.models import Task

class TaskForm(Wasa2ilForm):
    description = CharField(widget=ProseMirrorWidget)
    objectives = CharField(widget=ProseMirrorWidget)
    requirements = CharField(widget=ProseMirrorWidget)

    class Meta:
        model = Task
        exclude = ('polity', 'is_done', 'created_by', 'modified_by', 'created',
                   'modified', 'slug')


