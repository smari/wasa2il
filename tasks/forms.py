from wasa2il.forms import Wasa2ilForm

from tasks.models import Task

class TaskForm(Wasa2ilForm):
    class Meta:
        model = Task
        exclude = ('polity', 'is_done', 'created_by', 'modified_by', 'created',
                   'modified', 'slug')
