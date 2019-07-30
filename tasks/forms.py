from wasa2il.forms import Wasa2ilForm
from django.forms import CharField
from django.utils.translation import ugettext_lazy as _
from prosemirror.widgets import ProseMirrorWidget

from tasks.models import Task

class TaskForm(Wasa2ilForm):
    description = CharField(widget=ProseMirrorWidget, label=_('Description'))
    objectives = CharField(widget=ProseMirrorWidget, label=_('Objectives'))
    requirements = CharField(widget=ProseMirrorWidget, label=_('Requirements'))

    class Meta:
        model = Task
        exclude = (
            'polity',
            'is_done',
            'created_by',
            'modified_by',
            'created',
            'modified',
            'slug',
            'categories',
            'skills',
        )


