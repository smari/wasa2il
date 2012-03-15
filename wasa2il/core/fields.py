
from django.db import models

from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


CHAR_FIELD_TITLE_MAX_LENGTH = 128
CHAR_FIELD_VERSION_MAX_LENGTH = 16 # e.g. 10.0.1234 beta
COORD_FIELD_MAX_LENGTH = 32

def GenerateInitField(base, kwupdate, firstarg=None):
	class GeneratorField(base):
		def __init__(self, *args, **kwargs):
			kwupdate.update(kwargs)
			if firstarg:
				return super(base, self).__init__(firstarg, *args, **kwupdate)
			return super(base, self).__init__(*args, **kwupdate)
	return GeneratorField

NameField		= GenerateInitField(models.CharField, { 'max_length': CHAR_FIELD_TITLE_MAX_LENGTH })
NameSlugField	= GenerateInitField(models.SlugField, { 'max_length': CHAR_FIELD_TITLE_MAX_LENGTH })
CreatedField	= GenerateInitField(models.DateTimeField, { 'auto_now_add': True })
ModifiedField	= GenerateInitField(models.DateTimeField, { 'auto_now': True })
#AutoUserField	= GenerateInitField(models.ForeignKey, { 'editable': False, 'null': True, 'blank': True }, firstarg=User)

class AutoUserField(models.ForeignKey):
	def __init__(self, usermodel=User, *args, **kwargs):
		d = dict(
				editable=False,
				null=True,
				blank=True,
				)
		d.update(kwargs)
		return super(AutoUserField, self).__init__(usermodel, *args, **d)
