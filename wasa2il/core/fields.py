
from django.db import models

from django.contrib.auth.models import User


class AutoUserField(models.ForeignKey):
    def __init__(self, usermodel=User, *args, **kwargs):
        d = dict(
                editable=False,
                null=True,
                blank=True,
                )
        d.update(kwargs)
        return super(AutoUserField, self).__init__(usermodel, *args, **d)
